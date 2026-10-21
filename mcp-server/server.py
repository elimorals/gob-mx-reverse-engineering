"""MCP server del inventario de presencia digital del gobierno de México.

Expone como tools el mismo inventario que consulta el CLI gobmx.py (apps, sitios,
servicios, subdominios). Solo lectura sobre los JSON/CSV del repo.

Correr:  uv run --no-project --with "mcp<2" python mcp-server/server.py
"""
import csv
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import gobmx  # noqa: E402  (reusa cargar()/apps() del CLI)

mcp = FastMCP("gobmx-inventario")


def _filtra(items, nivel=None, estado=None, sector=None, estatus=None, texto=None, campos=()):
    def ok(i):
        for k, v in (("nivel", nivel), ("estado", estado), ("sector", sector), ("estatus", estatus)):
            if v and v.lower() not in str(i.get(k, "")).lower():
                return False
        if texto:
            blob = " ".join(str(i.get(c, "")) for c in campos).lower()
            if texto.lower() not in blob:
                return False
        return True
    return [i for i in items if ok(i)]


@mcp.tool()
def stats() -> dict:
    """Resumen del inventario: totales y conteos por nivel, sector y estatus."""
    from collections import Counter
    a, s = gobmx.apps(), gobmx.cargar("sitios")
    return {
        "apps": len(a), "sitios": len(s), "servicios": len(gobmx.cargar("servicios")),
        "permisos": len(gobmx.permisos()),
        "apps_por_nivel": dict(Counter((x.get("nivel") or "—") for x in a).most_common()),
        "apps_por_sector": dict(Counter((x.get("sector") or "—") for x in a).most_common()),
        "apps_por_estatus": dict(Counter((x.get("estatus") or "—") for x in a).most_common()),
        "apps_con_android": sum(bool(x.get("android_id")) for x in a),
        "apps_con_ios": sum(bool(x.get("ios_id")) for x in a),
    }


@mcp.tool()
def buscar_apps(nivel: str = "", estado: str = "", sector: str = "", estatus: str = "",
                texto: str = "", limite: int = 50) -> list:
    """Busca apps. Filtros opcionales: nivel (federal/estatal/municipal/paraestatal/autonomo),
    estado (entidad), sector (seguridad/movilidad/salud/fiscal/identidad...), estatus
    (activa/retirada/'sin actualizar >2 años'), texto (nombre/dependencia/propósito)."""
    r = _filtra(gobmx.apps(), nivel, estado, sector, estatus, texto,
                campos=("nombre", "dependencia", "siglas", "proposito"))
    return r[:limite]


@mcp.tool()
def buscar_sitios(nivel: str = "", estado: str = "", texto: str = "", limite: int = 50) -> list:
    """Busca portales web de gobierno. Filtros: nivel, estado, texto (dependencia/url/propósito)."""
    r = _filtra(gobmx.cargar("sitios"), nivel, estado, None, None, texto,
                campos=("dependencia", "siglas", "url", "proposito"))
    return r[:limite]


@mcp.tool()
def buscar_servicios(texto: str = "", limite: int = 50) -> list:
    """Busca trámites/servicios (incluye catálogo CONAMER y brechas). texto busca en nombre/dependencia."""
    r = _filtra(gobmx.cargar("servicios"), texto=texto,
                campos=("servicio", "nombre_tramite", "dependencia", "brecha", "siglas"))
    return r[:limite]


@mcp.tool()
def dependencia(nombre: str) -> dict:
    """Todo lo de una dependencia: sus apps (con permisos si los hay) y sus sitios.
    'nombre' hace match en dependencia o siglas."""
    t = nombre.lower()
    perm = {p.get("android_id"): p for p in gobmx.permisos()}
    def m(x):
        return t in str(x.get("dependencia", "")).lower() or t in str(x.get("siglas", "")).lower()
    aps = []
    for x in gobmx.apps():
        if m(x):
            x = dict(x)
            if x.get("android_id") in perm:
                x["permisos"] = perm[x["android_id"]]
            aps.append(x)
    return {"apps": aps, "sitios": [x for x in gobmx.cargar("sitios") if m(x)]}


@mcp.tool()
def permisos(texto: str = "", limite: int = 50) -> list:
    """Análisis de permisos y privacidad de apps (piloto). Cada entrada trae
    permisos_peligrosos, trackers (si hay) y notas de qué no cuadra con el propósito.
    'texto' hace match en nombre/dependencia/android_id."""
    out = []
    for p in gobmx.permisos():
        if texto:
            blob = f"{p.get('nombre','')} {p.get('dependencia','')} {p.get('android_id','')}".lower()
            if texto.lower() not in blob:
                continue
        out.append(p)
        if len(out) >= limite:
            break
    return out


@mcp.tool()
def buscar_subdominio(texto: str = "", solo_activos: bool = False, limite: int = 100) -> list:
    """Busca en los 12k+ subdominios .gob.mx consolidados (CT + dotgob-mx).
    'texto' hace match en el host; 'solo_activos' filtra los marcados activos por dotgob-mx."""
    f = ROOT / "sitios/subdominios-consolidado.csv"
    if not f.exists():
        return []
    out = []
    with f.open() as fh:
        for row in csv.DictReader(fh):
            if texto and texto.lower() not in row["host"].lower():
                continue
            if solo_activos and not str(row.get("activo_dotgob", "")).startswith("activo"):
                continue
            out.append(row)
            if len(out) >= limite:
                break
    return out


if __name__ == "__main__":
    mcp.run()
