from collector import collect_local_data
from embedder import Embedder
from indexer_typesense import TypesenseIndexer
from agent_labeler import AgentLabeler
import os

COLLECTION_NAME = os.getenv("TYPESENSE_COLLECTION", "issues")

def run_pipeline(top=10):
    print("[pipeline] Загружаю локальные данные...")
    issues = collect_local_data()
    print(f"[pipeline] Всего issues: {len(issues)}")

    embedder = Embedder()
    indexer = TypesenseIndexer()
    labeler = AgentLabeler(indexer, COLLECTION_NAME, embedder)

    print("[pipeline] Индексирую issues в Typesense...")
    labeler.index_issues(issues)

    print("[pipeline] Получаю рекомендации для всех issues...")
    results = labeler.label_all(issues, top=top)
    print("[pipeline] Готово")
    return results


if __name__ == "__main__":
    res = run_pipeline()
    for k, v in list(res.items())[:5]:
        print(k, v)