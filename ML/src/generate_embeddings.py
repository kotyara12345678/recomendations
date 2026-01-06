import yaml
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from utils.io_utils import read_jsonl, write_jsonl
from utils.text_utils import build_text


def main():
    ds_cfg = yaml.safe_load(Path("configs/dataset_config.yaml").read_text())
    tr_cfg = yaml.safe_load(Path("configs/training_config.yaml").read_text())

    model = SentenceTransformer(tr_cfg["output_path"])

    records = []

    for obj in tqdm(read_jsonl(ds_cfg["raw_issues_path"]), desc="Encoding"):
        text = build_text(obj.get("title"), obj.get("body"), obj.get("text"))
        emb = model.encode(text).tolist()
        records.append({"id": obj["id"], "embedding": emb})

    write_jsonl("data/embeddings.jsonl", records)
    print("Saved embeddings")


if __name__ == "__main__":
    main()