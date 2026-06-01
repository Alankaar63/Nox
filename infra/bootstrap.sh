#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infra/docker-compose.yml"

echo "Waiting for Cassandra..."
until docker compose -f "$COMPOSE_FILE" exec -T cassandra cqlsh -e "DESCRIBE CLUSTER" >/dev/null 2>&1; do
  sleep 4
done
docker compose -f "$COMPOSE_FILE" exec -T cassandra cqlsh < "$ROOT_DIR/schemas/cassandra/nox_keyspace.cql"

echo "Waiting for Weaviate..."
until curl --fail --silent http://127.0.0.1:8081/v1/.well-known/ready >/dev/null; do
  sleep 3
done

python3 - "$ROOT_DIR/schemas/weaviate/nox_classes.json" <<'PY'
import json
import sys
import urllib.error
import urllib.request

schema_path = sys.argv[1]
with open(schema_path, encoding="utf-8") as schema_file:
    classes = json.load(schema_file)["classes"]

for class_schema in classes:
    request = urllib.request.Request(
        "http://127.0.0.1:8081/v1/schema",
        data=json.dumps(class_schema).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(request, timeout=8).read()
        print(f"Created Weaviate class: {class_schema['class']}")
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            print(f"Weaviate class already exists: {class_schema['class']}")
        else:
            raise
PY

echo "NOX data schemas initialized."
