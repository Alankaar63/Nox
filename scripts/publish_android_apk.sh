#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APK_SRC="$ROOT_DIR/nox-android/app/build/outputs/apk/release/app-release.apk"
APK_DST_DIR="$ROOT_DIR/fitness_nutrition_agent/web/downloads"
APK_DST="$APK_DST_DIR/NOX-android-latest.apk"

if [[ ! -f "$APK_SRC" ]]; then
  echo "Release APK not found at: $APK_SRC"
  echo "Build it first in Android Studio (Build > Generate Signed Bundle / APK)."
  exit 1
fi

mkdir -p "$APK_DST_DIR"
cp "$APK_SRC" "$APK_DST"
echo "Published APK: $APK_DST"
