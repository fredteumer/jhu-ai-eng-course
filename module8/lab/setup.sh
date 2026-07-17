#!/usr/bin/env bash
# Bring up the Module 8 PKI lab and verify the OpenSSL version matches the
# assignment PDF. Nothing is installed on the host.
set -euo pipefail
cd "$(dirname "$0")"

EXPECTED="OpenSSL 3.0.13"

mkdir -p artifacts

# Run the container as us, so files it writes into the bind-mounted artifacts/
# are owned by us on the host rather than by root. Consumed by docker-compose.yml.
export LAB_UID="$(id -u)"
export LAB_GID="$(id -g)"

echo "🚧 Building and starting the lab container..."
docker compose up -d --build

echo "⏳ Waiting for the container to be ready..."
until [ "$(docker inspect -f '{{.State.Running}}' pki_lab 2>/dev/null)" = "true" ]; do
    sleep 1
    printf '.'
done
echo

# --- Verify we got the OpenSSL the assignment was written against -------------
actual=$(docker compose exec -T pki openssl version)

echo
if [[ "$actual" == "$EXPECTED"* ]]; then
    echo "✅ ${actual}"
    echo "   Matches the assignment PDF exactly (Figure 1, page 1)."
else
    echo "⚠️  Expected '${EXPECTED}...' but got '${actual}'."
    echo "   Screenshots will not match the guide's banner. Harmless for grading,"
    echo "   but check whether the ubuntu:24.04 base image moved."
fi

# --- Sanity-check the uid mapping actually took --------------------------------
whoami_out=$(docker compose exec -T pki id -un 2>/dev/null || echo "?")
if [ "$whoami_out" = "?" ] || [ -z "$whoami_out" ]; then
    echo "⚠️  Could not resolve the container user — files may land root-owned."
else
    echo "✅ Container user: ${whoami_out} (uid ${LAB_UID}) — artifacts/ stays yours."
fi

# Left-over root-owned files from an earlier run would be unwritable for us now.
if [ -n "$(find artifacts -maxdepth 1 ! -user "$(id -un)" -print -quit 2>/dev/null)" ]; then
    echo
    echo "💡 artifacts/ holds files from a previous root-owned run. To reclaim them:"
    echo "   sudo chown -R ${LAB_UID}:${LAB_GID} artifacts/"
fi

cat <<'EOF'

✅ Lab is up.

   Drop into the sandbox shell (this is where you run every assignment command):

       docker compose exec pki bash

   Anything you create in there appears on the host under ./artifacts/ and
   SURVIVES ./teardown.sh — which is what the PDF's "save cert.pem for the next
   module" note requires.

   Part 1's `hostnamectl` needs systemd and will NOT work in a container. It is
   also not on the grading rubric. Use one of these instead:

       docker compose exec pki uname -a
       docker compose exec pki cat /etc/os-release
       hostnamectl                      # <- or just run it on your Arch host

   Tear down with:  ./teardown.sh
EOF
