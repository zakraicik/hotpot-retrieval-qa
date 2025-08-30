# Multi-Hop RAG System with DSPy

A question-answering system that performs multi-hop reasoning using DSPy and the HotpotQA dataset. The system can connect information across multiple documents to answer complex questions requiring sequential reasoning.

## Features

- **Multi-hop reasoning**: Connects information across multiple documents
- **Scientific evaluation**: Comprehensive metrics and experiment tracking
- **Performance analysis**: Breakdown by question type and difficulty
- **Experiment management**: JSON-based tracking of all evaluation runs

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
# Download training data (default)
python hotpot_retrieval_qa/data/loader.py

# Or specify split and cache location
python hotpot_retrieval_qa/data/loader.py --split validation --cache-dir /custom/path
```

2. Build the vector index:

```bash
# Build with all available data (recommended)
python hotpot_retrieval_qa/data/build_index.py

# Or limit examples for faster testing
python hotpot_retrieval_qa/data/build_index.py --max-examples 5000 --cache-dir /custom/path
```

This creates the required files:

- `faiss.index` - Vector search index
- `documents.pkl` - Document text
- `embeddings.npy` - Document embeddings

**Note**: Using all training data provides better coverage than a limited sample

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

### Step 2: Evaluate Performance

```python
from hotpot_retrieval_qa.evaluation import evaluate_and_save

# Run systematic evaluation
experiment_id = evaluate_and_save(
    qa_system=qa,
    experiment_name="baseline",
    experiment_description="Initial system performance",
    max_examples=50
)
```

### Step 3: Compare Results

```python
from hotpot_retrieval_qa.utils.evaluation import compare_experiments, list_experiments

# See all experiments
list_experiments()

# Compare specific experiments
compare_experiments(['baseline', 'improved_version'])
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
- `evaluation.py` - Main evaluation orchestration and experiment tracking
- `experiment_tracker.py` - Experiment management and JSON storage
- `utils/evaluation.py` - Core metrics (EM, F1) and analysis utilities

### Evaluation System

The evaluation system provides:

- **Standard Metrics**: Exact Match (EM) and F1 scores following HotpotQA conventions
- **Category Analysis**: Performance breakdown by question type (bridge/comparison) and difficulty
- **Failure Analysis**: Identification of low-performing examples
- **Experiment Tracking**: JSON files storing complete evaluation results
- **Comparison Tools**: Side-by-side performance analysis across experiments

Each evaluation creates a timestamped JSON file in `hotpot_retrieval_qa/experiments/` containing:

- Overall metrics (EM, F1, speed)
- Detailed per-question results
- System configuration
- Category-wise performance breakdown

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

### Index Size and Data

Control how much training data to use:

```bash
# Use all available training data (best performance)
python hotpot_retrieval_qa/data/build_index.py

# Limit for faster prototyping
python hotpot_retrieval_qa/data/build_index.py --max-examples 5000
```

## Example Output

```
🔥 EXPERIMENT: baseline
============================================================
📊 Overall Performance:
   • Exact Match: 0.340
   • F1 Score: 0.485
   • Total Examples: 100
   • Speed: 0.8 q/sec

📈 By Question Type:
   • bridge: EM=0.380, F1=0.520 (n=60)
   • comparison: EM=0.275, F1=0.425 (n=40)

🎯 By Difficulty:
   • easy: EM=0.450, F1=0.580 (n=30)
   • medium: EM=0.320, F1=0.460 (n=45)
   • hard: EM=0.240, F1=0.410 (n=25)
============================================================
```

## Evaluation Workflow

1. **Baseline**: `evaluate_and_save(qa_system, "baseline")`
2. **Enhance**: Implement improvements (hybrid retrieval, better prompts, etc.)
3. **Re-evaluate**: `evaluate_and_save(improved_system, "enhancement_v1")`
4. **Compare**: `compare_experiments(['baseline', 'enhancement_v1'])`
5. **Iterate**: Use metrics to guide further improvements

## License

MIT
