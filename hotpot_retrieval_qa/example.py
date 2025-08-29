from hotpot_retrieval_qa.retrieval import Retrieval
from hotpot_retrieval_qa.multihop import QA


def example():

    retriever = Retrieval()
    qa = QA(retriever)

    questions = [
        "What nationality is the director of Lagaan?",
        "Which film was released first, Lagaan or 3 Idiots?",
        "What do the directors of Lagaan and 3 Idiots have in common?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question}")
        print("=" * 60)

        try:
            result = qa(question=question)

            print(f"Queries used: {result.queries_used}")
            print(f"Number of hops: {result.num_hops}")
            print(f"Reasoning: {result.reasoning_steps}")
            print(f"Answer: {result.answer}")
            print(f"Confidence: {result.confidence}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    example()
