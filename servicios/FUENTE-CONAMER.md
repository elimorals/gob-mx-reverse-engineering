# Fuente del catálogo de trámites federales (CONAMER / CNARTyS)

**Corte: 2026-10-20**

## Qué fuente se usó y por qué

El portal canónico del **Catálogo Nacional de Regulaciones, Trámites y Servicios (CNARTyS,
antes CNTSE / RFTS)** —`catalogonacional.gob.mx`— y la Ventanilla Única Nacional
`gob.mx/tramites` están **detrás de Akamai (bot manager)**: toda petición automatizada
(curl, WebFetch, fetch de servidor) recibe **HTTP 403 / "Challenge Validation"**, incluso
con User-Agent de navegador, Referer y cabeceras completas. No son raspa­bles sin un
navegador real que resuelva el reto JS. Verificado hoy:

| URL | Resultado (2026-10-20) |
|---|---|
| `https://www.catalogonacional.gob.mx/` | 403 (WAF) |
| `https://catalogonacional.gob.mx/api/...` | 403 (WAF) |
| `https://www.gob.mx/tramites` | 200 pero cuerpo = página "Challenge Validation" de Akamai (1898 bytes) |
| `https://www.gob.mx/tramites/ficha/.../<homoclave>` | reto Akamai (sin contenido real) |
| `repodatos.atdt.gob.mx/.../*.csv` | 403 "Access Denied" (Akamai) por curl, WebFetch y ctx_fetch |

**No se raspó el portal.** La vía correcta resultó ser **DATOS ABIERTOS vía la API CKAN**,
no el portal ni el CSV directo.

## La vía que SÍ funcionó: API CKAN DataStore de datos.gob.mx

- Plataforma: `datos.gob.mx` (CKAN 2.11.6), API en `https://www.datos.gob.mx/api/3/action/`.
- **No existe** una organización ni dataset de CONAMER en datos.gob.mx (búsqueda de
  `conamer`, `cofemer`, `mejora regulatoria` → 0 resultados). El CNARTyS **no se publica
  como dataset abierto propio**.
- El dataset aprovechable lo publica la **SFP (Secretaría de la Función Pública)**:
  *"Nivel de digitalización de los trámites registrados en el Catálogo Nacional de Trámites
  y Servicios (CNTS)"*.
  - package id `7543f7bb-196d-4cb2-8bdf-9641e1e2195b`
  - resource id `5ee3ea5f-0593-4d6d-8309-e89afbd44e1f` (CSV, `datastore_active=true`)
  - El CSV directo (repodatos.atdt.gob.mx) está bloqueado por Akamai, **pero el mismo
    contenido se obtiene fila por fila con `datastore_search`**, que sí responde JSON.

Fue **API (CKAN DataStore)**, no descarga de dataset ni raspado del portal.

Campos por fila: `homoclave`, `dependencia`, `siglas`, `nombre_tramite`, `nivel_digitalizacion`.
Las homoclaves son **reales** (provienen del registro oficial); ninguna fue inventada.

## Cobertura lograda

- **Total de trámites en el dataset: 6 125.**
- **Nivel: todos FEDERALES.** Son 222 dependencias/organismos federales (incluye
  paraestatales y órganos como API-Veracruz, que es autoridad portuaria federal, no
  estatal). **No hay trámites estatales ni municipales** en este dataset abierto: aunque
  el CNARTyS sí incorpora los subnacionales, la SFP solo publica el subconjunto federal
  (RFTS). Para estatal/municipal no se halló fuente abierta equivalente.

| Nivel | Nº trámites | Fuente |
|---|---|---|
| Federal | 6 125 | datos.gob.mx CKAN DataStore (SFP CNTS) |
| Estatal | 0 (no publicado como datos abiertos) | — |
| Municipal | 0 (no publicado como datos abiertos) | — |

### Nivel de digitalización (6 125 trámites federales)

| nivel_digitalizacion | Nº |
|---|---|
| Información (solo informativo) | 3 220 |
| Descargar formatos | 1 297 |
| Servicios punta a punta (100% en línea) | 647 |
| No reportado | 497 |
| Mandar formatos | 464 |

Solo **~10.6% (647/6125)** de los trámites federales son punta a punta; **más de la mitad
son solo informativos o de descarga de formatos**.

### Top dependencias por nº de trámites

SCT 532 · CNBV 507 · COFEPRIS 329 · SE 313 · SAT 303 · CNSF 255 · IMSS 182 · SEP 166 ·
SEMARNAT 161 · ISSSTE 131 · SHCP 124 · SRE 108 · CRE 105 · CONSAR 102 · CNH 97.

## Qué hay en `catalogo-conamer.json`

Una **muestra curada de los trámites federales de alto uso** que pidió la tarea
(RFC, CURP, pasaporte, licencia, IMSS, infonavit, actas, citas), con su **homoclave real**
y su `nivel_digitalizacion` del CNTS, **cruzada contra nuestro inventario** (`apps/apps.json`
y `sitios/*.json`) para llenar `canales` y `acceso_programatico`. No es el volcado de las
6 125 filas (está en `/tmp/conamer_raw/cnts_all.json` si se quiere sembrar completo).

### Reglas aplicadas (sin inventar)
- **Homoclaves**: todas verificadas contra el DataStore. Entradas transversales que no son
  trámite del catálogo (p. ej. "cita") llevan `homoclave: null` a propósito.
- **url_web**: solo URLs ya **verificadas en nuestro `sitios/federal.json`** (portales de
  dependencia / canales de cita). La ficha canónica `gob.mx/tramites/ficha/<slug>/<homoclave>`
  **no se verificó** (Akamai) → se dice en `notas`, no se inventa. Donde no hay URL verificada
  (licencia federal, acta de nacimiento nacional) → `url_web: null`.
- **acceso_programatico**: taxonomía Skills_MX. gob.mx tras reto Akamai ⇒ `web_con_captcha`;
  servicios con login/e.firma ⇒ `requiere_login`.

## Hallazgos de nivel (huecos)
1. **El CNARTyS no es datos abiertos ni API pública**: el portal canónico está tras WAF; lo
   único abierto es el subconjunto federal que republica la SFP.
2. **Estatal y municipal: cero cobertura abierta.** El trámite que más toca al ciudadano
   —acta de nacimiento, licencia de conducir ordinaria, predial— es competencia subnacional
   y **no está** en esta fuente federal.
3. **El CNTS subreporta digitalización real**: p. ej. la constancia de vigencia de derechos
   IMSS figura como "Información" pero en la práctica se baja en línea y en IMSS Digital.
   El nivel declarado va por detrás del canal observado en nuestro inventario de apps.
