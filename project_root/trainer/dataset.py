from pathlib import Path
from typing import List, Dict
import pandas as pd

class DatasetLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Папка {self.data_dir} не найдена: {self.data_dir}")

    def load_parquet(self) -> List[Dict]:
        files = list(self.data_dir.glob("*.parquet"))
        if not files:
            print(f"Нет parquet файлов в {self.data_dir}")
            return []
        records = []
        for f in files:
            df = pd.read_parquet(f)
            records.extend(df.to_dict(orient="records"))
        return records

    def load_csv(self) -> List[Dict]:
        files = list(self.data_dir.glob("*.csv"))
        if not files:
            print(f"Нет CSV файлов в {self.data_dir}")
            return []
        records = []
        for f in files:
            df = pd.read_csv(f)
            records.extend(df.to_dict(orient="records"))
        return records

    def load_all(self) -> List[Dict]:
        records = self.load_parquet() + self.load_csv()
        print(f"Загружено всего записей: {len(records)}")
        return records

    def prepare_texts(self, records: List[Dict], text_fields: List[str] = ["title", "body"]) -> List[str]:
        texts = []
        for r in records:
            parts = [str(r.get(f, "")) for f in text_fields if r.get(f)]
            if parts:
                texts.append(". ".join(parts))
        return texts