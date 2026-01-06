import yaml
import typesense
from pathlib import Path


def load_config(path="configs/typesense_config.yaml"):
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_client():
    cfg = load_config()
    return typesense.Client({
        "nodes": [{
            "host": cfg["host"],
            "port": cfg["port"],
            "protocol": cfg["protocol"],
        }],
        "api_key": cfg["api_key"],
        "connection_timeout_seconds": 5,
    })