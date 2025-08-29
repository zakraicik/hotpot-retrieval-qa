import dspy
from hotpot_retrieval_qa.dspy_setup import setup_dspy

setup_dspy()


class MultiHopReasoning(dspy.Signature):
    """Perform multi-hop reasoning to answer complex questions."""

    question = dspy.InputField(
        desc="Complex question requiring multiple reasoning steps"
    )
    context = dspy.InputField(desc="Retrieved documents and information")
    reasoning_steps = dspy.OutputField(desc="Step-by-step reasoning process")
    answer = dspy.OutputField(desc="Final answer based on reasoning")
    confidence = dspy.OutputField(desc="Confidence level: high, medium, or low")


class QA(dspy.Module):
    def __init__(self, retriever, max_hops=3):
        super().__init__()
        self.retriever = retriever
        self.max_hops = max_hops

        self.reason = dspy.ChainOfThought(MultiHopReasoning)

        class FollowUpQuery(dspy.Signature):
            question = dspy.InputField()
            current_info = dspy.InputField()
            next_query = dspy.OutputField(
                desc="Next search query needed, or 'DONE' if sufficient"
            )

        self.follow_up = dspy.Predict(FollowUpQuery)

    def forward(self, question):
        all_context = []
        queries_used = []

        initial_query = question

        for hop in range(self.max_hops):
            docs = self.retriever.retrieve(initial_query, k=5)
            context_text = "\n".join([doc["document"] for doc in docs[:3]])
            all_context.append(context_text)
            queries_used.append(initial_query)

            combined_context = "\n---\n".join(all_context)
            follow_up_result = self.follow_up(
                question=question, current_info=combined_context
            )

            if follow_up_result.next_query == "DONE" or hop == self.max_hops - 1:
                break

            initial_query = follow_up_result.next_query

        final_context = "\n---\n".join(all_context)
        result = self.reason(question=question, context=final_context)

        return dspy.Prediction(
            question=question,
            queries_used=queries_used,
            reasoning_steps=result.reasoning_steps,
            answer=result.answer,
            confidence=result.confidence,
            num_hops=len(queries_used),
        )
