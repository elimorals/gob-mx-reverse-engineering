# mcp-server — `gobmx-inventario`

MCP server (FastMCP) **de solo lectura** sobre el inventario de este repo: expone las apps,
sitios, servicios y subdominios como tools para consultarlos desde Claude u otro cliente MCP.
Mismo dato que el CLI `gobmx.py`; reusa su lógica (`import gobmx`), no duplica código.

- **Estado real:** instalado y validado en vivo el 2026-10-20 en macOS (Darwin 25.6.0), Python 3.13,
  `mcp 1.x`. `claude mcp list` → `✔ Connected`. Prueba end-to-end por protocolo (stdio JSON-RPC):
  las 6 tools responden sin error (`mcp-server/test_smoke.py`).
- **Sin red, sin escritura:** solo lee los JSON/CSV del repo. No sale a internet ni modifica nada.

---

## Tools

### `stats() -> dict`
Resumen del inventario. Sin parámetros.
Devuelve: `apps`, `sitios`, `servicios` (totales) y los desgloses `apps_por_nivel`,
`apps_por_sector`, `apps_por_estatus`, `apps_con_android`, `apps_con_ios`.

```jsonc
// stats()
{
  "apps": 468, "sitios": 231, "servicios": 6141,
  "apps_por_nivel": {"estatal": 277, "federal": 65, "municipal": 64, "paraestatal": 38, "autonomo": 20, "no_oficial": 4},
  "apps_con_android": 344, "apps_con_ios": 303
}
```

### `buscar_apps(nivel="", estado="", sector="", estatus="", texto="", limite=50) -> list`
Busca apps. Todos los filtros son opcionales y hacen match **parcial, sin distinguir mayúsculas**.
- `nivel`: `federal` · `estatal` · `municipal` · `paraestatal` · `autonomo` · `no_oficial`
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
```

### `buscar_sitios(nivel="", estado="", texto="", limite=50) -> list`
Busca portales web. Filtros: `nivel`, `estado`, `texto` (dependencia/url/propósito), `limite`.
Cada resultado trae `url`, `tipo`, `plataforma`, `anti_bot`, `autenticacion` y `estado_real` (evidencia fechada).

```
buscar_sitios(nivel="federal")
buscar_sitios(estado="Veracruz")          → incluye el hallazgo de TLS inválido
```

### `buscar_servicios(texto="", limite=50) -> list`
Busca trámites/servicios: el catálogo CONAMER (`catalogo-conamer.json`, `cnts-federal.json`) y las
brechas (`brechas.json`). `texto` busca en `servicio`/`nombre_tramite`/`dependencia`/`brecha`/`siglas`.

```
buscar_servicios(texto="CURP")
buscar_servicios(texto="pasaporte")
```

### `dependencia(nombre) -> dict`
Todo lo de una dependencia en un solo llamado: `{apps: [...], sitios: [...]}`.
`nombre` hace match en el campo dependencia o en las siglas.

```
dependencia("IMSS")   → 2 apps + su portal
dependencia("CFE")    → 5 apps + sitio
```

### `buscar_subdominio(texto="", solo_activos=False, limite=100) -> list`
Busca en los **12,110 subdominios `.gob.mx`** de `sitios/subdominios-consolidado.csv`
(Certificate Transparency + dotgob-mx). `texto` hace match en el host; `solo_activos=True` deja solo
los marcados activos por dotgob-mx (corte 13/10/2026). Cada fila: `host, fuente, activo_dotgob,
dependencia_o_estado`.

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
  python /Users/elias/Downloads/gob-mx-reverse-engineering/mcp-server/server.py
```

Verifica: `claude mcp list` debe mostrar `gobmx-inventario ... ✔ Connected`.
Quitar: `claude mcp remove gobmx-inventario`.

### Config manual (cualquier cliente MCP)

Copia el bloque de [`example.mcp.json`](example.mcp.json) a la config de tu cliente
(Claude Desktop, etc.). Ajusta la ruta absoluta si moviste el repo.

---

## Probar

```bash
# prueba end-to-end por el protocolo MCP (handshake + llamada a las 6 tools)
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
