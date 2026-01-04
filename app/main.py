import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from collector import collect_local_data
from embedder import Embedder
from indexer_typesense import TypesenseIndexer
from agent_labeler import AgentLabeler

app = FastAPI(title="Local Task Recommender")

TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "typesense")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "12345678")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("TYPESENSE_COLLECTION", "local_data")

embedder = Embedder(model_name=EMBED_MODEL)
indexer = TypesenseIndexer(host=TYPESENSE_HOST, api_key=TYPESENSE_API_KEY)
agent = AgentLabeler(indexer=indexer, collection_name=COLLECTION_NAME, embedder=embedder)

# Модель запроса
class QueryRequest(BaseModel):
    text: str
    top: int = 10
    collection: str = COLLECTION_NAME


def prepare_items_for_agent(items: List[Dict]) -> List[Dict]:
    for idx, item in enumerate(items, start=1):
        item["number"] = idx
        item["text"] = f"{item.get('title','')}. {item.get('body','')}"
        item["type"] = "task"
    return items


@app.post("/collect_and_index")
def collect_and_index():
    try:
        items = collect_local_data()
        if not items:
            raise HTTPException(status_code=404, detail="Нет данных для индексации")

        items = prepare_items_for_agent(items)

        if not indexer.collection_exists(COLLECTION_NAME):
            indexer.create_collection_if_not_exists(collection_name=COLLECTION_NAME)

        agent.index_issues(items)
        return {"status": "ok", "count": len(items)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query(req: QueryRequest):
    try:
        if not indexer.collection_exists(req.collection):
            raise HTTPException(status_code=404, detail=f"Коллекция {req.collection} не найдена")

        vec = embedder.encode([req.text])
        if isinstance(vec, list) and len(vec) == 1:
            vec = vec[0]  # получаем вектор из списка

        hits = indexer.search(collection_name=req.collection, query_vector=vec, top=req.top)

        clean_hits = []
        for h in hits:
            doc = h["document"]
            clean_doc = {
                "number": doc.get("number"),
                "title": doc.get("title"),
                "body": doc.get("body")
            }
            clean_hits.append({"score": h["score"], "document": clean_doc})

        return {"query": req.text, "results": clean_hits}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/label")
def label(top: int = 20):
    try:
        items = collect_local_data()
        if not items:
            raise HTTPException(status_code=404, detail="Нет данных для разметки")

        items = prepare_items_for_agent(items)
        result = agent.label_all(items, top=top)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) #.