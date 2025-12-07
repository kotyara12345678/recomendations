import os
import json
import pandas as pd
from typing import List, Dict

DATA_DIR = "data"

def load_csv(path: str) -> List[Dict]:

    df = pd.read_csv(path)
    records = []
    for i, row in df.iterrows():
        title = str(row.get("title", "")).strip()
        body = str(row.get("body", "")).strip()
        if not title and not body:
            continue
        records.append({
            "id": f"csv-{os.path.basename(path)}-{i}",
            "number": i + 1,
            "type": "issue",
            "title": title,
            "body": body,
            "text": f"{title}\n\n{body}"
        })
    return records

def load_json(path: str) -> List[Dict]:

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = []
    for i, item in enumerate(data):
        title = str(item.get("title", "")).strip()
        body = str(item.get("body", "")).strip()
        if not title and not body:
            continue
        records.append({
            "id": f"json-{os.path.basename(path)}-{i}",
            "number": i + 1,
            "type": "issue",
            "title": title,
            "body": body,
            "text": f"{title}\n\n{body}"
        })
    return records

def collect_local_data() -> List[Dict]:

    all_items = []
    if not os.path.exists(DATA_DIR):
        print(f"[collector] Папка {DATA_DIR} не найдена")
        return all_items

    for filename in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, filename)
        if filename.endswith(".csv"):
            all_items.extend(load_csv(path))
        elif filename.endswith(".json"):
            all_items.extend(load_json(path))
        else:
            print(f"[collector] Пропускаю неподдерживаемый файл: {filename}")

    for i, item in enumerate(all_items):
        item["number"] = i + 1

    print(f"[collector] Загружено записей: {len(all_items)}")
    return all_items