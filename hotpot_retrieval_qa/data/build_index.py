from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import faiss
import os
import numpy as np
import pickle
from hotpot_retrieval_qa.data.loader import load_hotpotqa_dataset
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def build_vector_index(
    max_examples=1000,
    cache_dir=os.path.join(os.getcwd(), "hotpot_retrieval_qa", "data", "cached"),
):
    dataset = load_hotpotqa_dataset("train")
    dataset = dataset.select(range(min(max_examples, len(dataset))))

    logging.info(f"Sampled {len(dataset)} records from dataset")

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

    return documents, embeddings, index


if __name__ == "__main__":
    build_vector_index()
