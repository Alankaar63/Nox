#!/usr/bin/env bash
set -euo pipefail

KEYSTORE="/Users/vivektripathi/keystores/nox-release.jks"
if [[ ! -f "$KEYSTORE" ]]; then
  echo "Keystore not found at $KEYSTORE"
  exit 1
fi

for d in /Users/vivektripathi/.gradle/daemon/*; do
  [[ -d "$d" ]] || continue
  cp -f "$KEYSTORE" "$d/nox-release.jks"
done

echo "Copied keystore override into all Gradle daemon dirs."
