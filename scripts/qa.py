"""QA de consistencia del inventario. No modifica nada: reporta.

Detecta: IDs duplicados entre segmentos, nombres repetidos, valores de enum fuera de esquema,
campos faltantes, apps sin ninguna fuente, y orden/poder/subtipo/municipio inválidos o incoherentes
(apps, sitios y servicios brechas + catalogo-conamer). Sale con código !=0 si hay errores duros.
uso: python3 -I scripts/qa.py [--test]
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from gobmx import ENTIDADES, ORDENES, PODERES  # noqa: E402

NIVELES = {"federal", "estatal", "municipal", "paraestatal", "autonomo", "no_oficial",
           "poder_legislativo", "poder_judicial"}
ESTATUS = {"activa", "retirada", "sin actualizar >2 años", "desconocido"}
CAMPOS_APP = {"nombre", "dependencia", "nivel", "estatus"}
# subtipo es texto corto abierto por contrato: los conocidos no avisan, otros sí (para revisarlos)
SUBTIPOS = {None, "paraestatal", "desconcentrado", "universidad_autonoma", "extinto"}

errores, avisos = [], []


def apps_por_segmento():
    out = {}
    for f in sorted((RAIZ / "apps/inventario").glob("*.json")):
        out[f.stem] = json.loads(f.read_text())
    return out


def registros_orden_poder():
    fs = sorted((RAIZ / "apps/inventario").glob("*.json")) + sorted((RAIZ / "sitios").glob("*.json"))
    fs += [RAIZ / "servicios/brechas.json", RAIZ / "servicios/catalogo-conamer.json"]
    for f in fs:
        if f.exists():
            for r in json.loads(f.read_text()):
                yield str(f.relative_to(RAIZ)), r


def validar_orden_poder(r, donde):
    """Errores duros de orden/poder/subtipo/municipio de un registro (lista vacía = ok)."""
    nom = f"{r.get('nombre') or r.get('dependencia') or r.get('servicio')} [{donde}]"
    faltan = {"orden", "poder", "subtipo", "municipio"} - set(r)
    if faltan:
        return [f"faltan {sorted(faltan)} (corre scripts/clasificar_orden_poder.py): {nom}"]
    o, p, errs = r["orden"], r["poder"], []
    if r.get("nivel") == "no_oficial":
        if p is not None or o is not None:
            errs.append(f"no_oficial debe tener orden y poder null: {nom}")
        return errs
    if o not in ORDENES:
        errs.append(f"orden inválido '{o}': {nom}")
    if p not in PODERES:
        errs.append(f"poder inválido '{p}': {nom}")
    if r["subtipo"] is not None and not isinstance(r["subtipo"], str):
        errs.append(f"subtipo no es texto: {nom}")
    agregado = r.get("estado") not in ENTIDADES  # brechas 'todos'/'mayoría'/'varios'
    if o == "municipal" and not r["municipio"] and not agregado:
        errs.append(f"orden=municipal sin municipio: {nom}")
    if o != "municipal" and r["municipio"]:
        errs.append(f"municipio con orden={o}: {nom}")
    if o == "federal" and r.get("estado") != "Nacional":
        errs.append(f"orden=federal con estado '{r.get('estado')}': {nom}")
    if o in ("estatal", "municipal") and r.get("estado") == "Nacional":
        errs.append(f"orden={o} con estado Nacional: {nom}")
    return errs


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

    # 4. orden / poder / subtipo / municipio (apps, sitios, servicios)
    for donde, r in registros_orden_poder():
        errores.extend(validar_orden_poder(r, donde))
        if r.get("subtipo") not in SUBTIPOS:
            avisos.append(f"subtipo no estándar '{r.get('subtipo')}': {r.get('dependencia')} [{donde}]")
        if r.get("orden") == "municipal" and not r.get("municipio"):
            avisos.append(f"municipal agregado sin municipio (estado '{r.get('estado')}'): "
                          f"{r.get('dependencia') or r.get('servicio')} [{donde}]")

    print(f"ERRORES ({len(errores)}):")
    for e in errores:
        print("  ✗", e)
    print(f"\nAVISOS ({len(avisos)}):")
    for v in avisos[:40]:
        print("  ·", v)
    if len(avisos) > 40:
        print(f"  ... y {len(avisos) - 40} más")

    return 1 if errores else 0


def _autoprueba():
    ok = {"nivel": "municipal", "estado": "Jalisco", "orden": "municipal", "poder": "ejecutivo",
          "subtipo": None, "municipio": "Guadalajara"}
    assert validar_orden_poder(ok, "t") == []
    assert validar_orden_poder({**ok, "municipio": None}, "t")
    assert validar_orden_poder({**ok, "poder": "otro"}, "t")
    assert validar_orden_poder({**ok, "nivel": "no_oficial", "orden": None, "poder": "ejecutivo"}, "t")
    assert validar_orden_poder({**ok, "estado": "varios", "municipio": None}, "t") == []
    print("autoprueba de qa: OK")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _autoprueba()
        sys.exit(0)
    sys.exit(main())
