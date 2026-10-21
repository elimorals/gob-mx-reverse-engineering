"""Reconstruye sitios/subdominios-consolidado.csv desde cero.

Fuentes: nuestros CT (sitios/subdominios/*.txt) + dotgob-mx (si su clon está en /tmp/dotgob-mx).
uso: python3 -I scripts/merge_subdominios.py
"""
import csv
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SUB = RAIZ / "sitios/subdominios"
DOTGOB = Path("/tmp/dotgob-mx")


def norm(h):
    return h.strip().lower().lstrip("*.").removeprefix("http://").removeprefix("https://").rstrip("/")


# nuestros: host -> dependencia (nombre del .txt)
nuestros = {}
for f in SUB.glob("*.txt"):
    for line in f.read_text().splitlines():
        h = norm(line)
        if h.endswith(".gob.mx") or h == "gob.mx":
            nuestros.setdefault(h, f.stem)

# dotgob: host -> flag de actividad
activo = {}
if DOTGOB.exists():
    todos = DOTGOB / "data/subdominios.txt"
    act = DOTGOB / "data/dominios_activos.txt"
    for line in (todos.read_text().splitlines() if todos.exists() else []):
        h = norm(line)
        if h.endswith(".gob.mx"):
            activo.setdefault(h, "inactivo")
    for line in (act.read_text().splitlines() if act.exists() else []):
        esquema = "https" if line.startswith("https") else "http"
        h = norm(line)
        if h.endswith(".gob.mx"):
            activo[h] = f"activo:{esquema}"

todos_hosts = sorted(set(nuestros) | set(activo))
filas = 0
with (RAIZ / "sitios/subdominios-consolidado.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["host", "fuente", "activo_dotgob", "dependencia_o_estado"])
    for h in todos_hosts:
        en_n, en_d = h in nuestros, h in activo
        fuente = "ambos" if en_n and en_d else "nuestro-CT" if en_n else "dotgob-mx"
        dep = nuestros.get(h) or (h.split(".gob.mx")[0].split(".")[-1] if ".gob.mx" in h else "")
        w.writerow([h, fuente, activo.get(h, ""), dep])
        filas += 1

n_act = sum(1 for v in activo.values() if v.startswith("activo"))
print(f"{filas} hosts únicos | nuestros {len(nuestros)} | dotgob {len(activo)} | ambos "
      f"{len(set(nuestros) & set(activo))} | activos(dotgob) {n_act}")
