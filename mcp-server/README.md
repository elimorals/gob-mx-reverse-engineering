# mcp-server — `gobmx-inventario`

MCP server (FastMCP) **de solo lectura** sobre el inventario de este repo: expone las apps,
sitios, servicios y subdominios como tools para consultarlos desde Claude u otro cliente MCP.
Mismo dato que el CLI `gobmx.py`; reusa su lógica (`import gobmx`), no duplica código.

- **Estado real:** instalado y validado en vivo el 2026-10-20 en macOS (Darwin 25.6.0), Python 3.13,
  `mcp 1.x`. `claude mcp list` → `✔ Connected`. Prueba end-to-end por protocolo (stdio JSON-RPC):
  las tools responden sin error (`mcp-server/test_smoke.py`; 8 tools desde 2026-10-21 con `comparar`).
- **Sin red, sin escritura:** solo lee los JSON/CSV del repo. No sale a internet ni modifica nada.

---

## Tools

### `stats() -> dict`
Resumen del inventario. Sin parámetros.
Devuelve: `apps`, `sitios`, `servicios`, `permisos` (totales) y los desgloses `apps_por_nivel`,
`apps_por_sector`, `apps_por_estatus`, `apps_con_android`, `apps_con_ios`, y las matrices
`apps_orden_poder` / `sitios_orden_poder` (orden × poder con todas las celdas, incluidas las de 0,
más `sin_orden(no_oficial)`).

```jsonc
// stats()
{
  "apps": 519, "sitios": 394, "servicios": 6141, "permisos": 387,
  "apps_por_nivel": {"estatal": 277, "municipal": 64, "federal": 64, "paraestatal": 38, "autonomo": 19, "no_oficial": 4},
  "apps_con_android": 387, "apps_con_ios": 371,
  "apps_orden_poder": {"federal": {"ejecutivo": 102, "legislativo": 0, "judicial": 2, "autonomo": 17},
                       "estatal": {"ejecutivo": 258, "legislativo": 0, "judicial": 5, "autonomo": 14},
                       "municipal": {"ejecutivo": 64, "legislativo": 0, "judicial": 0, "autonomo": 0},
                       "sin_orden(no_oficial)": {"null": 4}}
}
```

### `buscar_apps(nivel="", estado="", sector="", estatus="", texto="", orden="", poder="", limite=50) -> list`
Busca apps. Todos los filtros son opcionales; `orden` y `poder` son **exactos** (sin acentos ni
mayúsculas), el resto hace match **parcial, sin distinguir mayúsculas**.
- `orden`: `federal` · `estatal` · `municipal`
- `poder`: `ejecutivo` · `legislativo` · `judicial` · `autonomo`
- `nivel` (campo heredado): `federal` · `estatal` · `municipal` · `paraestatal` · `autonomo` · `no_oficial`
- `estado`: entidad federativa (p.ej. `Jalisco`, `Ciudad de México`)
- `sector`: `seguridad` · `movilidad` · `salud` · `fiscal` · `finanzas` · `identidad` · `trámites` ·
  `educación` · `turismo` · `clima` · `vivienda` · `energía` · `trabajo` · `elecciones` · `otro`
- `estatus`: `activa` · `retirada` · `sin actualizar >2 años` · `desconocido`
- `texto`: busca en nombre, dependencia, siglas y propósito
- `limite`: máximo de resultados (default 50)

Cada resultado es el objeto app completo (incluye `android_id`, `ios_id`, `play`/`appstore` con métricas).

```
buscar_apps(sector="identidad")                → 12 apps de identidad digital estatal
buscar_apps(estado="Jalisco", estatus="activa")
buscar_apps(texto="licencia", nivel="estatal")
buscar_apps(orden="estatal", poder="judicial")  → apps de poderes judiciales estatales
```

