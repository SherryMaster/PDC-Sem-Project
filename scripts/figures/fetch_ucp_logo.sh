#!/usr/bin/env bash
# Idempotent downloader for the UCP circular seal.
# Source: https://en.wikipedia.org/wiki/University_of_Central_Punjab
# License: fair-use (logo of a public university, used in an academic report).
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${SCRIPT_DIR}/ucp_logo.jpg"
URL="https://upload.wikimedia.org/wikipedia/en/e/eb/University_of_Central_Punjab_%28logo%29.jpg"

if [ -f "${TARGET}" ] && [ -s "${TARGET}" ]; then
    echo "UCP logo already present at ${TARGET} (skipping download)"
    exit 0
fi

echo "Downloading UCP logo from ${URL} ..."
curl -sSL -o "${TARGET}" "${URL}"

if [ ! -s "${TARGET}" ]; then
    echo "ERROR: download failed, ${TARGET} is empty" >&2
    rm -f "${TARGET}"
    exit 1
fi

echo "Saved to ${TARGET}"
ls -la "${TARGET}"
