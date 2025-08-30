import time
import uuid
import logging

from datetime import datetime
from typing import Optional
from hotpot_retrieval_qa.experiment_tracker import ExperimentTracker
from hotpot_retrieval_qa.utils.evaluation import (
    exact_match_score,
    f1_score,
    _analyze_by_category,
    _analyze_failures,
    _print_results,
    prepare_test_examples,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class HotpotEvaluator:
    def __init__(self):
        self.results = []

    def evaluate_single(self, prediction, ground_truth, question_id=None):
        em = exact_match_score(prediction, ground_truth)
        f1 = f1_score(prediction, ground_truth)

        result = {
            "id": question_id,
            "prediction": prediction,
            "ground_truth": ground_truth,
            "exact_match": em,
            "f1": f1,
        }

        self.results.append(result)
        return result

    def evaluate_batch(self, predictions_list, ground_truths_list, question_ids=None):
        if question_ids is None:
            question_ids = [None] * len(predictions_list)

        for pred, gold, qid in zip(predictions_list, ground_truths_list, question_ids):
            self.evaluate_single(pred, gold, qid)

    def get_metrics(self):
        if not self.results:
            return {"exact_match": 0.0, "f1": 0.0, "total_examples": 0}

        em_scores = [r["exact_match"] for r in self.results]
        f1_scores = [r["f1"] for r in self.results]

        return {
            "exact_match": sum(em_scores) / len(em_scores),
            "f1": sum(f1_scores) / len(f1_scores),
            "total_examples": len(self.results),
        }

    def get_detailed_results(self):
        return self.results

    def analyze_failures(self, threshold=0.5):
        failures = []
        for result in self.results:
            if result["f1"] < threshold:
                failures.append(result)

        logging.info(f"Found {len(failures)} failures (F1 < {threshold})")
        return failures

    def reset(self):
        self.results = []


def evaluate_and_save(
    qa_system,
    experiment_name: str,
    experiment_description: str = "",
    split: str = "validation",
    max_examples: int = 100,
    system_config: Optional[dict[str, any]] = None,
) -> str:

    experiment_id = f"{experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

    logging.info(f"🔬 Starting experiment: {experiment_name}")
    test_examples = prepare_test_examples(split=split, max_examples=max_examples)

    evaluator = HotpotEvaluator()

    logging.info(f"Running evaluation on {len(test_examples)} examples...")
    start_time = time.time()

    detailed_results = []
    for i, example in enumerate(test_examples):
        try:

            result = qa_system(example["question"])
            prediction = result.answer

            evaluation_result = evaluator.evaluate_single(
                prediction, example["answer"], example["id"]
            )

            detailed_result = {
                **evaluation_result,
                "question": example["question"],
                "type": example.get("type"),
                "level": example.get("level"),
                "system_info": {
                    "queries_used": getattr(result, "queries_used", []),
                    "num_hops": getattr(result, "num_hops", 0),
                    "confidence": getattr(result, "confidence", None),
                    "reasoning_steps": getattr(result, "reasoning_steps", ""),
                },
            }

            detailed_results.append(detailed_result)

            if (i + 1) % 10 == 0:
                logging.info(f"Processed {i + 1}/{len(test_examples)} examples...")

        except Exception as e:
            logging.error(f"Error processing example {i}: {e}")

            detailed_result = {
                "id": example["id"],
                "question": example["question"],
                "prediction": "",
                "ground_truth": example["answer"],
                "exact_match": 0,
                "f1": 0,
                "type": example.get("type"),
                "level": example.get("level"),
                "error": str(e),
            }

            detailed_results.append(detailed_result)
            evaluator.evaluate_single("", example["answer"], example["id"])

    elapsed_time = time.time() - start_time

    metrics = evaluator.get_metrics()
    metrics["elapsed_time_seconds"] = elapsed_time
    metrics["questions_per_second"] = len(test_examples) / elapsed_time

    category_analysis = _analyze_by_category(detailed_results)

    experiment_data = {
        "id": experiment_id,
        "name": experiment_name,
        "description": experiment_description,
        "created_at": datetime.now().isoformat(),
        "config": {
            "split": split,
            "max_examples": max_examples,
            "system_config": system_config or {},
        },
        "results": {
            "metrics": metrics,
            "category_analysis": category_analysis,
            "detailed_results": detailed_results,
            "failure_analysis": _analyze_failures(detailed_results),
        },
    }

    tracker = ExperimentTracker()
    tracker.save_experiment(experiment_data)

    _print_results(metrics, category_analysis, experiment_name)

    return experiment_id
