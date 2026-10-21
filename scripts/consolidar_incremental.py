"""Reconsolida apps.json REUSANDO métricas ya consultadas; solo baja las de IDs nuevos.

Lee métricas previas de apps/apps.json (o un respaldo), las reusa cuando el ID no cambió,
y solo llama a la tienda para apps cuyo ID es nuevo o cuya métrica falta.
uso: .venv/bin/python -I scripts/consolidar_incremental.py <raíz> [apps.json_previo]
"""
import csv
import json
import sys
import time
from pathlib import Path

from google_play_scraper import app as play_app
from google_play_scraper.exceptions import NotFoundError

sys.path.insert(0, str(Path(__file__).parent))
from tienda import IOS_CAMPOS, PLAY_CAMPOS, itunes  # noqa: E402

raiz = Path(sys.argv[1])
previo_path = Path(sys.argv[2]) if len(sys.argv) > 2 else raiz / "apps/apps.json"
previo = {}
if previo_path.exists():
    for a in json.loads(previo_path.read_text()):
        if a.get("android_id"):
            previo[("a", a["android_id"])] = a.get("play")
        if a.get("ios_id"):
            previo[("i", str(a["ios_id"]))] = a.get("appstore")


def play(appid):
    try:
        d = play_app(appid, lang="es", country="mx")
        return {k: d.get(k) for k in PLAY_CAMPOS}
    except NotFoundError:
        return {"no_encontrada": True}
    except Exception as e:
        return {"error": repr(e)}


def ios(trackid):
    for intento in range(4):
        try:
            r = itunes("lookup", id=trackid)
            time.sleep(1.5)
            return {k: r[0].get(k) for k in IOS_CAMPOS} if r else {"no_encontrada": True}
        except Exception as e:
            err = e
            time.sleep(10 * (intento + 1))
    return {"error": repr(err)}


apps, vistos = [], {}
for f in sorted((raiz / "apps/inventario").glob("*.json")):
    for a in json.loads(f.read_text()):
        a["segmento"] = f.stem
        a["android_id"] = a.get("android_id") or None
        a["ios_id"] = str(a["ios_id"]) if a.get("ios_id") else None
        clave = a["android_id"] or a["ios_id"] or (a["nombre"].lower(), a.get("estado"))
        if clave in vistos:
            vistos[clave].setdefault("tambien_en", []).append(f.stem)
            continue
        vistos[clave] = a
        apps.append(a)

nuevas_p = nuevas_i = 0
for a in apps:
    aid, iid = a["android_id"], a["ios_id"]
    # Play: reusa si ya hay métrica no-error; si no, baja
    pm = previo.get(("a", aid)) if aid else None
    if aid and (not pm or "error" in pm):
        pm = play(aid); nuevas_p += 1
    a["play"] = pm
    im = previo.get(("i", iid)) if iid else None
    if iid and (not im or "error" in im):
        im = ios(iid); nuevas_i += 1
    a["appstore"] = im

(raiz / "apps/apps.json").write_text(json.dumps(apps, ensure_ascii=False, indent=1, default=str))

cols = ["nombre", "siglas", "dependencia", "nivel", "estado", "sector", "android_id", "ios_id", "requiere_cuenta",
        "estatus", "play_dev", "play_instalaciones", "play_instalaciones_reales", "play_score", "play_ratings",
        "play_actualizada", "play_version", "ios_vendedor", "ios_score", "ios_ratings", "ios_actualizada",
        "ios_version", "proposito", "segmento"]
with open(raiz / "apps/apps.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, cols, extrasaction="ignore")
    w.writeheader()
    for a in apps:
        pp, ii = a["play"] or {}, a["appstore"] or {}
        w.writerow({**a, "play_dev": pp.get("developer"), "play_instalaciones": pp.get("installs"),
                    "play_instalaciones_reales": pp.get("realInstalls"), "play_score": pp.get("score"),
                    "play_ratings": pp.get("ratings"), "play_actualizada": pp.get("updated"),
                    "play_version": pp.get("version"), "ios_vendedor": ii.get("sellerName"),
                    "ios_score": ii.get("averageUserRating"), "ios_ratings": ii.get("userRatingCount"),
                    "ios_actualizada": ii.get("currentVersionReleaseDate"), "ios_version": ii.get("version")})

print(f"{len(apps)} apps | nuevas consultas: {nuevas_p} Play, {nuevas_i} iOS")
