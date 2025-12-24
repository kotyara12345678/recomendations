from pathlib import Path
import pandas as pd
import json


def load_parquet(path: Path):
    df = pd.read_parquet(path)
    return normalize_df(df)


def load_csv(path: Path):
    df = pd.read_csv(path)
    return normalize_df(df)


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("items", [])

    df = pd.DataFrame(data)
    return normalize_df(df)


def normalize_df(df: pd.DataFrame):

    required = {"title", "body"}
    if not required.issubset(df.columns):
        raise ValueError(f"Ожидались поля {required}, получены {df.columns}")

    df = df.fillna("")

    records = []
    for i, row in df.iterrows():
        records.append({
            "id": str(i),
            "title": str(row["title"]),
            "body": str(row["body"]),
        })

    return records


def collect_local_data(data_dir="data"):
    data_dir = Path(data_dir)
    all_records = []

    loaders = {
        ".parquet": load_parquet,
        ".csv": load_csv,
        ".json": load_json,
    }

    for file in data_dir.iterdir():
        if file.suffix in loaders:
            print(f" Загружаю {file.name}")
            all_records.extend(loaders[file.suffix](file))

    return all_records