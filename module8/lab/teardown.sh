#!/usr/bin/env bash
# Remove the lab container and the locally-built image.
#
# NOTE: this deliberately does NOT delete ./artifacts/. The assignment says to
# keep key.pem and cert.pem for the next module, so your generated keys and
# certificate stay on the host. Delete them yourself when the course is done.
set -euo pipefail
cd "$(dirname "$0")"

echo "🧹 Removing the container and the built image..."
docker compose down --rmi local

echo "✅ Gone. Your keys and certificate are untouched in ./artifacts/:"
ls -1 artifacts 2>/dev/null | sed 's/^/     /' || echo "     (empty)"

echo
echo "   To also delete the base image:  docker rmi ubuntu:24.04"
echo "   To delete your generated keys:  rm -rf artifacts/"