### `buscar_sitios(nivel="", estado="", texto="", orden="", poder="", limite=50) -> list`
Busca portales web. Filtros: `orden`, `poder`, `nivel`, `estado`, `texto` (dependencia/url/propósito), `limite`.
Cada resultado trae `url`, `tipo`, `plataforma`, `anti_bot`, `autenticacion` y `estado_real` (evidencia fechada).

```
buscar_sitios(nivel="federal")
buscar_sitios(estado="Veracruz")          → incluye el hallazgo de TLS inválido
```

### `buscar_servicios(texto="", orden="", poder="", limite=50) -> list`
Busca trámites/servicios: el catálogo CONAMER (`catalogo-conamer.json`, `cnts-federal.json`) y las
brechas (`brechas.json`). `texto` busca en `servicio`/`nombre_tramite`/`dependencia`/`brecha`/`siglas`.
`orden`/`poder` filtran; los 6,125 trámites CNTS se clasifican al cargar (orden federal, poder ejecutivo).

```
buscar_servicios(texto="CURP")
buscar_servicios(texto="pasaporte")
```

### `dependencia(nombre) -> dict`
Todo lo de una dependencia en un solo llamado: `{apps: [...], sitios: [...]}`.
`nombre` hace match en el campo dependencia o en las siglas. Cada app incluye su análisis de
`permisos` cuando existe.

```
dependencia("IMSS")   → 2 apps (con permisos) + su portal
dependencia("CFE")    → 5 apps + sitio
```

### `permisos(nivel="", estado="", sector="", texto="", orden="", poder="", solo_peligrosos=False, limite=50) -> list`
Análisis de permisos y privacidad de apps (387 apps con Android). Cada entrada trae
`permisos_peligrosos`, `trackers` (si hay) y `notas` de qué no cuadra con el propósito, más
`orden`/`poder`/`subtipo`/`municipio` de la app (join por `android_id`).
`texto` hace match en nombre/dependencia/android_id.

```
permisos(texto="IMSS")   → IMSS Digital: 10 permisos peligrosos (micrófono, calendario…)
permisos(orden="municipal", solo_peligrosos=True)
```

### `comparar(orden, nombres="", ordenar_por="") -> dict`
Compara **entidades** (`orden="estatal"`, las 32) o **municipios** (`orden="municipal"`).
`nombres`: lista separada por comas, match sin acentos (`"Jalisco, nuevo leon"`); vacío = todos.
`ordenar_por`: ranking descendente por una métrica con ruta de punto (`apps`, `por_100k_hab.sitios`,
`por_mil_mdp.apps`, `egreso_por_hab`, `instalaciones_por_hab`…); las filas sin dato van al final.
**Rechaza `orden="federal"`** (devuelve `{"error": ...}`): su presupuesto, extensión y población no
son comparables con los de una entidad o un municipio.

Devuelve `{orden, metodologia, ordenado_por, presupuesto_disponible, filas}`. Cada fila: `estado`, `cve_ent`,
(`municipio`, `cve_mun` en municipal), `apps`, `apps_activas`, `instalaciones`, `sitios`,
`subdominios`, `subdominios_activos`, `poderes` (conteo por poder), `cobertura_poderes` (0-4),
`poblacion_2020`, `egresos_mxn`, `egresos_anio`, `egreso_por_hab`, `transferencias_pef_mxn` (Ramos 28+33),
`transferencias_pef_anio`, `presupuesto_notas` (p. ej. CDMX con dato trimestral preliminar), `por_100k_hab`,
`instalaciones_por_hab`, `por_mil_mdp` (tasas `null` si no hay `datos/presupuesto/*.json`).

```
comparar(orden="estatal", nombres="Jalisco, Nuevo León")
comparar(orden="municipal", nombres="Monterrey, Guadalajara")
comparar(orden="estatal", ordenar_por="por_100k_hab.apps")   # ranking de las 32
comparar(orden="federal")   → {"error": "No se compara el orden federal: ..."}
```

