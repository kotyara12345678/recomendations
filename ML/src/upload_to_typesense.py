from tqdm import tqdm
from pathlib import Path
import yaml

from utils.io_utils import read_jsonl
from utils.typesense_client import get_client


def main():
    cfg = yaml.safe_load(Path("configs/typesense_config.yaml").read_text())
    client = get_client()

    for rec in tqdm(read_jsonl("data/embeddings.jsonl"), desc="Uploading"):
        client.collections[cfg["collection_name"]].documents.upsert(rec)

    print("Upload complete")


if __name__ == "__main__":
    main()