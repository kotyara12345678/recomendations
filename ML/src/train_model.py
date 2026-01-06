import yaml
from pathlib import Path
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, InputExample, losses

from utils.io_utils import read_jsonl


def main():
    cfg = yaml.safe_load(Path("configs/training_config.yaml").read_text())

    model = SentenceTransformer(cfg["model_name"])

    examples = [
        InputExample(texts=obj["texts"], label=float(obj["label"]))
        for obj in read_jsonl("data/pairs.jsonl")
    ]

    dataloader = DataLoader(
        examples,
        shuffle=True,
        batch_size=cfg["batch_size"],
        num_workers=cfg["num_workers"],
    )

    loss = losses.MultipleNegativesRankingLoss(model)
    warmup = int(cfg["warmup_ratio"] * len(dataloader))

    model.fit(
        train_objectives=[(dataloader, loss)],
        epochs=cfg["epochs"],
        warmup_steps=warmup,
        output_path=cfg["output_path"],
    )

    print("Model saved to", cfg["output_path"])


if __name__ == "__main__":
    main()