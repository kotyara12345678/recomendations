import typesense
import time
from typing import List

class TypesenseIndexer:
    def __init__(self, host="http://localhost:8108", api_key="typesense_key_here", port=8108):
        self.client = typesense.Client({
            'nodes': [{
                'host': host.replace('http://','').replace('https://',''),
                'port': port,
                'protocol': 'http'
            }],
            'api_key': api_key,
            'connection_timeout_seconds': 2
        })

    def create_collection_if_not_exists(self, collection_name="default"):
        try:
            self.client.collections[collection_name].retrieve()
        except Exception:
            schema = {
                'name': collection_name,
                'fields': [
                    {'name':'id','type':'int64'},
                    {'name':'number','type':'int32'},
                    {'name':'type','type':'string'},
                    {'name':'title','type':'string'},
                    {'name':'body','type':'string'},
                    {'name':'labels','type':'string[]'},
                    {'name':'html_url','type':'string'},
                    {'name':'vector','type':'float[]', 'num_dim': 384}
                ],
                'default_sorting_field':'number'
            }
            self.client.collections.create(schema)

    def upsert_items(self, collection_name: str, items: List[dict], vectors: List):
        documents = []
        for it, vec in zip(items, vectors):
            doc = {
                'id': it['id'],
                'number': it['number'],
                'type': it['type'],
                'title': it['title'][:2000] if it.get('title') else '',
                'body': it.get('body','')[:16000],
                'labels': it.get('labels',[]),
                'html_url': it.get('html_url',''),
                'vector': vec.tolist() if hasattr(vec, 'tolist') else list(vec)
            }
            documents.append(doc)
        chunk = 50
        for i in range(0, len(documents), chunk):
            batch = documents[i:i+chunk]
            self.client.collections[collection_name].documents.import_(batch, {'action':'upsert'})

    def search(self, collection_name: str, query_vector, top=10):
        query_by = "title,body"
        vector_str = "[" + ",".join([str(float(x)) for x in query_vector]) + "]"
        search_parameters = {
            'q': '*',
            'query_by': query_by,
            'vector_query': f"vector:({vector_str}),k:{top}"
        }
        res = self.client.collections[collection_name].documents.search(search_parameters)
        hits = []
        for hit in res.get('hits', []):
            doc = hit.get('document', {})
            score = hit.get('vector_score') or hit.get('score') or 0.0
            hits.append({'score': score, 'document': doc})
        return hits