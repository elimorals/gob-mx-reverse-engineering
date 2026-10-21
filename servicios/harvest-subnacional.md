# Servicios estatales y municipales — por qué siguen casi vacíos (#2)

**Fecha:** 2026-10-21. **Método:** navegador real (Chrome, extensión claude-in-chrome) para pasar el
Akamai que bloquea a `curl`/WebFetch. Solo lectura pasiva del catálogo público.

## Qué se intentó

El objetivo era llenar la capa subnacional de `servicios/` (hoy: 6,125 trámites **federales** vía el
dataset abierto de la SFP, y 0 estatales/municipales útiles) consultando el **Catálogo Nacional de
Regulaciones, Trámites y Servicios** (CNARTyS), `catalogonacional.gob.mx`, que por ley debe integrar
los tres órdenes de gobierno.

## Qué se encontró

1. **El Akamai sí se pasa con navegador real.** `curl`/WebFetch reciben 403 "Challenge Validation";
   el Chrome real carga el portal completo. Esto es reproducible y es la vía para cualquier cosecha futura.

2. **El portal expone filtros estatal y municipal** (dropdowns Estado → Municipio/alcaldía →
   Nivel de gobierno), y un API interno llamable desde el propio navegador (hereda la sesión Akamai):
   ```
   GET /Buscador/SearchInspeccionResult?search=&txtTipo=Todos&nivelId=-1&estadoId=<ID>&municipioId=-1&dependenciaId=-1&tem=<tema>
   (header X-Requested-With: XMLHttpRequest; devuelve HTML con tarjetas de resultado)
   ```

3. **Pero el contenido subnacional está vacío.** Barrido de los 32 estados (`estadoId` 1–32) por ese
   API, el 2026-10-21:
   - **Federación** (`estadoId=0`) y "todos" (`estadoId=-1`): devuelven datos (≈9 tarjetas/página, 34 KB).
   - **Los 32 estados, uno por uno: "No hay información disponible"** (0 resultados en todos).
   - El API no está roto (federal y búsqueda por texto sí responden); el subnacional simplemente no está cargado.

4. **Además, el CNARTyS cataloga Regulaciones / Inspecciones / Inspectores**, no trámites ciudadanos.
   Los trámites federales ya los teníamos del dataset de la SFP; este portal es un registro paralelo (RNIR).

## Conclusión

**Los trámites y servicios estatales y municipales NO están publicados de forma central y utilizable.**
Lo confirman tres fuentes independientes: el dataset abierto de la SFP (99% federal), el agente previo de
CONAMER, y ahora el propio catálogo nacional en vivo (los 32 estados vacíos). No es un límite de nuestra
herramienta: el dato no existe centralizado.

## Dónde vive realmente (para una cosecha futura)

La data subnacional está dispersa en **32 RETS estatales** (Registro Estatal de Trámites y Servicios, uno
por entidad, cada uno con su propio portal y a veces su propio anti-bot) **+ portales municipales**. Eso es
un harvest multi-portal (32+ sitios, sin esquema común) = proyecto aparte, no una consulta central. Para
cada estado, el punto de partida es su RETS (p.ej. "RETyS <estado>") o la ventanilla única estatal ya
listada en `sitios/estatal-ab.json` / `sitios/estatal-c-cdmx-municipal.json`.

Lo que sí quedó como capa subnacional estructurada son las **brechas** por servicio en
[`brechas.json`](brechas.json) (DIF, agua, transporte, salud, fiscalía, pagos), derivadas del cruce
apps × sitios.
