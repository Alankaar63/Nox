from __future__ import annotations

import os
import urllib.request
import json
from typing import Any

from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel, Field


SYSTEM_PROMPT = """
You are NOX, an elite AI fitness agent. You are direct, data-grounded, and never
invent training history. If data is missing, say exactly what data is missing.
Core domains: Great Lock In, Workout Tracker, Training Splits and Knowledge Vault,
Nutrition Engine.
""".strip()


class AgentMessage(BaseModel):
    user_id: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class RagQuery(BaseModel):
    user_id: str
    query: str
    top_k: int = 6


class RagDocument(BaseModel):
    user_id: str
    text: str
    source: str
    collection: str = "WorkoutMemory"
    metadata: dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="NOX AI Orchestrator", version="1.0.0")


def llm_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "nox-local"),
        base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1"),
    )


def embeddings_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("EMBEDDINGS_API_KEY", "nox-local"),
        base_url=os.getenv("EMBEDDINGS_BASE_URL", os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")),
    )


def embed(text: str) -> list[float]:
    model = os.getenv("NOX_EMBEDDING_MODEL", "nomic-embed-text")
    return embeddings_client().embeddings.create(model=model, input=text).data[0].embedding


def weaviate_request(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    base_url = os.getenv("VECTOR_STORE_URL", "http://localhost:8081").rstrip("/")
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def rag_retrieve(payload: RagQuery) -> list[dict[str, Any]]:
    vector = embed(payload.query)
    vector_literal = ", ".join(str(value) for value in vector)
    query = """
    {
      Get {
        WorkoutMemory(
          nearVector: {vector: [%s]}
          where: {path: ["user_id"], operator: Equal, valueText: "%s"}
          limit: %s
        ) {
          text
          source
          metadata
          _additional { distance }
        }
      }
    }
    """ % (vector_literal, payload.user_id.replace('"', '\\"'), payload.top_k)
    result = weaviate_request("/v1/graphql", {"query": query})
    return result.get("data", {}).get("Get", {}).get("WorkoutMemory", [])


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "ai-orchestrator", "status": "ok"}


@app.post("/agent/message")
def agent_message(payload: AgentMessage) -> dict[str, Any]:
    model = os.getenv("NOX_LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    memory = rag_retrieve(RagQuery(user_id=payload.user_id, query=payload.message))
    grounded_context = {**payload.context, "retrieved_memory": memory}
    response = llm_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context: {grounded_context}\n\nUser: {payload.message}"},
        ],
        temperature=0.35,
    )
    return {
        "user_id": payload.user_id,
        "answer": response.choices[0].message.content,
        "model": model,
        "grounding": grounded_context,
    }


@app.post("/rag/query")
def rag_query(payload: RagQuery) -> dict[str, Any]:
    return {
        "query": payload.query,
        "top_k": payload.top_k,
        "matches": rag_retrieve(payload),
        "status": "retrieved",
    }


@app.post("/rag/index")
def rag_index(payload: RagDocument) -> dict[str, Any]:
    vector = embed(payload.text)
    properties = {
        "user_id": payload.user_id,
        "text": payload.text,
        "source": payload.source,
        "metadata": json.dumps(payload.metadata),
    }
    result = weaviate_request(
        "/v1/objects",
        {"class": payload.collection, "properties": properties, "vector": vector},
    )
    return {"status": "indexed", "id": result.get("id"), "collection": payload.collection}
