#!/usr/bin/env bash
# Bring up the disposable Module 6 lab and load the employees database.
#
# Data source (in priority order):
#   1. The real MySQL sample DB from datacharmer/test_db (matches the PDF 1:1).
#   2. If that repo can't be cloned (offline), a compact fallback seed.
set -euo pipefail
cd "$(dirname "$0")"

REPO_URL="https://github.com/datacharmer/test_db.git"

# --- 1. Fetch the real dataset (shallow clone, ~35MB) -------------------------
if [ ! -f test_db/employees.sql ]; then
    echo "📦 Cloning $REPO_URL ..."
    git clone --depth 1 "$REPO_URL" test_db || echo "⚠️  Clone failed — will use compact fallback seed."
fi

# --- 2. Start containers ------------------------------------------------------
echo "🚧 Building and starting containers..."
docker compose up -d --build

echo "⏳ Waiting for MySQL to become healthy..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' websec_db 2>/dev/null)" = "healthy" ]; do
    sleep 2
    printf '.'
done
echo

# --- 3. Load data (idempotent: skip if salaries already populated) ------------
already_loaded=$(docker compose exec -T db \
    mysql -uroot -ppassword -N -B \
    -e "SELECT COUNT(*) FROM employees.salaries" 2>/dev/null || echo 0)

if [ "${already_loaded:-0}" -gt 0 ]; then
    echo "✅ employees.salaries already has ${already_loaded} rows — skipping load."
elif [ -f test_db/employees.sql ]; then
    echo "⬇️  Loading REAL employees database (this takes ~1 min)..."
    docker compose cp test_db db:/seed
    # `source` in employees.sql resolves relative to the working dir, so -w /seed.
    docker compose exec -T -w /seed db sh -c "mysql -uroot -ppassword < employees.sql"
    echo "✅ Real dataset loaded."
else
    echo "⬇️  Loading compact fallback seed..."
    docker compose exec -T db sh -c "mysql -uroot -ppassword" < db/seed-compact.sql
    echo "✅ Fallback seed loaded."
fi

rows=$(docker compose exec -T db mysql -uroot -ppassword -N -B \
    -e "SELECT COUNT(*) FROM employees.salaries" 2>/dev/null || echo "?")

echo
echo "✅ Lab is up.  salaries rows: ${rows}"
echo "   Web interface : http://localhost:8080"
echo "   DB (internal) : host 'db', user 'student' / 'student', database 'employees'"
echo
echo "   Try:  http://localhost:8080/module4.php     (all salaries)"
echo "         http://localhost:8080/lookup.html     (injection target)"
echo "         http://localhost:8080/info.php        (PHP info)"
echo
echo "   Tear everything down with:  ./teardown.sh"
