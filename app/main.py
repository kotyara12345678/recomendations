import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from collector import collect_repo
from embedder import Embedder
from indexer_typesense import TypesenseIndexer
from agent_labeler import AgentLabeler

app = FastAPI(title="GH Task Recommender")

TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "http://localhost:8108")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY", "typesense_key_here")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

embedder = Embedder(model_name=EMBED_MODEL)
indexer = TypesenseIndexer(host=TYPESENSE_HOST, api_key=TYPESENSE_API_KEY)
agent = AgentLabeler(openrouter_key=os.getenv("OPENROUTER_KEY"))

class QueryRequest(BaseModel):
    text: str
    top: int = 10

@app.post("/collect_and_index")
def collect_and_index(repo: str = Query(..., description="owner/repo")):
    owner_repo = repo.strip()
    try:
        items = collect_repo(owner_repo)
        texts = [it['text'] for it in items]
        vectors = embedder.encode(texts)
        indexer.create_collection_if_not_exists(collection_name=owner_repo.replace('/','_'))
        indexer.upsert_items(collection_name=owner_repo.replace('/','_'), items=items, vectors=vectors)
        return {"status":"ok", "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query(req: QueryRequest):
    vec = embedder.encode([req.text])[0]
    hits = indexer.search(collection_name=req.dict.get('collection', 'default'), query_vector=vec, top=req.top)
    return {"query": req.text, "results": hits}

@app.post("/label")
def label(repo: str = Query(...), top:int = 20):
    return agent.label_candidates_for_repo(repo, top=top)