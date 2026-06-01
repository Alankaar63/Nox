from __future__ import annotations


def architecture_status() -> dict:
    """Declarative target architecture for the full NOX platform."""
    return {
        "product": "NOX Elite Fitness AI Agent",
        "domains": [
            "Great Lock In",
            "Workout Tracker",
            "Training Splits & Knowledge Vault",
            "Nutrition Engine",
        ],
        "data_layer": {
            "cassandra": "Primary distributed workout, nutrition, schedule, and profile store",
            "redis_json": "Hot cache for active sessions, macro totals, lock-in state",
            "postgres_pgvector": "Food library, exercise library, split templates, embeddings",
            "weaviate": "Vector memory for RAG over sessions, food, plans, coach knowledge",
            "influxdb": "Biometric and training trend time-series",
        },
        "compute_layer": {
            "rust_axum": "High-throughput write APIs for workouts, nutrition, lock-in events",
            "go_grpc": "Kafka consumers, notifications, schedule sync, rollup workers",
            "fastapi_langgraph": "AI orchestration, RAG routing, tool calls, LLM streaming",
            "wasm": "On-device rep counting and form scoring path",
        },
        "ai_layer": {
            "vllm": "Self-hosted OpenAI-compatible inference",
            "llm": "Meta-Llama-3 or Mistral deployment tier",
            "embeddings": "nomic-embed-text or bge-large-en-v1.5",
            "rag": "Workout memory + knowledge vault retrieval on every agent message",
        },
        "deployment": {
            "docker_compose": "infra/docker-compose.yml",
            "kubernetes": "infra/kubernetes",
            "schemas": "schemas",
            "services": "services",
        },
    }
