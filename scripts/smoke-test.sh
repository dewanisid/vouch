#!/usr/bin/env bash
set -u

failed=0

check() {
  local name="$1"
  shift
  if "$@" > /dev/null 2>&1; then
    echo "ok    $name"
  else
    echo "FAIL  $name"
    failed=1
  fi
}

check postgres docker compose exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER"'
check redis docker compose exec -T redis redis-cli ping
check prometheus curl -fsS --max-time 3 http://localhost:9090/-/healthy
check loki curl -fsS --max-time 3 http://localhost:3100/ready
check grafana curl -fsS --max-time 3 http://localhost:3000/api/health
check otel-collector curl -fsS --max-time 3 http://localhost:13133

exit "$failed"
