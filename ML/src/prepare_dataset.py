import json
from pathlib import Path
from tqdm import tqdm

from utils.io_utils import read_jsonl, write_jsonl
from utils.text_utils import build_text


def main():
    cfg_path = Path("configs/dataset_config.yaml")
    cfg = json.loads(cfg_path.read_text()) if cfg_path.suffix == ".json" else __import__("yaml").safe_load(cfg_path.read_text())

    input_path = Path(cfg["raw_issues_path"])
    output_path = Path(cfg["pairs_output_path"])

    pairs = []

    for obj in tqdm(read_jsonl(input_path), desc="Building pairs"):
        title = obj.get("title", "")
        body = obj.get("body", "")
        text = obj.get("text", "")

        anchor = build_text(title, body)
        positive = build_text(body, text)

        if len(anchor) < cfg["min_text_length"]:
            continue

        pairs.append({
            "texts": [anchor, positive],
            "label": 1.0
        })

        if len(pairs) >= cfg["max_pairs"]:
            break

    write_jsonl(output_path, pairs)
    print(f"Saved {len(pairs)} pairs")


if __name__ == "__main__":
    main()