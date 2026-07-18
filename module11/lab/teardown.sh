#!/usr/bin/env bash
# Tear down the Module 11 Zero Trust / IAM lab.
#
# Removes the four containers, their volumes, the bind-mounted runtime state
# (Ghost content, MySQL data, Nginx Proxy Manager config), the generated
# self-signed certificates, and Authelia's local database.
#
# NOTE: this deliberately does NOT touch /etc/hosts -- that needs sudo and is
# the one change this lab made outside Docker and this repo. The script prints
# a reminder at the end. It also leaves the scaffold configs (docker-compose.yml,
# authelia/config/*.yml, advanced-config/*) in place, since those are tracked
# and document what was built.
set -euo pipefail
cd "$(dirname "$0")/IDZT"

echo "🧹 Stopping containers and removing volumes..."
docker compose down -v

echo
echo "🧹 Removing runtime state (bind mounts, certs, Authelia DB)..."
# Ghost and MySQL run as root inside their containers, so the directories they
# created are root-owned on the host and need sudo to remove.
for d in ghost mysql nginx-proxy-manager certs; do
  if [ -e "$d" ]; then
    echo "     removing ./$d"
    sudo rm -rf "$d"
  fi
done
rm -f authelia/config/db.sqlite3 authelia/config/notification.txt

echo
echo "✅ Containers, volumes, and runtime state are gone."
echo "   Scaffold configs kept: docker-compose.yml, authelia/config/*.yml, advanced-config/"
echo "   Evidence and writeup kept in ../../evidence/ and ../../"

echo
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                        ║"
echo "║   ⚠️  MANUAL STEP REQUIRED -- /etc/hosts WAS MODIFIED  ⚠️                ║"
echo "║                                                                        ║"
echo "║   This lab added ONE line to /etc/hosts. It is still there.            ║"
echo "║   This script cannot remove it for you (needs sudo + an editor).       ║"
echo "║                                                                        ║"
echo "║   Remove this line:                                                    ║"
echo "║                                                                        ║"
echo "║     127.0.0.1  auth.home.local  blog.home.local  admin.home.local      ║"
echo "║                                                                        ║"
echo "║   Edit it:      sudo \$EDITOR /etc/hosts                                 ║"
echo "║                                                                        ║"
echo "║   Or remove it in place:                                               ║"
echo "║     sudo sed -i '/home\\.local/d' /etc/hosts                             ║"
echo "║                                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"

echo
if grep -q "home\.local" /etc/hosts 2>/dev/null; then
  echo "   🛑 CONFIRMED STILL PRESENT in /etc/hosts:"
  grep -n "home\.local" /etc/hosts | sed 's/^/        /'
else
  echo "   ✅ No home.local entries found in /etc/hosts -- already clean."
fi

echo
echo "   Optional, reclaims ~1.5 GB of pulled images:"
echo "     docker image rm authelia/authelia:latest jc21/nginx-proxy-manager:latest ghost:latest mysql:8.0"
