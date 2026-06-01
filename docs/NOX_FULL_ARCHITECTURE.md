# NOX Full Platform Architecture

NOX is structured as an elite fitness agent platform with four product domains:

- Great Lock In: focus-mode scheduling, recommendations, recurring training commitments.
- Workout Tracker: set-level logging, progressive overload, session summaries, PR tracking.
- Training Splits & Knowledge Vault: Dorian HIT, Mentzer Heavy Duty, Arnold Classic, PPL, Upper/Lower, Bro Split, plus RAG coaching knowledge.
- Nutrition Engine: macro setup, food logging, diet charts, protein deficit alerts, meal suggestions.

## Runtime Services

- Rust Axum core API: high-throughput ingestion for workout sets, nutrition logs, and lock-ins.
- Go workers: Kafka consumers, notification dispatch, schedule sync, biometric rollups.
- FastAPI + LangGraph orchestrator: NOX agent routing, tool calls, RAG, LLM streaming.
- vLLM: self-hosted OpenAI-compatible LLM serving.
- vLLM embeddings tier: self-hosted BGE embedding generation for vector memory.

## Data Layer

- Cassandra: distributed write store partitioned by `user_id + week_bucket`.
- Redis + RedisJSON: active session state, lock-in state, current macro totals.
- PostgreSQL + pgvector: foods, exercises, split templates, coach articles and embeddings.
- Weaviate: vector search collections for workout memory, food memory, and coach knowledge.
- InfluxDB: biometrics and training trend time-series.
- Kafka: event stream between ingestion APIs, workers, analytics, and agent memory.

## Local Startup

```bash
cd "/Users/vivektripathi/Trial-Ai agent"
docker compose -f infra/docker-compose.yml up --build
./infra/bootstrap.sh
```

The `vllm` service is behind the `gpu` profile because it requires a suitable model and hardware:

```bash
docker compose -f infra/docker-compose.yml --profile gpu up vllm embeddings
```

## Kubernetes

```bash
kubectl apply -f infra/kubernetes/nox-namespace.yaml
kubectl apply -f infra/kubernetes/
```

The Kubernetes manifests define the app services. Managed or operator-backed deployments should be used for Cassandra, Kafka, Redis, Postgres, Weaviate, InfluxDB and vLLM in production.
