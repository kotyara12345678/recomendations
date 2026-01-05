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

        if not issues:
            return
        texts = [i.get('text','') for i in issues]
        vectors = self.embedder.encode(texts)
        if not vectors:
            return
        self.indexer.upsert_items(self.collection_name, issues, vectors)

    def label_single(self, issue, top=10):

        if 'text' not in issue or 'number' not in issue:
            return {"issue_number": None, "inline_refs": [], "similar": []}

        vec = self.embedder.encode([issue['text']])
        if not vec or not isinstance(vec[0], list):
            return {"issue_number": issue['number'], "inline_refs": [], "similar": []}

        vec = vec[0]
        hits = self.indexer.search(self.collection_name, vec, top=top)

        similar = [
            int(h['document'].get('number', -1))
            for h in hits
            if h['document'].get('number') != issue['number']
        ]

        inline_refs = extract_numbers(issue.get('text',''))

        return {"issue_number": issue['number'], "inline_refs": inline_refs, "similar": similar}

    def label_all(self, issues, top=10):

        result = {}
        for i in issues:
            key = i.get('number', None)
            if key is None:
                continue
            result[key] = self.label_single(i, top=top)
        return result