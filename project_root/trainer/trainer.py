import os
from embedder.embedder import Embedder
from dataset import DatasetLoader
import json

DATA_DIR = os.getenv("DATA_DIR", "./data")
SAVE_DIR = os.getenv("SAVE_DIR", "./models/LeFine_recommendation")

os.makedirs(SAVE_DIR, exist_ok=True)

def main():
    loader = DatasetLoader(DATA_DIR)
    records = loader.load_all()
    texts = loader.prepare_texts(records)

    if not texts:
        print("Нет текстов для обработки. Заканчиваем.")
        return

    embed_model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    embedder = Embedder(embed_model_name)

    print(f"Генерируем эмбеддинги для {len(texts)} текстов...")
    embeddings = embedder.encode(texts)

    save_path = os.path.join(SAVE_DIR, "embeddings.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump({"texts": texts, "embeddings": embeddings}, f)

    print(f"Эмбеддинги сохранены в {save_path}")

if __name__ == "__main__":
    main()