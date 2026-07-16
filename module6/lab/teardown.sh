#!/usr/bin/env bash
# Completely remove the lab: containers, the database volume, and the
# locally-built web image. Nothing is left on the host afterwards.
set -euo pipefail
cd "$(dirname "$0")"

echo "🧹 Removing containers, volumes, and the built image..."
docker compose down -v --rmi local

echo "✅ Gone. To also delete the base images you pulled:"
echo "   docker rmi mysql:8.4 php:8.3-apache"
