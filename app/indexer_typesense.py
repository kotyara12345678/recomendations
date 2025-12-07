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
        # батчинг
        chunk = 50
        for i in range(0, len(documents), chunk):
            batch = documents[i:i+chunk]
            self.client.collections[collection_name].documents.import_(batch, {'action':'upsert'})

    def search(self, collection_name: str, query_vector, top=10):
        vector_str = "[" + ",".join([str(float(x)) for x in query_vector]) + "]"
        search_parameters = {
            'q': '*',
            'query_by': 'text',
            'vector_query': f'vector:({vector_str}),k:{top}'
        }
        res = self.client.collections[collection_name].documents.search(search_parameters)
        hits = []
        for hit in res.get('hits', []):
            doc = hit.get('document', {})
            score = hit.get('vector_score') or hit.get('score') or 0.0
            hits.append({'score': score, 'document': doc})
        return hits