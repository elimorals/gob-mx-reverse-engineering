# Capa de presupuesto: fuentes y método

Archivos: `entidades.json` (32 filas) y `municipios.json` (25 municipios del inventario). Los regenera
`scripts/presupuesto.py` a partir de las descargas (ver «Regenerar»). Descargados el 2026-10-21.

## Series

| Serie | Año | Fuente (URL exacta) |
|---|---|---|
| Egresos estatales (31 gobiernos) | 2024, cifras definitivas | INEGI EFIPEM anual estatal: https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_estatal_csv.zip |
| Egresos de CDMX | 2024, acumulado al 4T, cifras preliminares | INEGI EFIPEM trimestral: https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_trimestral_csv.zip |
| Egresos municipales | 2024, cifras definitivas (los 25 tienen dato 2024) | INEGI EFIPEM anual municipal: https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_municipal_csv.zip |
| Ramo 28 y Ramo 33 por entidad | PEF 2026 aprobado | SHCP, Transparencia Presupuestaria, datos abiertos del PEF: https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/PEF_2026.csv |
| Población | Censo 2020 | INEGI ITER nacional: https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip |

Página del programa: https://www.inegi.org.mx/programas/finanzas/ . Catálogo de Transparencia Presupuestaria:
https://www.transparenciapresupuestaria.gob.mx/Datos-Abiertos .

## Conceptos

- **`egresos_inegi.total_mxn`**: la fila `TEMA=Egresos, CATEGORIA=Tema, DESCRIPCION_CATEGORIA="Total de egresos"` de la
  EFIPEM anual. Es el total de egresos e **incluye el capítulo «Disponibilidad final»** (el efectivo que queda al cierre).
  Por eso va también el campo extra `egresos_inegi.disponibilidad_final_mxn`. Si la EFIPEM no trae la fila, ese campo
  vale `null` y no `0`: en el archivo no se distingue un cero de una fila que no se publicó. Para aproximar el gasto
  devengado: `total_mxn - disponibilidad_final_mxn`. En Monterrey 2022 esa resta coincide al peso con el formato LDF 7d
  del municipio (ver «Cruces»).
- **CDMX**: no está en la EFIPEM anual (el metadato dice «Se difunde información de 31 Gobiernos Estatales» y ningún año
  desde 1989 la trae). Para CDMX se usa la EFIPEM **trimestral**, «Total de egresos» con clasificación económica (CEG)
  acumulado al 4T 2024. Ese dato no trae disponibilidad final y es preliminar. En los estados que están en las dos
  series, el 4T trimestral cuadra con el anual menos disponibilidad: Aguascalientes 1.000, Veracruz 1.000, Nuevo León 0.999,
  Jalisco 1.006. Edomex no cuadra porque su trimestral solo cubre el Poder Ejecutivo. La nota va en `notas`.
- **`transferencias_pef.ramo28_mxn` / `ramo33_mxn`**: suma de `MONTO_PEF_2026` con `ID_RAMO` 28 y 33, agrupada por
  `ID_ENTIDAD_FEDERATIVA`. Se omite la clave 34 («No Distribuible Geográficamente»): 17.3 mil millones en el Ramo 28 y
  62.8 mil millones en el Ramo 33 (parte de FASSA, FASP, FONE, FAM y otros fondos). Por eso las sumas por entidad no dan el
  total del ramo: 1,456,045.9 millones en el Ramo 28 y 1,041,892.9 millones en el Ramo 33.
- **Población**: `POBTOT` del ITER en las filas `LOC=0000`; `MUN=000` es el total estatal. El script verifica que la suma
  de las 32 entidades dé 126,014,024, el total nacional.

## Advertencias metodológicas

1. **Pesos corrientes**, sin deflactar. Las series son de años distintos: egresos 2024, PEF 2026 y población 2020. Un
   cociente entre ellas, como el egreso per cápita, mezcla años. Para comparar entre entidades del mismo orden sirve; como
   cifra absoluta, no.
2. **Ramo 28 + 33 no es el gasto total**. Son transferencias federales *presupuestadas*. No incluyen ingresos propios, deuda,
   convenios ni el Ramo 23, y una parte del Ramo 28 (Fondo de Fomento Municipal y la porción municipal del FGP) y del
   Ramo 33 (FAIS municipal, FORTAMUN) **pasa a los municipios**. El dato de la entidad incluye esos recursos municipales.
   Para municipios, `transferencias_pef` es `null`: el PEF no los desagrega por municipio.
3. El egreso estatal incluye el capítulo «Recursos asignados a municipios». Si se suman estado y municipios, ese monto se
   cuenta dos veces.
