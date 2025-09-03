import torch
import os
import logging
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig, TaskType, prepare_model_for_kbit_training, get_peft_model
from hotpot_retrieval_qa.data.processor import HotpotQAProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class LFM2Trainer:
    def __init__(
        self,
        model_name: str = "LiquidAI/LFM2-1.2B",
        output_dir: str = os.path.join(
            os.getcwd(), "hotpot_retrieval_qa", "models", "lfm2-multihop-lora"
        ),
        use_lora: bool = True,
        load_in_4bit: bool = True,
    ):
        self.model_name = model_name
        self.output_dir = output_dir
        self.use_lora = use_lora
        self.load_in_4bit = load_in_4bit

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.processor = HotpotQAProcessor(model_name)

    def setup_model(self):
        model_kwargs = {
            "torch_dtype": torch.bfloat16,
            "device_map": "auto",
            "trust_remote_code": True,
        }

        if self.load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
            model_kwargs["quantization_config"] = bnb_config

        model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_kwargs)

        if self.load_in_4bit:
            model = prepare_model_for_kbit_training(model)

        return model

    def setup_lora(self):
        GLU_MODULES = ["w1", "w2", "w3"]
        MHA_MODULES = ["q_proj", "k_proj", "v_proj", "out_proj"]
        CONV_MODULES = ["in_proj", "out_proj"]

        return LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=GLU_MODULES + MHA_MODULES + CONV_MODULES,
            bias="none",
        )

    def create_training_config(self, **kwargs):
        defaults = {
            "num_train_epochs": 3,
            "per_device_train_batch_size": 1,
            "learning_rate": 5e-5,
            "lr_scheduler_type": "linear",
            "warmup_steps": 100,
            "warmup_ratio": 0.2,
            "logging_steps": 10,
            "save_strategy": "epoch",
            "eval_strategy": "epoch",
            "load_best_model_at_end": True,
            "report_to": None,
            "bf16": True,
        }
        defaults.update(kwargs)

        return SFTConfig(output_dir=self.output_dir, **defaults)

    def train(self, train_examples: int = 5000, val_examples: int = 500, **kwargs):
        logging.info("Setting up model...")
        model = self.setup_model()
        if self.use_lora:

            peft_config = self.setup_lora()
            model = get_peft_model(model, peft_config)
            model.print_trainable_parameters()

        logging.info("Preparing datasets...")
        train_dataset = self.processor.prepare_dataset("train", train_examples)
        val_dataset = self.processor.prepare_dataset("validation", val_examples)

        logging.info(f"Train: {len(train_dataset)}, Val: {len(val_dataset)}")

        training_config = self.create_training_config(**kwargs)

        trainer = SFTTrainer(
            model=model,
            args=training_config,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            processing_class=self.tokenizer,
        )

        logging.info("Starting training...")
        trainer.train()
        trainer.save_model()

        logging.info(f"Training completed! Model saved to {self.output_dir}")
        return trainer
