import pandas as pd
import json
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from glob import glob

DATA_DIR = Path("./jsonl_data")
DATA_DIR.mkdir(exist_ok=True)


def load_jsonl_files(pattern: str) -> pd.DataFrame:
    files = glob(str(DATA_DIR / pattern))
    if not files:
        print(f"Файлы не найдены по шаблону {pattern}")
        return pd.DataFrame()

    df_list = [pd.read_json(f, lines=True) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    print(f"Загружено {len(df)} записей из {len(files)} файлов")
    return df


class JSONLDataset(Dataset):
    def __init__(self, jsonl_pattern: str):
        self.files = glob(str(DATA_DIR / jsonl_pattern))
        self.data = []
        for f in self.files:
            with open(f, "r", encoding="utf-8") as file:
                self.data.extend([json.loads(line) for line in file])
        print(f"PyTorch Dataset создан с {len(self.data)} элементами")

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)

def main():
    # Пример: загружаем issues
    df_issues = load_jsonl_files("issues_*.jsonl")

    dataset = JSONLDataset("issues_*.jsonl")
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    return df_issues, loader


if __name__ == "__main__":
    df, loader = main()