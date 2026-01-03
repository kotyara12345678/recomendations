import csv
import json
import os
import typesense
from sentence_transformers import SentenceTransformer

TYPESENSE_HOST = "localhost"
TYPESENSE_PORT = 8108
TYPESENSE_API_KEY = "12345678"
COLLECTION = "local_data"
CSV_PATH = "data/dataset1.csv"
JSON_PATH = "data/dataset2.json"

client = typesense.Client({
    "nodes": [{
        "host": TYPESENSE_HOST,
        "port": TYPESENSE_PORT,
        "protocol": "http"
    }],
    "api_key": TYPESENSE_API_KEY,
    "connection_timeout_seconds": 2
})

model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    client.collections[COLLECTION].delete()
except:
    pass

schema = {
    "name": COLLECTION,
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "number", "type": "int32"},
        {"name": "title", "type": "string"},
        {"name": "body", "type": "string"},
        {"name": "text", "type": "string"},
        {"name": "vector", "type": "float[]", "num_dim": 384}
    ],
    "default_sorting_field": "number"
}

client.collections.create(schema)
print(" make collection")

items = []

with open(CSV_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        items.append(row)

with open(JSON_PATH, encoding="utf-8") as f:
    items.extend(json.load(f))

docs = []
texts = []

for i, item in enumerate(items):
    text = f"{item['title']}. {item['body']}"
    texts.append(text)

vectors = model.encode(texts).tolist()

for i, (item, vec) in enumerate(zip(items, vectors)):
    docs.append({
        "id": str(item["id"]),
        "number": int(item["number"]),
        "title": item["title"],
        "body": item["body"],
        "text": f"{item['title']}. {item['body']}",
        "vector": vec
    })

res = client.collections[COLLECTION].documents.import_(docs, {"action": "upsert"})
errors = [r for r in res if not r["success"]]

if errors:
    print(" error:")
    print(errors[0])
else:
    print(f"documents: {len(docs)}")

query = "Как объединить строки в Python"
q_vec = model.encode(query).tolist()
vec_str = "[" + ",".join(map(str, q_vec)) + "]"

search = {
    "searches": [{
        "collection": COLLECTION,
        "q": "*",
        "vector_query": f"vector:({vec_str}, k:5)"
    }]
}

result = client.multi_search.perform(search)

print("\n result:")
for hit in result["results"][0]["hits"]:
    print("-", hit["document"]["title"])