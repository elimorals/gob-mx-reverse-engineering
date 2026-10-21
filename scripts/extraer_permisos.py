"""Extiende la capa de permisos a TODAS las apps con android_id. Resumible.

Preserva las entradas ya curadas (no las sobrescribe); para las nuevas clasifica los permisos
peligrosos a partir de los grupos que publica Google Play. Fuente: google-play (es). Sin APK.
uso: .venv/bin/python -I scripts/extraer_permisos.py [raíz]
Guarda incrementalmente en apps/permisos/permisos.json, así que se puede cortar y reanudar.
"""
import json
import sys
import time
from pathlib import Path

from google_play_scraper import permissions

RAIZ = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "apps/permisos/permisos.json"


def peligrosos(grupos):
    """Grupos de Google Play (es) -> lista de permisos peligrosos de Android (constantes)."""
    out = []
    for g, descs in grupos.items():
        d = " ".join(descs).lower()
        gl = g.lower()
        if "ubicaci" in gl:
            if "precisa" in d or "gps" in d:
                out.append("ACCESS_FINE_LOCATION")
            if "aproximada" in d or "red" in d:
                out.append("ACCESS_COARSE_LOCATION")
            if not descs:
                out.append("ACCESS_COARSE_LOCATION")
        elif "cámara" in gl or "camara" in gl:
            out.append("CAMERA")
        elif "micrófono" in gl or "microfono" in gl:
            out.append("RECORD_AUDIO")
        elif "contacto" in gl:
            out.append("WRITE_CONTACTS" if "modificar" in d else "READ_CONTACTS")
            if "leer" in d and "modificar" in d:
                out.append("READ_CONTACTS")
        elif "teléfono" in gl or "telefono" in gl:
            if "llamar" in d:
                out.append("CALL_PHONE")
            if "estado" in d or "identidad" in d:
                out.append("READ_PHONE_STATE")
            if "llamar" not in d and "estado" not in d:
                out.append("READ_PHONE_STATE")
        elif "sms" in gl or "mensaje" in gl:
            if "enviar" in d:
                out.append("SEND_SMS")
            if "recibir" in d:
                out.append("RECEIVE_SMS")
            if "leer" in d:
                out.append("READ_SMS")
        elif "calendario" in gl:
            out.append("READ_CALENDAR")
            if "añadir" in d or "modificar" in d or "escribir" in d:
                out.append("WRITE_CALENDAR")
        elif "almacenamiento" in gl or ("fotos" in gl and "archivos" in gl) or "multimedia" in gl:
            out.append("READ_EXTERNAL_STORAGE")
            if "modificar" in d or "eliminar" in d or "escribir" in d:
                out.append("WRITE_EXTERNAL_STORAGE")
        elif "sensores corporales" in gl:
            out.append("BODY_SENSORS")
        elif "registro de llamadas" in gl:
            out.append("READ_CALL_LOG")
        elif "identidad" in gl or "cuentas" in gl:
            out.append("GET_ACCOUNTS")
    # dedup preservando orden
    return sorted(set(out))


def pide(aid):
    for intento in range(4):
        try:
            return permissions(aid, lang="es", country="mx")
        except TypeError:
            time.sleep(3 * (intento + 1))  # bug intermitente de la librería
        except Exception:
            return None
    return None


def meta_app(a):
    return {"nombre": a.get("nombre"), "dependencia": a.get("dependencia"), "siglas": a.get("siglas"),
            "nivel": a.get("nivel"), "estado": a.get("estado"), "sector": a.get("sector"),
            "instalaciones": (a.get("play") or {}).get("realInstalls")}


def main():
    apps = json.loads((RAIZ / "apps/apps.json").read_text())
    por_aid = {a["android_id"]: a for a in apps if a.get("android_id")}
    existentes = {p["android_id"]: p for p in json.loads(SALIDA.read_text())} if SALIDA.exists() else {}
    # backfill nivel/estado/siglas en las ya curadas, sin tocar su análisis
    for aid, p in existentes.items():
        a = por_aid.get(aid)
        if a:
            p.setdefault("nivel", a.get("nivel"))
            p.setdefault("estado", a.get("estado"))
            p.setdefault("siglas", a.get("siglas"))
    # no re-consultar las ya curadas (fuente incluye google-play y tienen permisos_total)
    hechas = {k for k, v in existentes.items() if v.get("permisos_total") is not None}

    objetivo = [(a["android_id"], a) for a in apps if a.get("android_id") and a["android_id"] not in hechas]
    print(f"{len(apps)} apps | {len(hechas)} ya hechas | {len(objetivo)} por consultar")

    res = dict(existentes)
    nuevas = fallidas = 0
    for i, (aid, a) in enumerate(objetivo, 1):
        g = pide(aid)
        base = {**meta_app(a), "android_id": aid, "trackers": [], "fuente": ["google-play"], "fecha": "2026-10-21"}
        if g is None:
            res[aid] = {**base, "permisos_total": None, "permisos_peligrosos": [],
                        "notas": "Google Play no devolvió la sección de permisos al 2026-10-21."}
            fallidas += 1
        else:
            res[aid] = {**base, "permisos_total": sum(len(v) for v in g.values()),
                        "permisos_peligrosos": peligrosos(g),
                        "notas": "Permisos de Google Play (es). Clasificación mecánica de peligrosos; "
                                 "trackers no verificados (Exodus requiere token)."}
            nuevas += 1
        time.sleep(1.6)
        if i % 20 == 0:
            SALIDA.write_text(json.dumps(sorted(res.values(), key=lambda x: -(x.get("instalaciones") or 0)),
                                         ensure_ascii=False, indent=1))
            print(f"  {i}/{len(objetivo)} (nuevas {nuevas}, fallidas {fallidas})")

    SALIDA.write_text(json.dumps(sorted(res.values(), key=lambda x: -(x.get("instalaciones") or 0)),
                                 ensure_ascii=False, indent=1))
    print(f"listo: {len(res)} apps con capa de permisos (nuevas {nuevas}, fallidas {fallidas})")


if __name__ == "__main__":
    main()
