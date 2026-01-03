import os
import typesense
from typing import List, Dict

class TypesenseIndexer:

    def __init__(self, host=None, port=8108, api_key=None):
        host = host or os.getenv("TYPESENSE_HOST", "localhost")
        api_key = api_key or os.getenv("TYPESENSE_API_KEY", "typesense_key_here")
        self.client = typesense.Client({
            'nodes': [{
                'host': host.replace('http://','').replace('https://',''),
                'port': port,
                'protocol': 'http'
            }],
            'api_key': api_key,
            'connection_timeout_seconds': 2
        })

    def create_collection_if_not_exists(self, collection_name="default", vector_dim=384):
        try:
            self.client.collections[collection_name].retrieve()
        except Exception:
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

    def upsert_items(self, collection_name: str, items: List[dict], vectors: List):
        documents = []
        for it, vec in zip(items, vectors):
            documents.append({
                'id': str(it['id']),
                'number': it['number'],
                'type': it['type'],
                'title': it['title'][:2000] if it.get('title') else '',
                'body': it.get('body','')[:16000],
                'text': it.get('text','')[:16000],
                'vector': vec
            })

        chunk = 50
        for i in range(0, len(documents), chunk):
            batch = documents[i:i+chunk]
            self.client.collections[collection_name].documents.import_(batch, {'action':'upsert'})

    def search(self, collection_name: str, query_vector, top=10):
        vector_str = "[" + ",".join(map(str, query_vector)) + "]"

        res = self.client.multi_search.perform({
            "searches": [
                {
                    "collection": collection_name,
                    "q": "",
                    "vector_query": f"vector:({vector_str}),k:{top}"
                }
            ]
        })

        hits = []
        for hit in res["results"][0].get("hits", []):
            hits.append({
                "score": hit.get("vector_distance"),
                "document": hit["document"]
            })

        return hits