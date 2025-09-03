from datasets import Dataset
import logging
from transformers import AutoTokenizer
from hotpot_retrieval_qa.data.loader import load_hotpotqa_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Loading HotpotQA dataset")


class HotpotQAProcessor:

    def __init__(self, tokenizer_name: str = "LiquidAI/LFM2-1.2B"):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def extract_supporting_facts(self, example: dict) -> list[str]:
        facts = []

        titles = example["context"]["title"]
        sentences = example["context"]["sentences"]

        fact_titles = example["supporting_facts"]["title"]
        fact_sent_ids = example["supporting_facts"]["sent_id"]

        for fact_title, sent_id in zip(fact_titles, fact_sent_ids):
            try:
                title_idx = titles.index(fact_title)
                if sent_id < len(sentences[title_idx]):
                    facts.append(sentences[title_idx][sent_id].strip())
            except (ValueError, IndexError):
                continue

        return facts

    def prepare_dataset(
        self, split: str = "train", max_examples: int = None
    ) -> Dataset:

        raw_dataset = load_hotpotqa_dataset(split=split)
        logging.info(f"Loaded {len(raw_dataset)} examples from {split} split")
        if max_examples:
            raw_dataset = raw_dataset.select(range(min(max_examples, len(raw_dataset))))
            logging.info(f"Selected {len(raw_dataset)} examples from {split} split")

        conversations = []
        logging.info(f"Preparing dataset with {len(raw_dataset)} examples")
        for example in raw_dataset:
            facts = self.extract_supporting_facts(example)
            if not facts:
                continue

            conversation = [
                {
                    "role": "system",
                    "content": "You are an expert at multi-hop reasoning. Break down complex questions and provide structured answers.",
                },
                {
                    "role": "user",
                    "content": f"Question: {example['question']}\n\nProvide a step-by-step analysis and answer.",
                },
                {
                    "role": "assistant",
                    "content": f"Based on the evidence: {' | '.join(facts[:3])}\n\nAnswer: {example['answer']}",
                },
            ]

            text = self.tokenizer.apply_chat_template(conversation, tokenize=False)
            conversations.append(text)

        logging.info(f"Prepared {len(conversations)} conversations")

        return Dataset.from_dict({"text": conversations})
