#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APK_RELEASE="$ROOT_DIR/nox-android/app/build/outputs/apk/release/app-release.apk"
APK_DEBUG="$ROOT_DIR/nox-android/app/build/outputs/apk/debug/app-debug.apk"
APK_DST_DIR="$ROOT_DIR/fitness_nutrition_agent/web/downloads"
APK_DST="$APK_DST_DIR/NOX-android-latest.apk"

if [[ -f "$APK_RELEASE" ]]; then
  APK_SRC="$APK_RELEASE"
elif [[ -f "$APK_DEBUG" ]]; then
  APK_SRC="$APK_DEBUG"
else
  echo "No APK found."
  echo "Expected one of:"
  echo "  $APK_RELEASE"
  echo "  $APK_DEBUG"
  echo "Build first from Android Studio or run ./gradlew assembleDebug"
  exit 1
fi

mkdir -p "$APK_DST_DIR"
cp "$APK_SRC" "$APK_DST"
echo "Published APK: $APK_DST (source: $APK_SRC)"
