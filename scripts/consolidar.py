"""Une segmentos/*.json, deduplica y enriquece con métricas de Play y App Store.

Salida: datos/apps.json, datos/apps.csv
uso: .venv/bin/python -I scripts/consolidar.py <raíz del proyecto>
"""
import csv
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from google_play_scraper import app
from google_play_scraper.exceptions import NotFoundError

sys.path.insert(0, str(Path(__file__).parent))
from tienda import IOS_CAMPOS, PLAY_CAMPOS, itunes  # noqa: E402

raiz = Path(sys.argv[1])


def play(appid):
    try:
        d = app(appid, lang="es", country="mx")
        return {k: d.get(k) for k in PLAY_CAMPOS}
    except NotFoundError:
        return {"no_encontrada": True}
    except Exception as e:  # red, rate limit: se reporta, no se inventa
        return {"error": repr(e)}


def ios(trackid):
    for intento in range(5):  # iTunes devuelve 429 con facilidad
        try:
            r = itunes("lookup", id=trackid)
            time.sleep(1.5)
            return {k: r[0].get(k) for k in IOS_CAMPOS} if r else {"no_encontrada": True}
        except Exception as e:
            err = e
            time.sleep(15 * (intento + 1))
    return {"error": repr(err)}


apps, vistos = [], {}
for f in sorted((raiz / "segmentos").glob("*.json")):
    for a in json.loads(f.read_text()):
        a["segmento"] = f.stem
        a["android_id"] = a.get("android_id") or None
        a["ios_id"] = str(a["ios_id"]) if a.get("ios_id") else None
        clave = a["android_id"] or a["ios_id"] or (a["nombre"].lower(), a.get("estado"))
        if clave in vistos:  # misma app reportada por dos segmentos
            vistos[clave].setdefault("tambien_en", []).append(f.stem)
            continue
        vistos[clave] = a
        apps.append(a)

with ThreadPoolExecutor(8) as ex:
    p = list(ex.map(lambda a: play(a["android_id"]) if a["android_id"] else None, apps))
i = [ios(a["ios_id"]) if a["ios_id"] else None for a in apps]  # ponytail: serial por rate limit de iTunes
for a, pp, ii in zip(apps, p, i):
    a["play"], a["appstore"] = pp, ii

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

malos = [(a["nombre"], k) for a in apps for k in ("play", "appstore") if a[k] and ("error" in a[k] or "no_encontrada" in a[k])]
print(f"{len(apps)} apps únicas; {sum(bool(a['android_id']) for a in apps)} Android, "
      f"{sum(bool(a['ios_id']) for a in apps)} iOS; {len(malos)} IDs con error/no encontrados")
for m in malos:
    print("  !", *m)
