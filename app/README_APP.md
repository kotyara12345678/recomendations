# App module instructions

## Endpoints

1. /collect_and_index?repo=owner/repo
   - Сбор Issues + PR из GitHub
   - Вычисление эмбеддингов
   - Загрузка в Typesense collection owner_repo

2. /query
   - POST JSON: 
    
     { "text": "Describe issue", "top": 10 }
     
   - Возвращает ближайших соседей (Issues/PR) по семантической схожести

3. /label?repo=owner/repo&top=20
   - Возвращает candidate-пары PR→Issues:
     - heuristic — на основе текста PR (closes/fixes #X)
     - candidates — на основе similarity embeddings + Typesense

## Примечания
- Если нет OPENROUTER_KEY, агент использует только heuristics.
- Для production: рекомендуется добавить очередь задач (Celery/RQ) и расширить обработку diff/timeline.