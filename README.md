# gob-mx-reverse-engineering

Inventario y análisis de la **presencia digital del Estado mexicano**: aplicaciones
móviles, sitios web y servicios en línea de dependencias federales, organismos
autónomos, paraestatales, los tres poderes, estados y municipios.

Todo se construye con **observación pasiva** de fuentes públicas (tiendas de apps,
Certificate Transparency, páginas públicas) y búsqueda web. No hay escaneo intrusivo,
ni login con credenciales ajenas, ni envío de datos personales.

## Estructura

```
gob-mx-reverse-engineering/
├── README.md                    ← este archivo
├── apps/
│   ├── inventario/*.json        ← apps por segmento (federal, autónomos, estatal A/B/C+CDMX+municipal)
│   ├── apps.json                ← consolidado + métricas de tienda (genera consolidar.py)
│   └── apps.csv                 ← mismo, tabular
├── sitios/
│   ├── *.json                   ← portales web por segmento (esquema-sitios-servicios.md)
│   ├── subdominios/*.txt        ← subdominios por dependencia desde Certificate Transparency
│   └── subdominios-consolidado.csv  ← 12,110 hosts .gob.mx (nuestro CT + dotgob-mx) con flag de actividad
├── servicios/
│   ├── *.json                   ← trámites/servicios y por qué canal se pueden hacer (web/app/presencial)
│   └── catalogo-conamer.json    ← trámites desde el Catálogo Nacional (CONAMER), cruzados con apps/sitios
├── analisis/
│   ├── comparacion.md           ← documento final: comparación a detalle
│   ├── seguridad.md             ← hallazgos transversales (paquetes de prueba, anti-bot, incidentes)
│   └── benchmark-existentes.md  ← qué otros directorios/catálogos existen y qué les falta
├── gobmx.py                     ← CLI para consultar el inventario (python3 gobmx.py stats|apps|sitios|dep)
└── scripts/                     ← helpers (tiendas, CT, consolidar, stats) + esquemas
```

## CLI

```bash
python3 gobmx.py stats                    # resumen por nivel/sector/estatus
python3 gobmx.py apps --estado Jalisco    # apps de un estado
python3 gobmx.py apps --sector seguridad --json
python3 gobmx.py sitios --nivel federal
python3 gobmx.py dep IMSS                  # apps + sitios de una dependencia
```

## Créditos y fuentes

- Subdominios `.gob.mx`: Certificate Transparency (crt.sh) + [dotgob-mx](https://github.com/AlejandroTC/dotgob-mx)
  de Alejandro TC (licencia MIT), de donde se integró su lista y su marca de actividad.
- Trámites: Catálogo Nacional de Regulaciones, Trámites y Servicios (CONAMER).
- Métricas de apps: Google Play y App Store (MX).

### Por qué así

- **Tres ejes paralelos** (`apps/`, `sitios/`, `servicios/`) con la **misma segmentación**
  (federal / autónomos-paraestatales / estatal A-B-C / CDMX / municipal) para poder cruzarlos:
  "este trámite existe en web pero no en app", "esta dependencia tiene app pero el sitio está caído".
- **Cada afirmación sobre un portal lleva evidencia fechada** (`estado_real`), copiando la
  disciplina de [Skills_MX](https://github.com/elimorals/Skills_MX): fecha + URL + resultado observado.
- **El análisis vive aparte de los datos** (`analisis/` vs `apps|sitios|servicios`): los JSON son
  la fuente reutilizable; los `.md` son la lectura.

## Relación con Skills_MX

[Skills_MX](https://github.com/elimorals/Skills_MX) ya tiene **83 MCP servers / 417 tools** que
operan contra muchos de estos portales (SAT, IMSS, CURP/RENAPO, Banxico, predial municipal, DOF…),
cada uno con su sección "Estado real" de qué se validó en vivo. Este repo es el **mapa**; Skills_MX
es la **interacción**. Por cada portal documentado aquí se anota si Skills_MX ya tiene un MCP para él
(columna cruzada en `analisis/comparacion.md`), para no duplicar y para priorizar los que faltan.
```
```
