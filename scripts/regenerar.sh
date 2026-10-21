#!/usr/bin/env bash
# Regenera todos los derivados del inventario desde las fuentes (apps/inventario, sitios, servicios).
# Idempotente. Uso: scripts/regenerar.sh   (SIN_RED=1 para no consultar tiendas)
set -euo pipefail
cd "$(dirname "$0")/.."
RAIZ="$PWD"

PY="${PYTHON:-python3}"
if [ -x .venv/bin/python ]; then PY=".venv/bin/python"; fi
export SSL_CERT_FILE="$($PY -c 'import certifi;print(certifi.where())' 2>/dev/null || true)"

echo "==> 1/6 subdominios (CT propio + dotgob-mx si está en /tmp/dotgob-mx)"
$PY -I scripts/merge_subdominios.py || echo "  (merge omitido)"

echo "==> 2/6 clasificar orden/poder/subtipo/municipio (solo agrega campos que faltan)"
$PY -I scripts/clasificar_orden_poder.py

echo "==> 3/6 consolidar apps (incremental: reusa métricas, baja solo IDs nuevos)"
$PY -I scripts/consolidar_incremental.py "$RAIZ" "$RAIZ/apps/apps.json"

echo "==> 4/6 QA de consistencia"
$PY -I scripts/qa.py || echo "  (QA reportó errores, revisar arriba)"

echo "==> 5/6 estadísticas"
$PY -I scripts/stats.py | head -6

echo "==> 6/6 dashboard (web/data.js)"
$PY -I scripts/build_dashboard_data.py

echo "listo. Revisa git diff antes de commitear."
