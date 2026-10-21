"""Empaqueta el inventario en web/data.js (window.GOBMX) para el dashboard.

Recorta campos pesados y agrega los subdominios. Así el dashboard funciona en file:// y en Pages
sin fetch ni CORS. uso: python3 -I scripts/build_dashboard_data.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def apps():
    out = []
    for a in json.loads((R / "apps/apps.json").read_text()):
        p, i = a.get("play") or {}, a.get("appstore") or {}
        out.append({
            "nombre": a.get("nombre"), "siglas": a.get("siglas"), "dependencia": a.get("dependencia"),
            "nivel": a.get("nivel"), "estado": a.get("estado"), "sector": a.get("sector"),
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
    for f in sorted((R / "sitios").glob("*.json")):
        for s in json.loads(f.read_text()):
            er = (s.get("estado_real") or [{}])
            out.append({
                "dependencia": s.get("dependencia"), "siglas": s.get("siglas"), "nivel": s.get("nivel"),
                "estado": s.get("estado"), "url": s.get("url"), "tipo": s.get("tipo"),
                "plataforma": s.get("plataforma"), "anti_bot": s.get("anti_bot"),
                "auth": s.get("autenticacion"),
                "resultado": er[-1].get("resultado") if isinstance(er, list) and er else None,
                "prop": s.get("proposito"),
            })
    return out


def servicios():
    out = []
    for name in ("brechas.json", "catalogo-conamer.json"):
        f = R / "servicios" / name
        if f.exists():
            for s in json.loads(f.read_text()):
                s["_fuente"] = name.replace(".json", "")
                out.append(s)
    # catálogo federal CONAMER recortado (solo campos útiles para el dashboard)
    cnts = R / "servicios/cnts-federal.json"
    if cnts.exists():
        for t in json.loads(cnts.read_text()):
            out.append({
                "_fuente": "cnts",
                "nombre_tramite": t.get("nombre_tramite") or t.get("nombre"),
                "dependencia": t.get("dependencia"), "siglas": t.get("siglas"),
                "homoclave": t.get("homoclave"),
                "nivel_digitalizacion": t.get("nivel_digitalizacion"),
                "nivel": "federal",
            })
    return out


def permisos():
    f = R / "apps/permisos/permisos.json"
    return json.loads(f.read_text()) if f.exists() else []


def subdominios():
    import shutil
    f = R / "sitios/subdominios-consolidado.csv"
    por_dep, por_fuente, activos, total = Counter(), Counter(), 0, 0
    if f.exists():
        with f.open() as fh:
            for row in csv.DictReader(fh):
                total += 1
                por_dep[row.get("dependencia_o_estado") or "—"] += 1
                por_fuente[row.get("fuente") or "—"] += 1
                if str(row.get("activo_dotgob", "")).startswith("activo"):
                    activos += 1
        # copia junto al dashboard para carga diferida (fetch same-origin)
        shutil.copyfile(f, R / "web/subdominios.csv")
    return {"total": total, "activos": activos,
            "top": por_dep.most_common(30), "fuentes": por_fuente.most_common()}


data = {"apps": apps(), "sitios": sitios(), "servicios": servicios(),
        "permisos": permisos(), "subdominios": subdominios(), "corte": "2026-10-21"}
(R / "web").mkdir(exist_ok=True)
js = "window.GOBMX = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
(R / "web/data.js").write_text(js)
kb = len((R / "web/data.js").read_bytes()) // 1024
print(f"web/data.js: {len(data['apps'])} apps, {len(data['sitios'])} sitios, "
      f"{len(data['servicios'])} servicios, {len(data['permisos'])} permisos, "
      f"{data['subdominios']['total']} subdominios ({kb} KB)")
