import argparse
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


def main():
    parser = argparse.ArgumentParser(description="Load HotpotQA dataset")
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="Dataset split to load (default: train)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=os.path.join(os.getcwd(), "hotpot_retrieval_qa", "data", "cached"),
        help="Directory to cache dataset files (default: ./hotpot_retrieval_qa/data/cached)",
    )

    args = parser.parse_args()

    dataset = load_hotpotqa_dataset(split=args.split, cache_dir=args.cache_dir)

    logging.info(f"Successfully loaded {len(dataset)} examples from {args.split} split")
    logging.info(f"Sample example keys: {list(dataset[0].keys())}")


if __name__ == "__main__":
    main()
