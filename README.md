# Multi-Hop RAG System with DSPy

A question-answering system that performs multi-hop reasoning using DSPy and the HotpotQA dataset. The system can connect information across multiple documents to answer complex questions requiring sequential reasoning.

## Features

- **Multi-hop reasoning**: Connects information across multiple documents with iterative retrieval
- **Query rewriting**: Intelligently reformulates questions into better search queries
- **Chunk ranking**: Reorders retrieved documents by relevance to improve context quality
- **Scientific evaluation**: Comprehensive metrics and experiment tracking
- **Experiment management**: JSON-based tracking of all evaluation runs

## Setup

1. Create `.env` file:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

2. Install dependencies:

```bash
poetry install
```

## Quick Start

### Step 0: Download and Prepare Data

**Required for local setup** - This system runs entirely locally and needs the HotpotQA dataset:

1. Download HotpotQA dataset:

```bash
# Download training data (default)
poetry run python hotpot_retrieval_qa/data/loader.py

# Or specify split and cache location
poetry run python hotpot_retrieval_qa/data/loader.py --split validation --cache-dir /custom/path
```

2. Build the vector index:

```bash
# Build with all available data (recommended)
poetry run python hotpot_retrieval_qa/data/build_index.py

# Or limit examples for faster testing
poetry run python hotpot_retrieval_qa/data/build_index.py --max-examples 5000 --cache-dir /custom/path
```

This creates the required files:

- `faiss.index` - Vector search index
- `documents.pkl` - Document text
- `embeddings.npy` - Document embeddings

**Note**: Using all training data provides better coverage than a limited sample

### Step 1: Interactive Usage

Start Python and interact with the system directly:

```bash
poetry run python
```

```python
>>> from hotpot_retrieval_qa.retrieval import Retrieval
>>> from hotpot_retrieval_qa.multihop import QA
>>> retriever = Retrieval()
>>> qa = QA(retriever)

>>> result = qa("What nationality is the director of Lagaan?")
```

## How It Works

The system performs multi-hop reasoning with enhanced retrieval:

1. **Query Rewriting**: Transforms complex questions into multiple focused search queries
2. **Iterative Retrieval**: Performs multiple retrieval "hops" to gather evidence
3. **Chunk Ranking**: Reorders retrieved documents by relevance to the original question
4. **Chain-of-Thought**: Synthesizes information to generate the final answer

Example multi-hop question: _"What nationality is the director of Lagaan?"_

- **Query Rewriting**: Generates focused queries like "Lagaan director" and "director nationality"
- **Hop 1**: Search for "Lagaan director" → finds "Ashutosh Gowariker"
- **Hop 2**: Search for "Ashutosh Gowariker nationality" → finds "Indian"
- **Ranking**: Reorders chunks by relevance to original question
- **Synthesis**: Combines facts to answer "Indian"

## Example Questions

The system excels at multi-hop questions requiring sequential reasoning:

- **"What nationality is the director of Lagaan?"** - Requires finding the director first, then their nationality
- **"What is the capital of the country where Mount Everest is located?"** - Needs to identify the country, then find its capital
- **"What movie came out first? Titanic or Interstellar?"** - Requires looking up release dates for comparison

## Key Components

### `hotpot_retrieval_qa/data/`

- `loader.py` - Downloads HotpotQA dataset
- `build_index.py` - Creates vector search index

### `hotpot_retrieval_qa/`

- `retrieval.py` - Vector similarity search
- `dspy_setup.py` - DSPy configuration with Claude (1500 tokens)
- `multihop.py` - Multi-hop reasoning with query rewriting and chunk ranking
- `evaluation.py` - Main evaluation orchestration and experiment tracking
- `experiment_tracker.py` - Experiment management and JSON storage
- `utils/evaluation.py` - Core metrics (EM, F1) and analysis utilities

## License

MIT
