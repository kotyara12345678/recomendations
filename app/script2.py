import os
import json
import csv
import typesense
from sentence_transformers import SentenceTransformer

# Настройки Typesense
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "localhost")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "12345678")
COLLECTION_NAME = "local_data"
VECTOR_DIM = 384  # размерность эмбеддингов модели

# Подключение к Typesense
client = typesense.Client({
    'nodes': [{'host': TYPESENSE_HOST, 'port': 8108, 'protocol': 'http'}],
    'api_key': TYPESENSE_API_KEY,
    'connection_timeout_seconds': 2
})

# Проверяем коллекцию
def create_collection_if_not_exists():
    try:
        client.collections[COLLECTION_NAME].retrieve()
        print(f"Коллекция '{COLLECTION_NAME}' уже существует")
    except typesense.exceptions.ObjectNotFound:
        schema = {
            "name": COLLECTION_NAME,
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "body", "type": "string"},
                {"name": "text", "type": "string"},
                {"name": "vector", "type": "float[]", "num_dim": VECTOR_DIM}
            ],
            "default_sorting_field": "id"
        }
        client.collections.create(schema)
        print(f"Коллекция '{COLLECTION_NAME}' создана")

# Загружаем CSV
def load_csv(filename):
    items = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items

# Загружаем JSON
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Генерируем эмбеддинги
model = SentenceTransformer("all-MiniLM-L6-v2")
def embed_texts(items):
    texts = [f"{it.get('title','')}. {it.get('body','')}" for it in items]
    vectors = model.encode(texts).tolist()
    for it, vec in zip(items, vectors):
        it["text"] = f"{it.get('title','')}. {it.get('body','')}"
        it["vector"] = vec
    return items

# Загружаем данные в Typesense
def index_items(items):
    chunk = 50
    for i in range(0, len(items), chunk):
        batch = []
        for it in items[i:i+chunk]:
            batch.append({
                "id": str(it["id"]),
                "title": it.get("title",""),
                "body": it.get("body",""),
                "text": it.get("text",""),
                "vector": it.get("vector")
            })
        res = client.collections[COLLECTION_NAME].documents.import_(batch, {"action": "upsert"})
        # вывод ошибок
        for r in res:
            if isinstance(r, str):
                r = json.loads(r)
            if r.get("success") is False:
                print("Ошибка при вставке:", r)
    print(f"Документы загружены: {len(items)}")

# Поиск
def search(query, top=5):
    q_vec = model.encode([query])[0].tolist()
    vector_str = "[" + ",".join(map(str, q_vec)) + "]"
    body = {
        "searches": [
            {
                "collection": COLLECTION_NAME,
                "q": "*",
                "vector_query": f"vector:({vector_str}, k:{top})"
            }
        ]
    }
    res = client.multi_search.perform(body)
    hits = []
    results = res.get("results", [])
    if results:
        for hit in results[0].get("hits", []):
            doc = hit.get("document", {})
            score = hit.get("vector_score") or hit.get("vector_distance") or 0.0
            hits.append({"score": score, "document": doc})
    return hits

# ==== Основной блок ====
if __name__ == "__main__":
    create_collection_if_not_exists()
    csv_items = load_csv("data/dataset1.csv")   # путь к CSV
    json_items = load_json("data/dataset2.json") # путь к JSON
    all_items = csv_items + json_items
    all_items = embed_texts(all_items)
    index_items(all_items)

    while True:
        q = input("Введите текст для поиска: ")
        if q.lower() in ("exit", "quit"):
            break
        results = search(q, top=5)
        for r in results:
            print(r["score"], r["document"]["title"])
        print("нету ")