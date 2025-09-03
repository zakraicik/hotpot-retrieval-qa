import logging
from hotpot_retrieval_qa.training.trainer import LFM2Trainer

logging.basicConfig(level=logging.INFO)


def main():
    trainer = LFM2Trainer(
        output_dir="./data/models/finetuned/lfm2-multihop-lora",
        use_lora=True,
        load_in_4bit=True,
    )

    trainer.train(
        train_examples=1000,
        val_examples=100,
        num_train_epochs=1,
        per_device_train_batch_size=1,
        learning_rate=2e-4,
    )


if __name__ == "__main__":
    main()
