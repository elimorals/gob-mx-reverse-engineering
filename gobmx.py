#!/usr/bin/env python3
"""gobmx — consulta el inventario de presencia digital del gobierno de México.

uso:
  gobmx apps [--nivel N] [--estado E] [--sector S] [--estatus T] [--busca TXT] [--json]
  gobmx sitios [--nivel N] [--estado E] [--busca TXT] [--json]
  gobmx servicios [--busca TXT] [--json]
  gobmx stats                      # resumen por nivel/sector/estatus
  gobmx dep "<dependencia>"        # todo (apps+sitios) de una dependencia

Lee los JSON junto a este archivo. Sin dependencias externas.
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def cargar(sub):
    out = []
    d = RAIZ / sub
    for f in sorted(d.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            out += data if isinstance(data, list) else [data]
        except (ValueError, OSError):
            pass
    return out


def apps():
    # apps.json consolidado si existe; si no, los segmentos
    j = RAIZ / "apps/apps.json"
    return json.loads(j.read_text()) if j.exists() else cargar("apps/inventario")


def filtra(items, args, campos_busca):
    def ok(i):
        for k in ("nivel", "estado", "sector", "estatus"):
            v = getattr(args, k, None)
            if v and v.lower() not in str(i.get(k, "")).lower():
                return False
        if args.busca:
            blob = " ".join(str(i.get(c, "")) for c in campos_busca).lower()
            if args.busca.lower() not in blob:
                return False
        return True
    return [i for i in items if ok(i)]


def imprime(items, args, cols):
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=1))
        return
    print(f"{len(items)} resultados\n")
    for i in items:
        linea = "  ".join(str(i.get(c, "") or "·") for c in cols)
        print("•", linea)


def cmd_apps(args):
    items = filtra(apps(), args, ["nombre", "dependencia", "siglas", "proposito"])
    imprime(items, args, ["nombre", "siglas", "nivel", "estado", "sector", "estatus", "android_id"])


def cmd_sitios(args):
    items = filtra(cargar("sitios"), args, ["dependencia", "siglas", "url", "proposito"])
    imprime(items, args, ["siglas", "dependencia", "nivel", "estado", "url"])


def cmd_servicios(args):
    items = filtra(cargar("servicios"), args, ["servicio", "dependencia", "brecha"])
    imprime(items, args, ["servicio", "nivel", "estado", "brecha"])


def cmd_stats(args):
    from collections import Counter
    a, s = apps(), cargar("sitios")
    print(f"APPS: {len(a)}  |  SITIOS: {len(s)}  |  SERVICIOS: {len(cargar('servicios'))}\n")
    for campo in ("nivel", "sector", "estatus"):
        c = Counter((x.get(campo) or "—") for x in a)
        print(f"apps por {campo}:", dict(c.most_common()))
    print("apps con Android:", sum(bool(x.get("android_id")) for x in a),
          "| con iOS:", sum(bool(x.get("ios_id")) for x in a))


def cmd_dep(args):
    t = args.texto.lower()
    a = [x for x in apps() if t in str(x.get("dependencia", "")).lower() or t in str(x.get("siglas", "")).lower()]
    s = [x for x in cargar("sitios") if t in str(x.get("dependencia", "")).lower() or t in str(x.get("siglas", "")).lower()]
    print(f"== {args.texto} ==\nApps ({len(a)}):")
    for x in a:
        print("  •", x.get("nombre"), "—", x.get("android_id") or x.get("ios_id") or "sin ID")
    print(f"Sitios ({len(s)}):")
    for x in s:
        print("  •", x.get("url"), "—", x.get("tipo"))


def main():
    p = argparse.ArgumentParser(prog="gobmx", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nombre, fn in [("apps", cmd_apps), ("sitios", cmd_sitios), ("servicios", cmd_servicios)]:
        sp = sub.add_parser(nombre)
        sp.add_argument("--nivel"); sp.add_argument("--estado"); sp.add_argument("--sector")
        sp.add_argument("--estatus"); sp.add_argument("--busca"); sp.add_argument("--json", action="store_true")
        sp.set_defaults(fn=fn)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    dp = sub.add_parser("dep"); dp.add_argument("texto"); dp.set_defaults(fn=cmd_dep)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
