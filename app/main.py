import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from collector import collect_local_data  # <- заменили collect_repo
from embedder import Embedder
from indexer_typesense import TypesenseIndexer
from agent_labeler import AgentLabeler

app = FastAPI(title="Local Task Recommender")

TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "http://localhost:8108")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "typesense_key_here")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

embedder = Embedder(model_name=EMBED_MODEL)
indexer = TypesenseIndexer(host=TYPESENSE_HOST, api_key=TYPESENSE_API_KEY)
agent = AgentLabeler(openrouter_key=os.getenv("OPENROUTER_KEY"))

class QueryRequest(BaseModel):
    text: str
    top: int = 10
    collection: str = "local_data"  # <- по умолчанию наша коллекция

@app.post("/collect_and_index")
def collect_and_index():

    try:
        items = collect_local_data()
        if not items:
            raise HTTPException(status_code=404, detail="Нет данных для индексации")
        texts = [it['text'] for it in items]
        vectors = embedder.encode(texts)
        collection_name = "local_data"
        indexer.create_collection_if_not_exists(collection_name=collection_name)
        indexer.upsert_items(collection_name=collection_name, items=items, vectors=vectors)
        return {"status":"ok", "count": len(items)}
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

    items = collect_local_data()
    collection_name = "local_data"
    return agent.label_candidates_for_repo(collection_name, top=top)