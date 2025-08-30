import re
import string
import logging
from collections import Counter
from hotpot_retrieval_qa.data.loader import load_hotpotqa_dataset
from hotpot_retrieval_qa.experiment_tracker import ExperimentTracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def normalize_answer(text):
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(text))))


def exact_match_score(prediction, ground_truth):
    return int(normalize_answer(prediction) == normalize_answer(ground_truth))


def f1_score(prediction, ground_truth):
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(ground_truth).split()

    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0

    common_tokens = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common_tokens.values())

    if num_common == 0:
        return 0.0

    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    return f1


def calculate_metrics(predictions, ground_truths):
    if len(predictions) != len(ground_truths):
        raise ValueError("Predictions and ground truths must have same length")

    em_scores = []
    f1_scores = []

    for pred, gold in zip(predictions, ground_truths):
        em_scores.append(exact_match_score(pred, gold))
        f1_scores.append(f1_score(pred, gold))

    metrics = {
        "exact_match": sum(em_scores) / len(em_scores) if em_scores else 0.0,
        "f1": sum(f1_scores) / len(f1_scores) if f1_scores else 0.0,
        "total_examples": len(predictions),
    }

    return metrics


def prepare_test_examples(split="validation", max_examples=None):

    dataset = load_hotpotqa_dataset(split=split)

    if max_examples:
        dataset = dataset.select(range(min(max_examples, len(dataset))))

    test_examples = []
    for example in dataset:
        test_example = {
            "id": example["id"],
            "question": example["question"],
            "answer": example["answer"],
            "type": example["type"],
            "level": example["level"],
            "supporting_facts": example["supporting_facts"],
        }
        test_examples.append(test_example)

    logging.info(f"Prepared {len(test_examples)} test examples from {split} split")
    return test_examples


def _analyze_by_category(detailed_results: list[dict]) -> dict[str, any]:

    by_type = {}
    by_level = {}

    for result in detailed_results:
        qtype = result.get("type", "unknown")
        level = result.get("level", "unknown")

        if qtype not in by_type:
            by_type[qtype] = {"em_scores": [], "f1_scores": [], "count": 0}
        by_type[qtype]["em_scores"].append(result["exact_match"])
        by_type[qtype]["f1_scores"].append(result["f1"])
        by_type[qtype]["count"] += 1

        if level not in by_level:
            by_level[level] = {"em_scores": [], "f1_scores": [], "count": 0}
        by_level[level]["em_scores"].append(result["exact_match"])
        by_level[level]["f1_scores"].append(result["f1"])
        by_level[level]["count"] += 1

    def calc_category_metrics(category_data):
        return {
            "exact_match": (
                sum(category_data["em_scores"]) / len(category_data["em_scores"])
                if category_data["em_scores"]
                else 0
            ),
            "f1": (
                sum(category_data["f1_scores"]) / len(category_data["f1_scores"])
                if category_data["f1_scores"]
                else 0
            ),
            "count": category_data["count"],
        }

    analysis = {
        "by_type": {k: calc_category_metrics(v) for k, v in by_type.items()},
        "by_level": {k: calc_category_metrics(v) for k, v in by_level.items()},
    }

    return analysis


def _analyze_failures(
    detailed_results: list[dict], threshold: float = 0.3
) -> list[dict]:
    failures = [r for r in detailed_results if r["f1"] < threshold]
    return sorted(failures, key=lambda x: x["f1"])[:10]


def _print_results(metrics, category_analysis, experiment_name):

    print(f"\n{'='*60}")
    print(f"🔥 EXPERIMENT: {experiment_name}")
    print("=" * 60)

    print(f"📊 Overall Performance:")
    print(f"   • Exact Match: {metrics['exact_match']:.3f}")
    print(f"   • F1 Score: {metrics['f1']:.3f}")
    print(f"   • Total Examples: {metrics['total_examples']}")
    print(f"   • Speed: {metrics['questions_per_second']:.1f} q/sec")

    if category_analysis.get("by_type"):
        print(f"\n📈 By Question Type:")
        for qtype, type_metrics in category_analysis["by_type"].items():
            print(
                f"   • {qtype}: EM={type_metrics['exact_match']:.3f}, F1={type_metrics['f1']:.3f} (n={type_metrics['count']})"
            )

    if category_analysis.get("by_level"):
        print(f"\n🎯 By Difficulty:")
        for level, level_metrics in category_analysis["by_level"].items():
            print(
                f"   • {level}: EM={level_metrics['exact_match']:.3f}, F1={level_metrics['f1']:.3f} (n={level_metrics['count']})"
            )

    print("=" * 60 + "\n")


def compare_experiments(experiment_names_or_ids: list[str]):

    tracker = ExperimentTracker()
    comparison = tracker.compare_experiments(experiment_names_or_ids)

    if not comparison["experiments"]:
        logging.error("No valid experiments found for comparison")
        return

    print(f"\n{'='*60}")
    print("📊 EXPERIMENT COMPARISON")
    print("=" * 60)

    for metric in ["exact_match", "f1"]:
        if metric in comparison["metrics_comparison"]:
            print(f"\n{metric.replace('_', ' ').title()}:")
            for item in comparison["metrics_comparison"][metric]:
                value = item["value"]
                if value is not None:
                    print(f"   • {item['experiment']}: {value:.3f}")

    print("=" * 60 + "\n")

    return comparison


def list_experiments():

    tracker = ExperimentTracker()
    experiments = tracker.list_experiments()

    if not experiments:
        print("No experiments found.")
        return

    print(f"\n📁 Found {len(experiments)} experiments:")
    for exp in experiments:
        metrics = exp["metrics"]
        em = metrics.get("exact_match", "N/A")
        f1 = metrics.get("f1", "N/A")
        created = exp["created_at"][:10]

        em_str = f"{em:.3f}" if isinstance(em, float) else str(em)
        f1_str = f"{f1:.3f}" if isinstance(f1, float) else str(f1)

        print(f"   • {exp['name']} ({created}): EM={em_str}, F1={f1_str}")

    print()
