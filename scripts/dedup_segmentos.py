"""Quita apps duplicadas entre segmentos federales.

Regla: si una app de federal-secretarias.json comparte android_id o ios_id con una de
federal-autonomos-paraestatales.json, se queda en autonomos-paraestatales (su hogar natural:
SAT, Guardia Nacional, PROFEPA, CONALITEG, Gasoapp... son desconcentrados/paraestatales) y se
elimina de secretarias. Es la misma entrada que consolidar.py ya deduplica en apps.json.
uso: python3 -I scripts/dedup_segmentos.py [--apply]   (sin --apply solo reporta)
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SEC = RAIZ / "apps/inventario/federal-secretarias.json"
AUT = RAIZ / "apps/inventario/federal-autonomos-paraestatales.json"
aplicar = "--apply" in sys.argv

aut = json.loads(AUT.read_text())
ids_aut = {str(a[k]) for a in aut for k in ("android_id", "ios_id") if a.get(k)}

sec = json.loads(SEC.read_text())
quitar, quedan = [], []
for a in sec:
    aid, iid = a.get("android_id"), a.get("ios_id")
    if (aid and str(aid) in ids_aut) or (iid and str(iid) in ids_aut):
        quitar.append(a["nombre"])
    else:
        quedan.append(a)

print(f"federal-secretarias: {len(sec)} -> {len(quedan)} (quita {len(quitar)} dup ya presentes en autonomos-paraestatales)")
for n in quitar:
    print("  -", n)

if aplicar and quitar:
    SEC.write_text(json.dumps(quedan, ensure_ascii=False, indent=1))
    print("aplicado.")
elif quitar:
    print("\n(dry-run; usa --apply para escribir)")
