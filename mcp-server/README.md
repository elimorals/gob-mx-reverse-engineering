# mcp-server — `gobmx-inventario`

MCP server (FastMCP) de solo lectura sobre el inventario de este repo. Mismo dato que el
CLI `gobmx.py`, pero consultable desde Claude u otro cliente MCP.

## Tools

| Tool | Qué hace |
|---|---|
| `stats` | Totales y conteos por nivel/sector/estatus |
| `buscar_apps(nivel, estado, sector, estatus, texto, limite)` | Busca apps con filtros |
| `buscar_sitios(nivel, estado, texto, limite)` | Busca portales web |
| `buscar_servicios(texto, limite)` | Busca trámites/servicios (CONAMER + brechas) |
| `dependencia(nombre)` | Apps + sitios de una dependencia (match en dependencia o siglas) |
| `buscar_subdominio(texto, solo_activos, limite)` | Busca en los 12k+ subdominios `.gob.mx` consolidados |

## Instalar en Claude Code

El único requisito es [`uv`](https://docs.astral.sh/uv/) (descarga `mcp<2` solo la primera vez).
Copia `example.mcp.json` a tu config MCP, o:

```bash
claude mcp add gobmx-inventario -- uv run --no-project --quiet --with "mcp<2" \
  python /Users/elias/Downloads/gob-mx-reverse-engineering/mcp-server/server.py
```

## Notas

- Solo lectura: lee los JSON/CSV del repo (`../apps`, `../sitios`, `../servicios`). No escribe ni sale a la red.
- Fijado a `mcp<2` (FastMCP v1). En `mcp` 2.x `FastMCP` se renombró a `MCPServer`.
- Para integrarlo en [Skills_MX](https://github.com/elimorals/Skills_MX) como un server más del monorepo,
  este archivo es el punto de partida (`mp_gobmx_inventario`).
