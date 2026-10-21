# gob-mx-reverse-engineering

Inventario y análisis de la **presencia digital del Estado mexicano**: aplicaciones
móviles, sitios web y servicios en línea de dependencias federales, organismos
autónomos, paraestatales, los tres poderes, estados y municipios.

Todo se construye con **observación pasiva** de fuentes públicas (tiendas de apps,
Certificate Transparency, páginas públicas) y búsqueda web. No hay escaneo intrusivo,
ni login con credenciales ajenas, ni envío de datos personales.

🔗 **Dashboard en vivo:** https://elimorals.github.io/gob-mx-reverse-engineering/

## Cifras (corte 2026-10-21)

| | |
|---|---:|
| Apps móviles | **466** (351 Android · 326 iOS · 246 en ambas) |
| Sitios web | **231** portales |
| Subdominios `.gob.mx` | **12,812** (CT + dotgob-mx) |
| Servicios / trámites | **6,141** (6,125 federales CONAMER + 16 brechas/clave) |
| Apps con análisis de permisos | **20** (piloto) |

No existe un equivalente oficial: los catálogos del gobierno están en silos separados y el
nivel subnacional no se publica de forma central (ver `analisis/benchmark-existentes.md`).

## Estructura

```
gob-mx-reverse-engineering/
├── README.md                    ← este archivo
├── index.html                   ← redirect de GitHub Pages al dashboard
├── llms.txt · robots.txt · sitemap.xml   ← SEO / GEO (descubrimiento por buscadores y LLMs)
├── apps/
│   ├── inventario/*.json        ← apps por segmento (federal, autónomos, estatal A/B/C+CDMX+municipal)
│   ├── apps.json                ← consolidado + métricas de tienda (genera consolidar_incremental.py)
│   ├── apps.csv                 ← mismo, tabular
│   └── permisos/                ← permisos peligrosos por app (piloto, 20 apps) + README
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
├── mcp-server/                  ← MCP server (FastMCP) con 7 tools de consulta + README y prueba e2e
└── scripts/                     ← helpers (tiendas, CT, consolidar, qa, stats, regenerar) + esquemas
```

## Dashboard web

Navegador visual del inventario, en **https://elimorals.github.io/gob-mx-reverse-engineering/**
(claro/oscuro, responsive). Pestañas: Apps, Sitios, Servicios, Subdominios y **Guía** (documentación
del CLI y el MCP). Las barras filtran al hacer clic; cada app abre una ficha con sus permisos.

Para correrlo local: `cd web && python3 -m http.server` y abre `http://localhost:8000/`.
El dato lo empaqueta `scripts/build_dashboard_data.py` en `web/data.js`.

## CLI — `gobmx`

Consulta el inventario desde la terminal. Único requisito: Python 3, sin dependencias externas.

```bash
python3 gobmx.py stats                    # 466 apps · 231 sitios · 6141 servicios
python3 gobmx.py apps --estado Jalisco    # apps de un estado
python3 gobmx.py apps --sector seguridad --json
python3 gobmx.py sitios --nivel federal
python3 gobmx.py servicios --busca CURP
python3 gobmx.py dep IMSS                  # apps + sitios de una dependencia
```

## MCP — `gobmx-inventario`

Servidor [MCP](https://modelcontextprotocol.io) de solo lectura: expone el inventario como 7 tools
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
scripts/regenerar.sh   # consolida apps + fusiona subdominios + QA + reconstruye el dashboard
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
