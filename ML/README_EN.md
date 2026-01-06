# ML Recommendation Pipeline — Documentation

This project implements a full ML pipeline for training a recommendation model based on issue data and performing semantic search using Typesense.

---

## 🚀 Start the system

docker-compose up -d
---

## 🧩 Full ML Pipeline

### 1. Prepare dataset (create pairs.jsonl)

docker exec -it trainer uv run prepare-dataset
Output: ML/data/pairs.jsonl

---

### 2. Train the model

docker exec -it trainer uv run train-model
Output: ML/models/fine_tuned/

---

### 3. Generate embeddings

docker exec -it trainer uv run generate-embeddings
Output: ML/data/embeddings.jsonl

---

### 4. Upload embeddings to Typesense

docker exec -it trainer uv run upload-to-typesense
---

## 🔁 Full cycle in one command

docker exec -it trainer uv run prepare-dataset && \
docker exec -it trainer uv run train-model && \
docker exec -it trainer uv run generate-embeddings && \
docker exec -it trainer uv run upload-to-typesense
---

## 🛠 Useful commands

### Check containers:
docker ps -a
### Restart everything:
docker-compose down
docker-compose up -d
### Logs:
docker logs trainer
docker logs recommendation-app
---

## 📌 Data locations

- ML/data/issues.jsonl — raw dataset  
- ML/data/pairs.jsonl — training pairs  
- ML/data/embeddings.jsonl — embeddings  
- ML/models/fine_tuned/ — trained model  

---

## ⚙️ Dataset requirements

Format of issues.jsonl:

{"id": 1, "title": "...", "body": "...", "text": "..."}
---

## 🧠 Training recommendations

- epochs: 1–2  
- batch_size: 16  
- max_length: 256  
- dataset size: 100k — ideal  

---

## 🧱 Typesense

The collection is created automatically during embedding upload.

---

## 📞 Support

If something breaks — check logs or restart trainer.