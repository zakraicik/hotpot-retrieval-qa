import logging
import os
from pathlib import Path
from datasets import load_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_hotpotqa_dataset(
    split="train",
    cache_dir=os.path.join(os.getcwd(), "hotpot_retrieval_qa", "data", "cached"),
):

    logging.info(f"Loading HotpotQA {split} split...")

    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(
        "hotpotqa/hotpot_qa",
        name="distractor",
        split=split,
        cache_dir=cache_dir,
    )

    logging.info(f"Loaded {len(dataset)} examples from {split} split")
    return dataset
