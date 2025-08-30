import argparse
import faiss
import os
import numpy as np
import pickle
import logging
from hotpot_retrieval_qa.data.loader import load_hotpotqa_dataset
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def build_vector_index(
    max_examples=None,
    cache_dir=os.path.join(os.getcwd(), "hotpot_retrieval_qa", "data", "cached"),
):
    dataset = load_hotpotqa_dataset("train", cache_dir=cache_dir)

    if max_examples:
        dataset = dataset.select(range(min(max_examples, len(dataset))))

    logging.info(f"Using {len(dataset)} records from dataset")

    documents = []
    for example in dataset:
        titles = example["context"]["title"]
        sentences = example["context"]["sentences"]

        for title, sentence_list in zip(titles, sentences):
            documents.extend(sentence_list)

    logging.info(f"Extracted {len(documents)} documents from dataset")

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedder.encode(documents, show_progress_bar=True)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    index.add(embeddings.astype("float32"))

    np.save(f"{cache_dir}/embeddings.npy", embeddings)
    with open(f"{cache_dir}/documents.pkl", "wb") as f:
        pickle.dump(documents, f)
    faiss.write_index(index, f"{cache_dir}/faiss.index")

    logging.info(f"Vector index built and saved to {cache_dir}")
    return documents, embeddings, index


def main():
    parser = argparse.ArgumentParser(
        description="Build vector index for HotpotQA dataset"
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=None,
        help="Maximum number of examples to use from dataset (default: use all)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=os.path.join(os.getcwd(), "hotpot_retrieval_qa", "data", "cached"),
        help="Directory to save index files (default: ./hotpot_retrieval_qa/data/cached)",
    )

    args = parser.parse_args()

    build_vector_index(max_examples=args.max_examples, cache_dir=args.cache_dir)

    logging.info("Index building completed successfully!")


if __name__ == "__main__":
    main()
