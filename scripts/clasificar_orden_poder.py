"""Clasifica cada app, sitio y servicio por orden de gobierno y poder (contrato de la rama
feat/orden-poder-comparacion-presupuesto). Idempotente: solo agrega campos que faltan.

Campos que agrega (además de `nivel`, que se conserva):
  orden      federal | estatal | municipal            (null solo si nivel=no_oficial)
  poder      ejecutivo | legislativo | judicial | autonomo   (null solo si nivel=no_oficial)
  subtipo    null | paraestatal | desconcentrado | universidad_autonoma | extinto
  municipio  nombre oficial INEGI cuando orden=municipal; si no, null
  nota_clasificacion   (solo cuando la regla aplicada merece explicación: casos dudosos)

Orden de reglas: EXCEPCIONES explícitas → nivel poder_* → patrones de nombre → tabla de
fiscalías estatales → nivel autonomo → ejecutivo. Recorre apps/inventario/*.json, sitios/*.json,
servicios/brechas.json y servicios/catalogo-conamer.json (cualquier JSON nuevo en esas carpetas
también, p.ej. poderes-autonomos.json). cnts-federal.json NO se reescribe: gobmx.servicios() le
aplica `clasificar()` al cargar.

uso: python3 -I scripts/clasificar_orden_poder.py [--forzar] [--revisar]
  --forzar   recalcula aunque el registro ya tenga los campos (pierde ediciones a mano)
  --revisar  imprime la tabla (orden, poder, subtipo) × conteo y todos los no-ejecutivos
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from gobmx import ENTIDADES  # noqa: E402

# --- Fiscalías / procuradurías estatales: ¿autonomía constitucional? -------------------------
# Verificado el 2026-10-21 con búsqueda web. Fuentes:
#  [J] La Jornada 2022-08-03, cita a funcionaria de la FGR: Campeche, Chihuahua, Durango y Yucatán
#      dependen del Ejecutivo; BCS, Hidalgo y Tlaxcala no habían transitado de procuraduría a fiscalía.
#      https://www.jornada.com.mx/2022/08/03/politica/010n3pol
#  [E] Este País, "El gran dilema de la autonomía en las fiscalías": designación directa por el
#      Ejecutivo en Campeche, Chihuahua, Coahuila y Durango. https://estepais.com/tendencias_y_opiniones/impunidad-cero/dilema-autonomia-fiscalias/
#  [L] Ley Orgánica de la Fiscalía del Estado de Jalisco (decreto 27214/LXII/18): la define como
#      "dependencia"; nació en 2013 de la fusión con la Procuraduría dentro de la administración centralizada.
#  [S] SciELO 2024, fiscalías anticorrupción estatales: la de Chihuahua tiene autonomía constitucional.
#      https://www.scielo.org.mx/scielo.php?script=sci_arttext_plus&pid=S2594-00822024000200073
#  [C] conocimiento general (constitución local reformada 2014-2021 para crear fiscalía autónoma);
#      no se cruzó con la constitución local vigente.
# Solo afecta a registros cuyo nombre de dependencia es una fiscalía/procuraduría de justicia.
FISCALIAS = {
    "Aguascalientes": ("autonomo", "[C] FGE órgano constitucional autónomo"),
    "Baja California": ("autonomo", "[C] FGE autónoma desde 2020"),
    "Baja California Sur": ("ejecutivo", "[J] sigue siendo Procuraduría General de Justicia, dependiente del Ejecutivo"),
    "Campeche": ("ejecutivo", "[J][E] FGE dependiente del Ejecutivo"),
    "Chiapas": ("autonomo", "[C] FGE órgano autónomo (constitución 2016)"),
    "Chihuahua": ("ejecutivo", "[J][E] FGE dependencia del Ejecutivo (la Fiscalía Anticorrupción sí es autónoma [S])"),
    "Ciudad de México": ("autonomo", "[C] FGJ autónoma desde 2020"),
    "Coahuila": ("autonomo", "[C][E] autónoma en la constitución local, pero designación por el Ejecutivo: dudoso"),
    "Colima": ("autonomo", "[C]"),
    "Durango": ("ejecutivo", "[J][E] dependiente del Ejecutivo"),
    "Estado de México": ("autonomo", "[C] FGJEM autónoma desde 2016"),
    "Guanajuato": ("autonomo", "[C] FGE autónoma desde 2019"),
    "Guerrero": ("autonomo", "[C] FGE órgano autónomo (constitución 2014)"),
    "Hidalgo": ("ejecutivo", "[J] sigue siendo Procuraduría General de Justicia, dependiente del Ejecutivo"),
    "Jalisco": ("ejecutivo", "[L] la ley orgánica la define como dependencia del Ejecutivo"),
    "Michoacán": ("autonomo", "[C]"),
    "Morelos": ("autonomo", "[C]"),
    "Nayarit": ("autonomo", "[C]"),
    "Nuevo León": ("autonomo", "[C] FGJ autónoma desde 2017"),
    "Oaxaca": ("autonomo", "[C] FGEO autónoma desde 2015"),
    "Puebla": ("autonomo", "[C]"),
    "Querétaro": ("autonomo", "[C]"),
    "Quintana Roo": ("autonomo", "[C]"),
    "San Luis Potosí": ("autonomo", "[C]"),
    "Sinaloa": ("autonomo", "[C]"),
    "Sonora": ("autonomo", "[C] FGJE autónoma desde 2017"),
    "Tabasco": ("autonomo", "[C]"),
    "Tamaulipas": ("autonomo", "[C]"),
    "Tlaxcala": ("autonomo", "[C] FGJ creada en 2021; [J] la daba como procuraduría en 2022: dudoso"),
    "Veracruz": ("autonomo", "[C] FGE autónoma desde 2015"),
    "Yucatán": ("ejecutivo", "[J] dependiente del Ejecutivo; otra fuente 2024 la da como autónoma: dudoso"),
    "Zacatecas": ("autonomo", "[C]"),
}
RE_FISCALIA = re.compile(r"Fiscal[ií]a General|Fiscal[ií]a del Estado|Procuradur[ií]a General de Justicia", re.I)

# --- Excepciones explícitas (substring de dependencia → campos). Ganan sobre todo lo demás. ---
EXCEPCIONES = [
    ("Fiscalía Anticorrupción del Estado de Chihuahua",
     {"poder": "autonomo", "nota_clasificacion": "fiscalía anticorrupción con autonomía constitucional (SciELO 2024)"}),
    ("Secretaría de Seguridad del Pueblo y Fiscalía General del Estado de Chiapas",
     {"poder": "ejecutivo", "nota_clasificacion": "app copublicada; se asigna al titular principal (SSP, Ejecutivo)"}),
    ("Poder Judicial del Estado de Coahuila de Zaragoza / Secretaría de Seguridad",
     {"poder": "judicial", "nota_clasificacion": "anunciada por el PJECZ y entregada a la SSP estatal; se asigna al Judicial"}),
    ("Comisión Federal de Competencia Económica",
     {"poder": "autonomo", "subtipo": "extinto",
      "nota_clasificacion": "reforma de autónomos 2024-2025: COFECE sustituida por la Comisión Nacional Antimonopolio"}),
    ("Plataforma Nacional de Transparencia",
     {"poder": "ejecutivo", "nota_clasificacion": "la operaba el INAI (extinto); hoy la Secretaría Anticorrupción y Buen Gobierno"}),
    ("Instituto Politécnico Nacional", {"poder": "ejecutivo", "subtipo": "desconcentrado"}),
    ("Consejo de la Judicatura Federal",
     {"poder": "judicial", "nota_clasificacion": "CJF sustituido por el Órgano de Administración Judicial (reforma 2024-2025)"}),
    ("Denuncia ciudadana / fiscalía en línea",
     {"poder": "autonomo", "nota_clasificacion": "brecha agregada de varias fiscalías; la mayoría son autónomas, no verificable caso a caso"}),
]

# --- Patrones de nombre de dependencia → poder ---
PATRONES_PODER = [
    ("judicial", r"Poder Judicial|Tribunal Superior de Justicia|Suprema Corte|Judicatura|"
                 r"Órgano de Administración Judicial|Tribunal de Disciplina Judicial"),
    ("legislativo", r"Congreso del Estado|Congreso de la Ciudad|H\. Congreso|Cámara de Diputados|Senado de la República|"
                    r"Legislatura|Auditoría Superior|Órgano Superior de Fiscalización"),
    ("autonomo", r"Instituto (Estatal )?Electoral|Instituto Nacional Electoral|Organismo Público Local Electoral|"
                 r"Tribunal Electoral (?!del Poder Judicial)|Derechos Humanos|Universidad Autónoma|Universidad Nacional Autónoma|"
                 r"Banco de México|Instituto Nacional de Estadística|Fiscalía General de la República|"
                 r"Instituto (de|para la) Transparencia|Instituto de Acceso a la Información|Órgano Garante|"
                 r"Tribunal (Federal )?de Justicia Administrativa|Tribunal de lo Contencioso|Tribunal (Federal )?de Conciliación|"
                 r"Tribunal Laboral"),
]
NOTA_TRIBUNAL_ADM = "tribunal administrativo/laboral: autónomo por regla del contrato (no es Poder Judicial)"

# --- Subtipo (solo para poder ejecutivo) ---
RE_PARAESTATAL = re.compile(
    r"S\.A\.|S\.N\.C\.|Fideicomiso|Fondo Nacional|Instituto Mexicano del Seguro Social|Seguridad y Servicios Sociales|"
    r"Seguridad Social para las Fuerzas Armadas|Comisión Federal de Electricidad|\bCFE\b|Petróleos Mexicanos|Pemex|"
    r"Liconsa|Diconsa|Telecomunicaciones de México|Infonavit|Lotería Nacional|Banco|Financiera|Aeropuerto|Aerolínea|"
    r"Tren Maya|Comisión Nacional para la Protección y Defensa de los Usuarios|Procuraduría Federal del Consumidor|"
    r"Instituto Mexicano de la Propiedad Industrial|Comisión Nacional de Vivienda|Servicio Postal Mexicano|"
    r"Consejo Nacional de Fomento Educativo|Sistema Nacional para el Desarrollo Integral|Comisión Nacional de Libros de Texto|"
    r"Servicio Geológico Mexicano|Instituto Mexicano de la Juventud|"
    r"Comisión Estatal de Servicios Públicos|Comisión Estatal de Aguas|Sistema de Agua Potable|Agua de Hermosillo|"
    r"organismo operador", re.I)
RE_DESCONCENTRADO = re.compile(
    r"Servicio de Administración Tributaria|Comisión Federal para la Protección contra Riesgos Sanitarios|"
    r"Comisión Nacional Bancaria|Comisión Nacional de Seguros y Fianzas|Comisión Nacional del Sistema de Ahorro|"
    r"Comisión Nacional del Agua|Servicio Nacional de Sanidad|Servicio de Información Agroalimentaria|"
    r"Secretariado Ejecutivo del Sistema Nacional de Seguridad|Instituto Nacional de Migración|"
    r"Instituto Nacional del Derecho de Autor|Instituto Nacional de Antropología|Instituto Nacional de Bellas Artes|"
    r"Agencia de Seguridad, Energía y Ambiente|Agencia Nacional de Aduanas|Comisión Nacional de Acuacultura|"
    r"Registro Agrario Nacional|Comisión Nacional de Áreas Naturales")

# --- Municipios: nombre oficial INEGI por entidad, con alias que aparecen en las dependencias ---
MUNICIPIOS = {
    "Aguascalientes": {"Aguascalientes": ["Aguascalientes"]},
    "Baja California": {"Mexicali": ["Mexicali"], "Tijuana": ["Tijuana"]},
    "Chihuahua": {"Juárez": ["Juárez", "Ciudad Juárez"], "Chihuahua": ["Chihuahua"]},
    "Coahuila": {"Saltillo": ["Saltillo"], "Torreón": ["Torreón"]},
    "Estado de México": {"Ecatepec de Morelos": ["Ecatepec"], "Toluca": ["Toluca"],
                         "Naucalpan de Juárez": ["Naucalpan"]},
    "Guanajuato": {"León": ["León"]},
    "Jalisco": {"Guadalajara": ["Guadalajara"], "Zapopan": ["Zapopan"], "Tlajomulco de Zúñiga": ["Tlajomulco"]},
    "Michoacán": {"Morelia": ["Morelia"]},
    "Nuevo León": {"Monterrey": ["Monterrey"], "San Nicolás de los Garza": ["San Nicolás"],
                   "San Pedro Garza García": ["San Pedro Garza García", "San Pedro"], "Apodaca": ["Apodaca"]},
    "Puebla": {"Puebla": ["Puebla"]},
    "Querétaro": {"Querétaro": ["Querétaro"]},
    "Quintana Roo": {"Benito Juárez": ["Benito Juárez", "Cancún"]},
    "San Luis Potosí": {"San Luis Potosí": ["San Luis Potosí"]},
    "Sinaloa": {"Culiacán": ["Culiacán"]},
    "Sonora": {"Hermosillo": ["Hermosillo"]},
    "Yucatán": {"Mérida": ["Mérida"]},
}


def municipio_de(r):
    """Nombre oficial del municipio buscando sus alias en dependencia, nombre y url (alias más largo gana)."""
    tabla = MUNICIPIOS.get(r.get("estado"), {})
    for campo in ("dependencia", "nombre", "servicio", "url"):
        txt = str(r.get(campo) or "")
        hits = [(len(a), m) for m, alias in tabla.items() for a in alias if a.lower() in txt.lower()]
        if hits:
            return max(hits)[1]
    return None


def clasificar(r):
    """Devuelve {orden, poder, subtipo, municipio[, nota_clasificacion]} para un registro."""
    nivel = r.get("nivel")
    dep = str(r.get("dependencia") or r.get("servicio") or "")
    estado = r.get("estado")
    if nivel == "no_oficial":
        return {"orden": None, "poder": None, "subtipo": None, "municipio": None}
    if nivel == "municipal":
        orden = "municipal"
    elif nivel in ("federal", "paraestatal") or not estado or estado == "Nacional":
        orden = "federal"
    else:
        orden = "estatal"  # incluye agregados ('todos', 'mayoría', 'varios'): no son una entidad

    out = {"orden": orden, "poder": None, "subtipo": None, "municipio": None}
    for clave, campos in EXCEPCIONES:
        if clave in dep:
            out.update(campos)
            break
    if out["poder"] is None:
        if nivel == "poder_judicial":
            out["poder"] = "judicial"
        elif nivel == "poder_legislativo":
            out["poder"] = "legislativo"
    if out["poder"] is None:
        for poder, pat in PATRONES_PODER:
            m = re.search(pat, dep)
            if m:
                out["poder"] = poder
                if "Tribunal" in m.group(0) and poder == "autonomo" and "Electoral" not in m.group(0):
                    out["nota_clasificacion"] = NOTA_TRIBUNAL_ADM
                break
    if out["poder"] is None and orden != "federal" and RE_FISCALIA.search(dep):
        p, nota = FISCALIAS.get(estado, ("autonomo", "entidad sin verificar: autónomo por default del contrato"))
        out["poder"], out["nota_clasificacion"] = p, f"fiscalía estatal: {nota}"
    if out["poder"] is None:
        out["poder"] = "autonomo" if nivel == "autonomo" else "ejecutivo"

    if out["subtipo"] is None:
        if re.search(r"extint", dep, re.I):
            out["subtipo"] = "extinto"
        elif re.search(r"Universidad (Nacional )?Autónoma", dep):
            out["subtipo"] = "universidad_autonoma"
        elif out["poder"] == "ejecutivo":
            if nivel == "paraestatal" or RE_PARAESTATAL.search(dep):
                out["subtipo"] = "paraestatal"
            elif orden == "federal" and RE_DESCONCENTRADO.search(dep):
                out["subtipo"] = "desconcentrado"
    if orden == "municipal":
        out["municipio"] = municipio_de(r)
    return out


def con_campos(r, nuevos):
    """Inserta los campos nuevos justo después de `estado` (diff local y legible)."""
    out = {}
    for k, v in r.items():
        if k not in nuevos:
            out[k] = v
        if k == "estado":
            out.update(nuevos)
    if not any(k in out for k in nuevos):
        out.update(nuevos)
    return out


# --- escritura conservando el formato de cada archivo ---
def _por_linea(d):
    return "[\n" + ",\n".join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in d) + "\n]"


def _inline(n):
    def f(d):
        p = " " * n
        return "[\n" + ",\n".join(
            p + "{\n" + ",\n".join(f"{p}{p}{json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}"
                                   for k, v in o.items()) + "\n" + p + "}" for o in d) + "\n]"
    return f


FORMATOS = [_por_linea, lambda d: json.dumps(d, ensure_ascii=False, indent=1),
            lambda d: json.dumps(d, ensure_ascii=False, indent=2), _inline(1), _inline(2)]


def formato_de(texto, datos):
    for fmt in FORMATOS:
        if fmt(datos) == texto.rstrip("\n"):
            return fmt
    lineas = texto.splitlines()
    sangria = len(lineas[1]) - len(lineas[1].lstrip()) if len(lineas) > 1 else 1
    return _por_linea if sangria == 0 else _inline(sangria or 1)


def archivos():
    yield from sorted((RAIZ / "apps/inventario").glob("*.json"))
    yield from sorted((RAIZ / "sitios").glob("*.json"))
    for n in ("brechas.json", "catalogo-conamer.json"):
        if (RAIZ / "servicios" / n).exists():
            yield RAIZ / "servicios" / n


def main(argv):
    forzar, revisar = "--forzar" in argv, "--revisar" in argv
    tabla, no_ejec, sin_mun, cambiados = Counter(), [], [], 0
    for f in archivos():
        texto = f.read_text()
        datos = json.loads(texto)
        fmt = formato_de(texto, datos)
        nuevos_datos, toco = [], False
        for r in datos:
            calc = clasificar(r)
            if forzar:
                r = {k: v for k, v in r.items() if k != "nota_clasificacion"}
            if "poder" in r and not forzar:
                calc.pop("nota_clasificacion", None)  # la nota solo acompaña a un poder calculado aquí
            faltan = {k: v for k, v in calc.items() if forzar or k not in r}
            if faltan:
                r, toco = con_campos(r, faltan), True
            nuevos_datos.append(r)
            tabla[(f.parent.name if f.parent.name != "inventario" else "apps", r.get("orden"), r.get("poder"),
                   r.get("subtipo"))] += 1
            if r.get("poder") != "ejecutivo":
                no_ejec.append((f.relative_to(RAIZ), r))
            if r.get("orden") == "municipal" and not r.get("municipio"):
                sin_mun.append((f.relative_to(RAIZ), r))
        if toco:
            f.write_text(fmt(nuevos_datos) + "\n")
            cambiados += 1
    print(f"archivos reescritos: {cambiados}")
    if revisar:
        print("\n(capa, orden, poder, subtipo) × conteo")
        for k, v in sorted(tabla.items(), key=lambda t: tuple(str(x) for x in t[0])):
            print(f"  {v:>4}  {' | '.join(str(x) for x in k)}")
        print(f"\nNO-EJECUTIVOS ({len(no_ejec)}):")
        for f, r in no_ejec:
            print(f"  {r.get('orden')}/{r.get('poder')}/{r.get('subtipo')}  {r.get('estado')}  "
                  f"{r.get('nombre') or r.get('url') or r.get('servicio')} — {r.get('dependencia') or ''}"
                  f"{'  ['+r['nota_clasificacion']+']' if r.get('nota_clasificacion') else ''}  ({f})")
        print(f"\nMUNICIPALES SIN MUNICIPIO ({len(sin_mun)}):")
        for f, r in sin_mun:
            print(f"  {r.get('estado')}  {r.get('dependencia') or r.get('servicio')} ({f})")


def _autoprueba():
    c = clasificar
    assert c({"nivel": "estatal", "estado": "Yucatán", "dependencia": "Poder Judicial del Estado de Yucatán"})["poder"] == "judicial"
    assert c({"nivel": "autonomo", "estado": "Nacional", "dependencia": "Tribunal Electoral del Poder Judicial de la Federación"}) \
        == {"orden": "federal", "poder": "judicial", "subtipo": None, "municipio": None}
    assert c({"nivel": "estatal", "estado": "Chihuahua", "dependencia": "Instituto Estatal Electoral de Chihuahua"})["poder"] == "autonomo"
    assert c({"nivel": "estatal", "estado": "Oaxaca", "dependencia": "Fiscalía General del Estado de Oaxaca"})["poder"] == "autonomo"
    assert c({"nivel": "estatal", "estado": "Jalisco", "dependencia": "Fiscalía General del Estado de Jalisco"})["poder"] == "ejecutivo"
    assert c({"nivel": "federal", "estado": "Nacional", "dependencia": "Instituto Mexicano del Seguro Social"})["subtipo"] == "paraestatal"
    assert c({"nivel": "autonomo", "estado": "Nacional", "dependencia": "Universidad Nacional Autónoma de México"})["subtipo"] == "universidad_autonoma"
    assert c({"nivel": "autonomo", "estado": "Nacional", "dependencia": "Instituto Federal de Telecomunicaciones (EXTINTO)"})["subtipo"] == "extinto"
    assert c({"nivel": "no_oficial", "estado": "Nacional", "dependencia": "(no oficial) Correos"})["poder"] is None
    m = c({"nivel": "municipal", "estado": "Quintana Roo", "dependencia": "Ayuntamiento de Benito Juárez (Cancún)"})
    assert (m["orden"], m["poder"], m["municipio"]) == ("municipal", "ejecutivo", "Benito Juárez")
    assert c({"nivel": "municipal", "estado": "Estado de México", "dependencia": "Naucalpan de Juárez"})["municipio"] == "Naucalpan de Juárez"
    assert c({"nivel": "estatal", "estado": "Nuevo León", "dependencia": "Congreso del Estado de Nuevo León"})["poder"] == "legislativo"
    assert set(FISCALIAS) == set(ENTIDADES), "la tabla de fiscalías debe cubrir las 32 entidades"
    print("autoprueba del clasificador: OK")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _autoprueba()
    else:
        main(sys.argv[1:])
