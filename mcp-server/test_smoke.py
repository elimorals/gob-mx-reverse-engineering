"""Prueba de humo end-to-end del server por el protocolo MCP (stdio JSON-RPC).

Arranca el server como subproceso, hace el handshake, lista las tools y llama a cada una (incluye comparar federal, que debe rechazarse).
uso: uv run --no-project --with "mcp<2" python mcp-server/test_smoke.py
"""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = str(Path(__file__).resolve().parent / "server.py")


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-I", SERVER])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("tools:", [t.name for t in tools])
            assert {"stats", "buscar_apps", "buscar_sitios", "buscar_servicios",
                    "dependencia", "buscar_subdominio", "permisos", "comparar"} <= {t.name for t in tools}

            llamadas = [
                ("stats", {}),
                ("buscar_apps", {"sector": "identidad"}),
                ("buscar_apps", {"estado": "Jalisco", "limite": 3}),
                ("buscar_sitios", {"nivel": "federal", "limite": 3}),
                ("buscar_servicios", {"texto": "CURP"}),
                ("dependencia", {"nombre": "IMSS"}),
                ("permisos", {"texto": "IMSS"}),
                ("buscar_subdominio", {"texto": "imss", "solo_activos": True, "limite": 5}),
                ("buscar_apps", {"orden": "estatal", "poder": "judicial"}),
                ("buscar_sitios", {"orden": "federal", "poder": "legislativo"}),
                ("buscar_servicios", {"orden": "federal", "texto": "pasaporte", "limite": 2}),
                ("permisos", {"orden": "municipal", "limite": 2}),
                ("comparar", {"orden": "estatal", "nombres": "Jalisco, Nuevo León"}),
                ("comparar", {"orden": "municipal", "nombres": "Monterrey"}),
                ("comparar", {"orden": "federal"}),
            ]
            for nombre, args in llamadas:
                res = await s.call_tool(nombre, args)
                assert not res.isError, f"{nombre} devolvió error"
                txt = res.content[0].text if res.content else ""
                if nombre == "comparar" and args["orden"] == "federal":
                    assert "no son comparables" in txt, txt
                if nombre == "stats":
                    assert "apps_orden_poder" in txt
                print(f"OK {nombre}({args}) -> {len(txt)} chars")
    print("\n✅ todas las tools respondieron por el protocolo MCP")


if __name__ == "__main__":
    asyncio.run(main())
