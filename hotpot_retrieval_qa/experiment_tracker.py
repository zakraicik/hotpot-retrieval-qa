import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ExperimentTracker:

    def __init__(self, experiments_dir: str = "hotpot_retrieval_qa/experiments"):
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(exist_ok=True, parents=True)

    def save_experiment(self, experiment_data: dict[str, any]) -> str:

        experiment_id = experiment_data["id"]
        experiment_file = self.experiments_dir / f"{experiment_id}.json"

        with open(experiment_file, "w") as f:
            json.dump(experiment_data, f, indent=2)

        logging.info(f"💾 Saved experiment: {experiment_id}")
        return experiment_id

    def list_experiments(self) -> list[dict[str, any]]:

        experiments = []
        for exp_file in self.experiments_dir.glob("*.json"):
            with open(exp_file, "r") as f:
                experiment_data = json.load(f)

            experiments.append(
                {
                    "id": experiment_data["id"],
                    "name": experiment_data["name"],
                    "description": experiment_data["description"],
                    "created_at": experiment_data["created_at"],
                    "metrics": experiment_data.get("results", {}).get("metrics", {}),
                }
            )

        experiments.sort(key=lambda x: x["created_at"], reverse=True)
        return experiments

    def get_experiment(self, experiment_id: str) -> dict[str, any]:

        experiment_file = self.experiments_dir / f"{experiment_id}.json"

        if not experiment_file.exists():
            raise ValueError(f"Experiment {experiment_id} not found")

        with open(experiment_file, "r") as f:
            return json.load(f)

    def compare_experiments(self, experiment_names_or_ids: list[str]) -> dict[str, any]:

        comparison = {"experiments": [], "metrics_comparison": {}}

        all_experiments = self.list_experiments()

        for name_or_id in experiment_names_or_ids:
            matching_exp = None
            for exp in all_experiments:
                if exp["id"] == name_or_id or exp["name"] == name_or_id:
                    matching_exp = exp
                    break

            if matching_exp:
                comparison["experiments"].append(matching_exp)
            else:
                logging.warning(f"No experiment found matching: {name_or_id}")

        if comparison["experiments"]:
            metrics_keys = set()
            for exp in comparison["experiments"]:
                metrics_keys.update(exp["metrics"].keys())

            for metric in metrics_keys:
                comparison["metrics_comparison"][metric] = []
                for exp in comparison["experiments"]:
                    value = exp["metrics"].get(metric)
                    comparison["metrics_comparison"][metric].append(
                        {"experiment": exp["name"], "value": value}
                    )

        return comparison
