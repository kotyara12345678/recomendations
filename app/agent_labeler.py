import os, json, re
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_KEY = os.getenv('OPENROUTER_KEY')

CLOSE_RE = re.compile(r"\b(?:close[sd]?|fix(?:es)?|resolve[sd]?)\s+(?:#(\d+)|https?://\S+/issues/(\d+))", re.I)
REF_RE = re.compile(r"#(\d+)")

def extract_issue_numbers_from_text(text: str):
    nums = set()
    if not text:
        return []
    for m in CLOSE_RE.finditer(text):
        g1 = m.group(1) or m.group(2)
        if g1:
            nums.add(int(g1))
    for m in REF_RE.finditer(text):
        nums.add(int(m.group(1)))
    return sorted(nums)

class AgentLabeler:
    def init(self, openrouter_key: str = None):
        self.openrouter_key = openrouter_key or OPENROUTER_KEY

    def label_candidates_for_repo(self, repo: str, top: int = 20):
        from collector import collect_repo
        from embedder import Embedder
        from indexer_typesense import TypesenseIndexer

        items = collect_repo(repo)
        issues = {it['number']: it for it in items if it['type']=='issue'}
        prs = [it for it in items if it['type']=='pr']

        # heuristics
        mapping = {}
        for pr in prs:
            nums = extract_issue_numbers_from_text(pr.get('body','') or '') + extract_issue_numbers_from_text(pr.get('title','') or '')
            nums = sorted(set(n for n in nums if n in issues))
            mapping[pr['number']] = nums

        embedder = Embedder()
        vectors = embedder.encode([p['text'] for p in prs])
        ts = TypesenseIndexer(host=os.getenv('TYPESENSE_HOST','http://localhost:8108'),
                              api_key=os.getenv('TYPESENSE_API_KEY','typesense_key_here'))
        ts.create_collection_if_not_exists(collection_name=repo.replace('/','_'))
        candidates = {}
        for pr, vec in zip(prs, vectors):
            hits = ts.search(collection_name=repo.replace('/','_'), query_vector=vec, top=top)
            hits_nums = [h['document'].get('number') for h in hits if h['document'].get('type')=='issue']
            candidates[pr['number']] = hits_nums

        combined = {}
        for pr in prs:
            combined[pr['number']] = {
                'heuristic': mapping.get(pr['number'], []),
                'candidates': candidates.get(pr['number'], [])
            }
        return combined