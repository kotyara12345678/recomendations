import pandas as pd
from pathlib import Path

OUTPUT_PATH = Path("data/issues.parquet")

def export_to_parquet(rows: list[dict]):
    df = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)

    print(f"✅ Saved parquet: {OUTPUT_PATH}")
    print(df.head())