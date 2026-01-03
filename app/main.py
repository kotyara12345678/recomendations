import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collector import collect_local_data
from embedder import Embedder
from indexer_typesense import TypesenseIndexer
from agent_labeler import AgentLabeler

app = FastAPI(title="Local Task Recommender")

# Переменные окружения
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "typesense")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "12345678")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-mpnet-base-v2")
COLLECTION_NAME = os.getenv("TYPESENSE_COLLECTION", "local_data")

# Инициализация компонентов
embedder = Embedder(model_name=EMBED_MODEL)
indexer = TypesenseIndexer(host=TYPESENSE_HOST, api_key=TYPESENSE_API_KEY)
agent = AgentLabeler(indexer=indexer, collection_name=COLLECTION_NAME, embedder=embedder)

class QueryRequest(BaseModel):
    text: str
    top: int = 10
    collection: str = COLLECTION_NAME

def prepare_items_for_agent(items):
    for idx, item in enumerate(items, start=1):
        item["number"] = idx
        item["text"] = f"{item['title']}. {item['body']}"
        item["type"] = "task"
    return items

@app.post("/collect_and_index")
def collect_and_index():
    try:
        items = collect_local_data()
        if not items:
            raise HTTPException(status_code=404, detail="Нет данных для индексации")
        items = prepare_items_for_agent(items)
        agent.index_issues(items)
        return {"status": "ok", "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query(req: QueryRequest):
    try:
        vec = embedder.encode([req.text])[0]
        hits = indexer.search(collection_name=req.collection, query_vector=vec, top=req.top)
        return {"query": req.text, "results": hits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/label")
def label(top: int = 20):
    try:
        items = collect_local_data()
        items = prepare_items_for_agent(items)
        result = agent.label_all(items, top=top)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))