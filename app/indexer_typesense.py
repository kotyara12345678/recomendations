import os
import typesense
from typing import List, Dict
import json

class TypesenseIndexer:
    def __init__(self, host=None, port=8108, api_key=None):
        host = host or os.getenv("TYPESENSE_HOST", "localhost")
        api_key = api_key or os.getenv("TYPESENSE_API_KEY", "12345678")
        self.client = typesense.Client({
            'nodes': [{
                'host': host.replace('http://','').replace('https://',''),
                'port': port,
                'protocol': 'http'
            }],
            'api_key': api_key,
            'connection_timeout_seconds': 2
        })

    def collection_exists(self, collection_name: str) -> bool:
        try:
            self.client.collections[collection_name].retrieve()
            return True
        except typesense.exceptions.ObjectNotFound:
            return False
        except Exception:
            return False

    def create_collection_if_not_exists(self, collection_name="default", vector_dim=384):
        if self.collection_exists(collection_name):
            print(f"Коллекция '{collection_name}' уже существует")
            return

        schema = {
            'name': collection_name,
            'fields': [
                {'name':'id','type':'string'},
                {'name':'number','type':'int32'},
                {'name':'type','type':'string'},
                {'name':'title','type':'string'},
                {'name':'body','type':'string'},
                {'name':'text','type':'string'},
                {'name':'vector','type':'float[]','num_dim': vector_dim}
            ],
            'default_sorting_field':'number'
        }
        self.client.collections.create(schema)
        print(f"Коллекция '{collection_name}' создана")

    def upsert_items(self, collection_name: str, items: List[dict], vectors: List[List[float]]):
        documents = []
        for it, vec in zip(items, vectors):
            documents.append({
                'id': str(it['id']),
                'number': it['number'],
                'type': it.get('type','task'),
                'title': it.get('title','')[:2000],
                'body': it.get('body','')[:16000],
                'text': it.get('text','')[:16000],
                'vector': vec
            })

        chunk = 50
        for i in range(0, len(documents), chunk):
            batch = documents[i:i+chunk]
            res = self.client.collections[collection_name].documents.import_(batch, {'action':'upsert'})
            # res уже список словарей, split не нужен
            for status in res:
                if isinstance(status, str):
                    status = json.loads(status)
                if status.get("success") is False:
                    print("Ошибка при вставке документа:", status)

        print(f"Документы загружены: {len(documents)}")

    def search(self, collection_name: str, query_vector, top=10):
        vector_str = "[" + ",".join(map(str, query_vector)) + "]"

        body = {
            "searches": [
                {
                    "collection": collection_name,
                    "q": "*",
                    "vector_query": f"vector:({vector_str}, k:{top})"
                }
            ]
        }

        res = self.client.multi_search.perform(body)

        hits = []
        results = res.get("results", [])
        if results:
            for hit in results[0].get("hits", []):
                doc = hit.get("document", {})
                score = hit.get("vector_score") or hit.get("vector_distance") or 0.0
                hits.append({"score": score, "document": doc})

        return hits