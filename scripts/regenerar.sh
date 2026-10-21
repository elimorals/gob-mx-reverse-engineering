#!/usr/bin/env bash
# Regenera todos los derivados del inventario desde las fuentes (apps/inventario, sitios, servicios).
# Idempotente. Uso: scripts/regenerar.sh
set -euo pipefail
cd "$(dirname "$0")/.."
RAIZ="$PWD"

PY="${PYTHON:-python3}"
if [ -x .venv/bin/python ]; then PY=".venv/bin/python"; fi
export SSL_CERT_FILE="$($PY -c 'import certifi;print(certifi.where())' 2>/dev/null || true)"

echo "==> 1/4 subdominios (CT propio + dotgob-mx si está en /tmp/dotgob-mx)"
$PY -I scripts/merge_subdominios.py || echo "  (merge omitido)"

echo "==> 2/4 consolidar apps (incremental: reusa métricas, baja solo IDs nuevos)"
$PY -I scripts/consolidar_incremental.py "$RAIZ" "$RAIZ/apps/apps.json"

echo "==> 3/4 QA de consistencia"
$PY -I scripts/qa.py || echo "  (QA reportó errores, revisar arriba)"

echo "==> 4/4 estadísticas"
$PY -I scripts/stats.py | head -6

echo "listo. Revisa git diff antes de commitear."
