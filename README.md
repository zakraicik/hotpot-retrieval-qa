# Multi-Hop RAG System with DSPy

A question-answering system that performs multi-hop reasoning using DSPy and the HotpotQA dataset. The system can connect information across multiple documents to answer complex questions requiring sequential reasoning.

## Setup

1. Install dependencies:

```bash
poetry install
```

2. Create `.env` file:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

## Quick Start

### Step 0: Download and Prepare Data

**Required for local setup** - This system runs entirely locally and needs the HotpotQA dataset:

1. Download HotpotQA dataset:

```bash
python hotpot_retrieval_qa/data/loader.py
```

2. Build the vector index:

```bash
python hotpot_retrieval_qa/data/build_index.py
```

This creates the required files:

- `faiss.index` - Vector search index
- `documents.pkl` - Document text
- `embeddings.npy` - Document embeddings

**Note**: Default uses 1000 examples for prototyping. Edit `max_examples` in `build_index.py` for better coverage.

### Step 1: Run Multi-Hop QA

```python
from hotpot_retrieval_qa.retrieval import Retrieval
from hotpot_retrieval_qa.multihop import QA

# Initialize system
retriever = Retrieval()
qa = QA(retriever)

# Ask complex questions
result = qa("What nationality is the director of Lagaan?")

print(f"Answer: {result.answer}")
print(f"Reasoning: {result.reasoning_steps}")
print(f"Confidence: {result.confidence}")
```

### Step 2: Test with Examples

Run the complete example:

```bash
python hotpot_retrieval_qa/example.py
```

## How It Works

The system performs multi-hop reasoning in three steps:

1. **Question Analysis**: Breaks down complex questions into search queries
2. **Iterative Retrieval**: Performs multiple retrieval "hops" to gather evidence
3. **Chain-of-Thought**: Synthesizes information to generate the final answer

Example multi-hop question: _"What nationality is the director of Lagaan?"_

- **Hop 1**: Search for "Lagaan director" → finds "Ashutosh Gowariker"
- **Hop 2**: Search for "Ashutosh Gowariker nationality" → finds "Indian"
- **Synthesis**: Combines facts to answer "Indian"

## Key Components

### `hotpot_retrieval_qa/data/`

- `loader.py` - Downloads HotpotQA dataset
- `build_index.py` - Creates vector search index

### `hotpot_retrieval_qa/`

- `retrieval.py` - Vector similarity search
- `dspy_setup.py` - DSPy configuration with Claude
- `multihop.py` - Multi-hop reasoning module
- `example.py` - Demo script

## Configuration

### Model Selection

Edit `dspy_setup.py` to change the language model:

```python
lm = dspy.LM(
    model="anthropic/claude-3-5-sonnet-20240620",
    api_key=api_key,
    max_tokens=500
)
```

### Index Size

Edit `build_index.py` to change dataset size:

```python
build_vector_index(max_examples=5000)  # More examples = better coverage
```

## Example Output

```
Test 1: What nationality is the director of Lagaan?
============================================================
Queries used: ['What nationality is the director of Lagaan?', 'Ashutosh Gowariker nationality']
Number of hops: 2
Reasoning: 1. Lagaan was directed by Ashutosh Gowariker
2. Ashutosh Gowariker is described as an "Indian film director"
Answer: Indian
Confidence: high
```

## Troubleshooting

**"Index files not found"**: Run `build_index.py` first

**Low confidence answers**: Increase `max_examples` in `build_index.py` for better document coverage

**API errors**: Check your `ANTHROPIC_API_KEY` environment variable
