"""QA de consistencia del inventario. No modifica nada: reporta.

Detecta: IDs duplicados entre segmentos, nombres repetidos, valores de enum fuera de esquema,
campos faltantes, y apps sin ninguna fuente. Sale con código !=0 si hay errores duros.
uso: python3 -I scripts/qa.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

NIVELES = {"federal", "estatal", "municipal", "paraestatal", "autonomo", "no_oficial",
           "poder_legislativo", "poder_judicial"}
ESTATUS = {"activa", "retirada", "sin actualizar >2 años", "desconocido"}
CAMPOS_APP = {"nombre", "dependencia", "nivel", "estatus"}

errores, avisos = [], []


def apps_por_segmento():
    out = {}
    for f in sorted((RAIZ / "apps/inventario").glob("*.json")):
        out[f.stem] = json.loads(f.read_text())
    return out


def main():
    segs = apps_por_segmento()
    todas = [(seg, a) for seg, lst in segs.items() for a in lst]
    print(f"== {len(todas)} apps en {len(segs)} segmentos ==\n")

    # 1. IDs duplicados entre entradas distintas
    for campo in ("android_id", "ios_id"):
        idx = defaultdict(list)
        for seg, a in todas:
            v = a.get(campo)
            if v:
                idx[str(v)].append(f"{a.get('nombre')} [{seg}]")
        for v, quienes in idx.items():
            if len(quienes) > 1:
                errores.append(f"{campo} duplicado {v}: {' | '.join(quienes)}")

    # 2. nombres repetidos (posible dup cross-segmento, p.ej. federal vs paraestatal)
    nombres = Counter(a.get("nombre", "").strip().lower() for _, a in todas)
    for nom, n in nombres.items():
        if n > 1 and nom:
            donde = [f"{seg}" for seg, a in todas if a.get("nombre", "").strip().lower() == nom]
            avisos.append(f"nombre repetido x{n}: '{nom}' en {', '.join(donde)}")

    # 3. enums y campos
    for seg, a in todas:
        if a.get("nivel") not in NIVELES:
            errores.append(f"nivel inválido '{a.get('nivel')}' en {a.get('nombre')} [{seg}]")
        if a.get("estatus") not in ESTATUS:
            errores.append(f"estatus inválido '{a.get('estatus')}' en {a.get('nombre')} [{seg}]")
        faltan = CAMPOS_APP - set(a)
        if faltan:
            errores.append(f"faltan campos {faltan} en {a.get('nombre')} [{seg}]")
        if not a.get("fuentes"):
            avisos.append(f"sin fuentes: {a.get('nombre')} [{seg}]")

    print(f"ERRORES ({len(errores)}):")
    for e in errores:
        print("  ✗", e)
    print(f"\nAVISOS ({len(avisos)}):")
    for v in avisos[:40]:
        print("  ·", v)
    if len(avisos) > 40:
        print(f"  ... y {len(avisos) - 40} más")

    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
