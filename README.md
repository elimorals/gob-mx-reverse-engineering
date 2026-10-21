# gobmx-presencia-digital

Inventario y análisis de la **presencia digital del Estado mexicano**: aplicaciones
móviles, sitios web y servicios en línea de dependencias federales, organismos
autónomos, paraestatales, los tres poderes, estados y municipios.

Todo se construye con **observación pasiva** de fuentes públicas (tiendas de apps,
Certificate Transparency, páginas públicas) y búsqueda web. No hay escaneo intrusivo,
ni login con credenciales ajenas, ni envío de datos personales.

🔗 **Dashboard en vivo:** https://elimorals.github.io/gobmx-presencia-digital/

## Cifras (corte 2026-10-21)

| | |
|---|---:|
| Apps móviles | **519** (387 Android · 371 iOS · 274 en ambas) |
| Sitios web | **394** portales |
| Subdominios `.gob.mx` | **12,812** (CT + dotgob-mx) |
| Servicios / trámites | **6,141** (6,125 federales CONAMER + 16 brechas/clave) |
| Apps con análisis de permisos | **387** (todas las que tienen Android; 338 con permisos peligrosos) |

No existe un equivalente oficial: los catálogos del gobierno están en silos separados y el
nivel subnacional no se publica de forma central (ver `analisis/benchmark-existentes.md`).

## Estructura

```
gobmx-presencia-digital/
├── README.md                    ← este archivo
├── index.html                   ← redirect de GitHub Pages al dashboard
├── llms.txt · robots.txt · sitemap.xml   ← SEO / GEO (descubrimiento por buscadores y LLMs)
├── apps/
│   ├── inventario/*.json        ← apps por segmento (federal, autónomos, estatal A/B/C+CDMX+municipal)
│   ├── apps.json                ← consolidado + métricas de tienda (genera consolidar_incremental.py)
│   ├── apps.csv                 ← mismo, tabular
│   └── permisos/                ← permisos peligrosos por app (387) + README
├── sitios/
│   ├── *.json                   ← portales web por segmento (esquema-sitios-servicios.md)
│   ├── subdominios/*.txt        ← subdominios por dependencia desde Certificate Transparency
│   └── subdominios-consolidado.csv  ← 12,812 hosts .gob.mx (nuestro CT + dotgob-mx) con flag de actividad
├── servicios/
│   ├── brechas.json             ← servicios que faltan o solo existen en un canal (cruce apps×sitios)
│   ├── catalogo-conamer.json    ← trámites de alto uso con homoclave (CONAMER)
│   └── cnts-federal.json        ← catálogo federal completo (6,125 trámites)
├── analisis/
│   ├── comparacion.md           ← documento final: comparación a detalle
│   ├── seguridad.md             ← hallazgos transversales (paquetes de prueba, anti-bot, incidentes)
│   ├── benchmark-existentes.md  ← qué otros directorios/catálogos existen y qué les falta
│   └── harvest-subnacional.md   ← por qué los trámites estatales/municipales no están centralizados
├── web/                         ← dashboard (index.html + data.js) y bundler
├── gobmx.py                     ← CLI para consultar el inventario
├── mcp-server/                  ← MCP server (FastMCP) con 8 tools de consulta + README y prueba e2e
└── scripts/                     ← helpers (tiendas, CT, consolidar, qa, stats, regenerar) + esquemas
```

## Dashboard web

Navegador visual del inventario, en **https://elimorals.github.io/gobmx-presencia-digital/**
(claro/oscuro, responsive). Pestañas: Apps, Sitios, Servicios, Subdominios y **Guía** (documentación
del CLI y el MCP). Las barras filtran al hacer clic; cada app abre una ficha con sus permisos.

Para correrlo local: `cd web && python3 -m http.server` y abre `http://localhost:8000/`.
El dato lo empaqueta `scripts/build_dashboard_data.py` en `web/data.js`.

## CLI — `gobmx`

Consulta el inventario desde la terminal. Único requisito: Python 3, sin dependencias externas.

```bash
python3 gobmx.py stats                    # 519 apps · 394 sitios · 6141 servicios
python3 gobmx.py apps --estado Jalisco    # apps de un estado
python3 gobmx.py apps --sector seguridad --json
python3 gobmx.py sitios --nivel federal
python3 gobmx.py servicios --busca CURP
python3 gobmx.py dep IMSS                  # apps + sitios de una dependencia
python3 gobmx.py apps --orden estatal --poder judicial    # filtros por orden de gobierno y poder
python3 gobmx.py comparar --orden estatal --nombres "Jalisco,Nuevo León"
python3 gobmx.py comparar --orden municipal --nombres Monterrey,Guadalajara
python3 gobmx.py comparar --orden estatal --ordenar por_100k_hab.apps   # ranking de las 32
python3 gobmx.py comparar --orden federal  # se rechaza: no es comparable
```