4. **CDMX tiene alcaldías (demarcaciones territoriales), no municipios**, y su gobierno concentra funciones que en otros
   estados son municipales. Su egreso no es comparable de forma directa con el de las otras 31 entidades. Además viene de
   otra serie (punto anterior).
5. La cobertura institucional de la EFIPEM cambia según la entidad: en Edomex abarca los tres poderes, organismos auxiliares
   y autónomos. Dentro de un municipio, la EFIPEM cubre el ayuntamiento. Los organismos operadores de agua o institutos
   municipales del inventario (SAPAL, Agua de Hermosillo, etc.) pueden no estar consolidados en esa cifra.
6. La EFIPEM 2025 existe, pero es preliminar y en municipios cubre 1,737 gobiernos (2,380 en 2024). Por eso el año base es
   2024. Para cambiarlo, edita `ANIO_EFIPEM` en el script. Si a un municipio le falta el año base, el script usa el más
   reciente anterior y lo anota en `notas`.

## Municipios: normalización

El script lee las entradas `nivel`/`orden` = municipal de `apps/apps.json` y `sitios/*.json` (campos `dependencia` y
`municipio`). A cada nombre le asigna el municipio del catálogo INEGI (`catalogos/tc_municipio.csv` de la EFIPEM) de la
misma entidad cuyo nombre oficial aparece en él como palabra completa, y se queda con la coincidencia más larga. Si no
encuentra ninguna o encuentra un empate, se detiene. Los nombres del inventario quedan en el campo extra `alias`.
Ejemplos: «Ayuntamiento de Benito Juárez (Cancún)» → Benito Juárez, 23005; «Municipio de Querétaro» → Querétaro, 22014;
«San Luis Potosí (capital)» → San Luis Potosí, 24028; «Agua de Hermosillo (organismo operador municipal)» → Hermosillo,
26030. `cve_mun` lleva las 5 cifras (CVEGEO: entidad + municipio).

## Cruces contra una segunda fuente

| Cifra | Este archivo | Segunda fuente | Resultado |
|---|---|---|---|
| Egresos Monterrey 2024 | 10,286,997,010 | Formato LDF 7d «Resultados de Egresos», Tesorería de Monterrey, columna 2024 (devengado): 10,286,997,000.22 — https://www.monterrey.gob.mx/pdf/tesoreria/2026/Resultados_de_Egresos_Formato_7d.pdf | coincide (difieren 10 pesos) |
| Egresos Monterrey 2022 (EFIPEM total − disponibilidad final) | 8,153,791,529 − 284,056,771 = 7,869,734,758 | mismo formato 7d, columna 2022: 7,869,734,755.85 | coincide; confirma que el «total» de EFIPEM incluye la disponibilidad final |
| Ramo 28 Coahuila / Durango, PEF 2026 | 35,151.6 / 20,534.1 millones | Instituto Belisario Domínguez (Senado), citado por El Siglo de Torreón, 14-mar-2026: 35,151.6 / 20,534.1 millones — https://www.elsiglodetorreon.com.mx/noticia/2026/coahuila-y-durango-destacan-en-el-pef-2026-por-aumento-en-recursos-federalizados.html | coincide |
| Ramo 33 Coahuila / Durango, PEF 2026 | 24,968.5 / 19,932.4 millones | misma nota (IBD): 25,720.4 / 20,548.4 millones | **no coincide: el IBD da 3.0 % y 3.1 % más**. La causa no está verificada. Lo más probable es que el IBD reparta por entidad montos que en el CSV del PEF van como «No Distribuible» (FASP y parte de FASSA y FONE) |
| Ramo 28 total nacional | 1,456,045.9 millones (incluye la clave 34) | CEFP, infografía PPEF 2026 — https://www.cefp.gob.mx/publicaciones/infografias/2025/dpie/infdpie1832025.pdf (cifra vista solo en el extracto del buscador: el certificado TLS del CEFP está vencido y no se descargó) | coincide según el extracto |
| Población Monterrey / Tijuana | 1,142,994 / 1,922,523 | Gobierno de Nuevo León (tabla con fuente Censo 2020) y Zeta Tijuana (2021) | coincide |

## Regenerar

```sh
# 1. Descargar las cinco fuentes de la tabla de arriba en un directorio propio (son datos no confiables)
# 2. Ejecutar desde la raíz del repo:
python3 -I datos/presupuesto/scripts/presupuesto.py /ruta/a/descargas
```

transparenciapresupuestaria.gob.mx no envía el certificado intermedio de su cadena TLS (Let's Encrypt), así que
`urllib` falla con `CERTIFICATE_VERIFY_FAILED`. Hay que completar la cadena descargando el intermedio desde la URL AIA del
certificado, sin desactivar la verificación, o bajar el CSV con un navegador.
