import re
from indexer_typesense import TypesenseIndexer
from embedder import Embedder

REF_RE = re.compile(r"#(\d+)")

def extract_numbers(text: str):

    return [int(m.group(1)) for m in REF_RE.finditer(text or "")]

class AgentLabeler:
    def __init__(self, indexer: TypesenseIndexer, collection_name: str, embedder: Embedder):
        self.indexer = indexer
        self.collection_name = collection_name
        self.embedder = embedder

    def index_issues(self, issues):
        vectors = self.embedder.encode([i['text'] for i in issues])
        self.indexer.create_collection_if_not_exists(
            self.collection_name,
            vector_dim=len(vectors[0])
        )
        self.indexer.upsert_items(self.collection_name, issues, vectors)

    def label_single(self, issue, top=10):
        vec = self.embedder.encode([issue['text']])[0]
        hits = self.indexer.search(self.collection_name, vec, top=top)
        similar = [int(h['document']['number']) for h in hits if int(h['document']['number']) != issue['number']]
        inline_refs = extract_numbers(issue['text'])

        return {"issue_number": issue['number'], "inline_refs": inline_refs, "similar": similar}

    def label_all(self, issues, top=10):
        result = {}
        for i in issues:
            result[i['number']] = self.label_single(i, top=top)
        return result