## Orden de gobierno, poder y comparación

Cada app, sitio y servicio lleva `orden` (federal · estatal · municipal), `poder` (ejecutivo ·
legislativo · judicial · autónomo), `subtipo` (paraestatal, desconcentrado, universidad_autonoma,
extinto…) y `municipio` (nombre INEGI cuando el orden es municipal). `nivel` se conserva por
compatibilidad pero mezclaba orden con tipo de ente. Los asigna `scripts/clasificar_orden_poder.py`
con reglas por nivel, patrones de nombre, una tabla de excepciones y una tabla de las 32 fiscalías
estatales (autónoma o dependiente del Ejecutivo, con fuente). Reglas en `scripts/esquema.md`.

**Comparación:** solo estatal↔estatal o municipal↔municipal; nunca federal contra otro orden
(presupuesto, extensión y población no comparables). Métricas por entidad/municipio: apps, apps
activas, instalaciones, sitios, subdominios, cobertura de poderes y, con `datos/presupuesto/`,
tasas por 100 mil habitantes (Censo 2020 INEGI) y por cada mil millones de pesos de egreso (INEGI
EFIPEM). Sin dato, las tasas son `null`, nunca 0. CLI (`comparar`), MCP (`comparar`) y dashboard
(`window.GOBMX.entidades` / `.municipios`) usan la misma función de `gobmx.py`.

## MCP — `gobmx-inventario`

Servidor [MCP](https://modelcontextprotocol.io) de solo lectura: expone el inventario como 8 tools
consultables desde Claude u otro cliente. Instalación, referencia de tools y prueba end-to-end en
[`mcp-server/README.md`](mcp-server/README.md).

```bash
uv venv .venv && VIRTUAL_ENV=.venv uv pip install "mcp<2"
claude mcp add gobmx-inventario -- \
  "$PWD/.venv/bin/python" -I "$PWD/mcp-server/server.py"
claude mcp list   # debe decir: gobmx-inventario ... ✔ Connected
```

## Para agentes / LLMs

- [`llms.txt`](llms.txt) — resumen y enlaces a todos los datos, pensado para modelos.
- Datos crudos por HTTP (sin auth): `apps/apps.json`, `apps/permisos/permisos.json`,
  `sitios/*.json`, `servicios/*.json`, `sitios/subdominios-consolidado.csv`.
- Esquemas en `scripts/esquema.md` y `scripts/esquema-sitios-servicios.md`.

## Regenerar

```bash
scripts/regenerar.sh   # subdominios + clasifica orden/poder + consolida apps + QA + dashboard
SIN_RED=1 scripts/regenerar.sh   # igual, sin consultar tiendas
python3 -I scripts/test_orden_poder.py   # comprobación del clasificador y de comparar
```

Un **GitHub Action** (`.github/workflows/refresh-subdominios.yml`) refresca los subdominios por
Certificate Transparency y reconstruye `web/data.js` una vez al mes.

## Créditos y fuentes

- Subdominios `.gob.mx`: Certificate Transparency (crt.sh) + [dotgob-mx](https://github.com/AlejandroTC/dotgob-mx)
  de Alejandro TC (licencia MIT), de donde se integró su lista y su marca de actividad.
- Trámites: Catálogo Nacional de Regulaciones, Trámites y Servicios (CONAMER).
- Métricas de apps: Google Play y App Store (MX). Permisos: Google Play.

### Por qué así

- **Tres ejes paralelos** (`apps/`, `sitios/`, `servicios/`) con la **misma segmentación**
  (federal / autónomos-paraestatales / estatal A-B-C / CDMX / municipal) para poder cruzarlos:
  "este trámite existe en web pero no en app", "esta dependencia tiene app pero el sitio está caído".
- **Cada afirmación sobre un portal lleva evidencia fechada** (`estado_real`): fecha + URL + resultado.
- **El análisis vive aparte de los datos** (`analisis/` vs `apps|sitios|servicios`): los JSON son
  la fuente reutilizable; los `.md` son la lectura.

## Relación con Skills_MX

[Skills_MX](https://github.com/elimorals/Skills_MX) ya tiene **83 MCP servers / 417 tools** que
operan contra muchos de estos portales (SAT, IMSS, CURP/RENAPO, Banxico, predial municipal, DOF…),
cada uno con su sección "Estado real" de qué se validó en vivo. Este repo es el **mapa**; Skills_MX
es la **interacción**. Por cada portal documentado aquí se anota si Skills_MX ya tiene un MCP para él,
para no duplicar y priorizar los que faltan.

## Licencia

MIT. Autor: Elias Rashid Morales Mendoza ([@elimorals](https://github.com/elimorals)).