### `buscar_subdominio(texto="", solo_activos=False, limite=100) -> list`
Busca en los **12,812 subdominios `.gob.mx`** de `sitios/subdominios-consolidado.csv`
(Certificate Transparency + dotgob-mx). `texto` hace match en el host; `solo_activos=True` deja solo
los marcados activos por dotgob-mx (corte 13/10/2026). Cada fila: `host, fuente, activo_dotgob,
dependencia_o_estado, estado, municipio` (estado/municipio `null` si el slug no está mapeado en
`sitios/subdominios/slugs.json`).

```
buscar_subdominio(texto="sat", solo_activos=True)
buscar_subdominio(texto="pruebas")     → instancias de prueba expuestas en CT
```

---

## Instalación

Único requisito: [`uv`](https://docs.astral.sh/uv/). Descarga `mcp<2` solo la primera vez; no hace
falta clonar nada más ni activar un venv.

### Claude Code (una línea)

```bash
claude mcp add gobmx-inventario -- uv run --no-project --quiet --with "mcp<2" \
  python /ruta/absoluta/a/gobmx-presencia-digital/mcp-server/server.py
```

Verifica: `claude mcp list` debe mostrar `gobmx-inventario ... ✔ Connected`.
Quitar: `claude mcp remove gobmx-inventario`.

> **Vía rápida (recomendada en local):** `uv run --with "mcp<2"` resuelve el paquete en cada arranque
> y en **caché frío puede pasar de los 30 s de timeout de conexión** (el server se marca como no
> conectado). Para evitarlo, apunta a un venv que ya tenga `mcp` instalado y así el arranque es ~0.3 s:
>
> ```bash
> uv venv .venv && VIRTUAL_ENV=.venv uv pip install "mcp<2"
> claude mcp add gobmx-inventario -- \
>   /ruta/al/repo/.venv/bin/python -I /ruta/al/repo/mcp-server/server.py
> ```
>
> La forma `uv run` de `example.mcp.json` sigue siendo la portable entre máquinas; úsala cuando el
> arranque lento no importe, o pre-calienta la caché una vez con `uv run --with "mcp<2" python -c ""`.

### Config manual (cualquier cliente MCP)

Copia el bloque de [`example.mcp.json`](example.mcp.json) a la config de tu cliente
(Claude Desktop, etc.). Ajusta la ruta absoluta si moviste el repo.

---

## Probar

```bash
# prueba end-to-end por el protocolo MCP (handshake + llamada a las 8 tools, incluido comparar rechazando federal)
uv run --no-project --with "mcp<2" python mcp-server/test_smoke.py
```

Salida esperada: `✅ todas las tools respondieron por el protocolo MCP`.

---

## Diseño y decisiones

- **La carpeta es `mcp-server/`, no `mcp/`.** Una carpeta llamada `mcp` en la raíz del repo ensombrece
  el paquete `mcp` de Python (el server hace `sys.path.insert(ROOT)` para `import gobmx`), y el import
  fallaría. El guion evita la colisión.
- **Fijado a `mcp<2`.** En `mcp` 2.x `FastMCP` se renombró a `MCPServer` y cambió la API. v1 es estable
  y es la versión que usa [Skills_MX](https://github.com/elimorals/Skills_MX).
- **Reusa el CLI.** `import gobmx` trae `apps()` y `cargar()`; el server solo añade los filtros y el
  envoltorio de tool. Un cambio en el formato de datos se arregla en un solo lugar.
- **Solo lectura.** No hay tools de escritura a propósito: el inventario se regenera con los scripts
  (`scripts/consolidar.py`), no desde el MCP.

## Portar a Skills_MX

Para integrarlo como un server más del monorepo (`mp_gobmx_inventario`): este `server.py` es el punto
de partida. Habría que empaquetar los datos (o apuntar a una copia versionada), añadir la sección
"Estado real" al README del MCP y registrarlo en el `CATALOGO.md`, siguiendo el patrón de los otros 83.
