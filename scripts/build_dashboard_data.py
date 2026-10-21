"""Empaqueta el inventario en web/data.js (window.GOBMX) para el dashboard.

Recorta campos pesados y agrega los subdominios. Así el dashboard funciona en file:// y en Pages
sin fetch ni CORS. Las métricas de `entidades`/`municipios` salen de gobmx.metricas() (la misma
implementación que usan el CLI y el MCP). uso: python3 -I scripts/build_dashboard_data.py
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import gobmx  # noqa: E402

OP = ("orden", "poder", "subtipo", "municipio")


def op(x):
    return {k: x.get(k) for k in OP}


def apps():
    out = []
    for a in gobmx.apps():
        p, i = a.get("play") or {}, a.get("appstore") or {}
        out.append({
            "nombre": a.get("nombre"), "siglas": a.get("siglas"), "dependencia": a.get("dependencia"),
            "nivel": a.get("nivel"), **op(a), "estado": a.get("estado"), "sector": a.get("sector"),
            "estatus": a.get("estatus"), "android": a.get("android_id"), "ios": a.get("ios_id"),
            "cuenta": a.get("requiere_cuenta"),
            "inst": p.get("realInstalls") or 0, "inst_txt": p.get("installs"),
            "play_score": p.get("score"), "play_ratings": p.get("ratings"),
            "ios_score": i.get("averageUserRating"), "ios_ratings": i.get("userRatingCount"),
            "prop": a.get("proposito"),
        })
    return out


def sitios():
    out = []
    for s in gobmx.sitios():
        er = (s.get("estado_real") or [{}])
        out.append({
            "dependencia": s.get("dependencia"), "siglas": s.get("siglas"), "nivel": s.get("nivel"),
            **op(s), "estado": s.get("estado"), "url": s.get("url"), "tipo": s.get("tipo"),
            "plataforma": s.get("plataforma"), "anti_bot": s.get("anti_bot"),
            "auth": s.get("autenticacion"),
            "resultado": er[-1].get("resultado") if isinstance(er, list) and er else None,
            "prop": s.get("proposito"),
        })
    return out


def servicios():
    out = []
    for s in gobmx.servicios():
        if "nombre_tramite" in s and "servicio" not in s:  # catálogo federal CONAMER (cnts): recortado
            out.append({
                "_fuente": "cnts",
                "nombre_tramite": s.get("nombre_tramite") or s.get("nombre"),
                "dependencia": s.get("dependencia"), "siglas": s.get("siglas"),
                "homoclave": s.get("homoclave"),
                "nivel_digitalizacion": s.get("nivel_digitalizacion"),
                "nivel": "federal", **op(s),
            })
        else:
            out.append({"_fuente": "catalogo-conamer" if "homoclave" in s else "brechas", **s})
    return out


def subdominios():
    f = R / "sitios/subdominios-consolidado.csv"
    por_dep, por_fuente, activos, total = Counter(), Counter(), 0, 0
    if f.exists():
        import csv
        with f.open() as fh:
            for row in csv.DictReader(fh):
                total += 1
                por_dep[row.get("dependencia_o_estado") or "—"] += 1
                por_fuente[row.get("fuente") or "—"] += 1
                if str(row.get("activo_dotgob", "")).startswith("activo"):
                    activos += 1
        # copia junto al dashboard para carga diferida (fetch same-origin)
        shutil.copyfile(f, R / "web/subdominios.csv")
    _, cobertura = gobmx.subdominios_por_lugar()
    return {"total": total, "activos": activos,
            "top": por_dep.most_common(30), "fuentes": por_fuente.most_common(),
            "mapeo_lugar": cobertura}


A, S = apps(), sitios()
crudos_a, crudos_s = gobmx.apps(), gobmx.sitios()
data = {"apps": A, "sitios": S, "servicios": servicios(),
        "permisos": gobmx.permisos(), "subdominios": subdominios(),
        "orden_poder": {"apps": gobmx.matriz_orden_poder(A), "sitios": gobmx.matriz_orden_poder(S)},
        "entidades": gobmx.metricas("estatal", crudos_a, crudos_s),
        "municipios": gobmx.metricas("municipal", crudos_a, crudos_s),
        "comparacion": {"metodologia": gobmx.METODOLOGIA,
                        "presupuesto_entidades": bool(gobmx.presupuesto("entidades")),
                        "presupuesto_municipios": bool(gobmx.presupuesto("municipios"))},
        "corte": "2026-10-21"}
(R / "web").mkdir(exist_ok=True)
js = "window.GOBMX = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
(R / "web/data.js").write_text(js)
kb = len((R / "web/data.js").read_bytes()) // 1024
print(f"web/data.js: {len(A)} apps, {len(S)} sitios, {len(data['servicios'])} servicios, "
      f"{len(data['permisos'])} permisos, {data['subdominios']['total']} subdominios, "
      f"{len(data['entidades'])} entidades, {len(data['municipios'])} municipios ({kb} KB)")
