# Esquema de cada segmento (`segmentos/<segmento>.json`)

Lista JSON de objetos:

```json
{
  "nombre": "IMSS Digital",
  "dependencia": "Instituto Mexicano del Seguro Social",
  "siglas": "IMSS",
  "nivel": "federal | autonomo | paraestatal | estatal | municipal | poder_judicial | poder_legislativo | no_oficial  (heredado; se conserva por compatibilidad)",
  "estado": "Nacional | <entidad federativa>",
  "orden": "federal | estatal | municipal  (null solo si nivel=no_oficial)",
  "poder": "ejecutivo | legislativo | judicial | autonomo  (null solo si nivel=no_oficial)",
  "subtipo": "null | paraestatal | desconcentrado | universidad_autonoma | extinto | <texto corto>",
  "municipio": "nombre oficial INEGI si orden=municipal (p.ej. 'Benito Juárez' para Cancún); si no, null",
  "nota_clasificacion": "(opcional) por qué se eligió ese poder en un caso dudoso",
  "sector": "salud | fiscal | seguridad | movilidad | identidad | finanzas | educación | trabajo | vivienda | energía | clima | elecciones | turismo | trámites | otro",
  "android_id": "mx.gob.imss.imssdigital o null",
  "ios_id": "id numérico de App Store o null",
  "desarrollador_tienda": "nombre de la cuenta de desarrollador tal como aparece en la tienda",
  "proposito": "1-2 frases: qué hace",
  "funciones": ["lista de funciones clave"],
  "requiere_cuenta": "CURP | RFC+e.firma | Llave MX | NSS | INE | ninguna | otra",
  "estatus": "activa | retirada | sin actualizar >2 años | desconocido",
  "fuentes": ["URLs que respaldan el dato"],
  "notas": "controversias, incidentes de seguridad, fugas, reseñas negativas recurrentes, proveedor que la desarrolló, etc."
}
```

Reglas:
- Solo apps oficiales (publicadas por o para el gobierno). Apps de terceros "no oficiales" que imitan trámites → van con `"nivel": "no_oficial"` y nota.
- Verifica IDs con el helper (curl está bloqueado por un hook; usa esto):
  `.venv/bin/python -I scripts/tienda.py {play-buscar|play|ios-buscar|ios} "<arg>"`
- (alternativa directa) scraper:
  `.venv/bin/python -I -c "from google_play_scraper import app; d=app('<id>',lang='es',country='mx'); print(d['title'],d['developer'],d['installs'],d['updated'])"`
  Búsqueda: `from google_play_scraper import search; search('<término>',lang='es',country='mx',n_hits=30)` (el primer resultado a veces trae appId None: ignóralo).
- Verifica `ios_id` con `curl -s 'https://itunes.apple.com/search?term=<término>&country=mx&entity=software&limit=25'` o `https://itunes.apple.com/lookup?id=<id>&country=mx`.
- No inventes IDs. Si no lo pudiste verificar, `null` y dilo en `notas`.
- Incluye apps retiradas si hay fuente (y marca `estatus`).

## Orden de gobierno y poder

`nivel` mezclaba orden de gobierno con tipo de ente; `orden` + `poder` los separan. Los asigna
`scripts/clasificar_orden_poder.py` (idempotente: solo agrega lo que falta; `--forzar` recalcula,
`--revisar` imprime la tabla y todos los no-ejecutivos). Reglas, en orden:

1. Tabla de **excepciones** explícitas en el script (casos dudosos, con `nota_clasificacion`).
2. `nivel` poder_judicial / poder_legislativo.
3. Patrones de nombre: Poder Judicial, tribunales superiores, SCJN, CJF/OAJ, TEPJF → judicial;
   congresos, cámaras, auditorías superiores → legislativo; INE, Banxico, INEGI, CNDH, FGR,
   OPLEs, comisiones de DDHH, órganos garantes, universidades autónomas, tribunales
   administrativos/laborales → autonomo.
4. **Fiscalías estatales**: tabla `FISCALIAS` de las 32 entidades (autónoma vs. dependiente del
   Ejecutivo) con fuente por fila. Sin verificar → autonomo y se anota.
5. `nivel` autonomo → autonomo; todo lo demás → ejecutivo. Subtipo paraestatal/desconcentrado por
   patrones; `extinto` si el nombre lo dice; `universidad_autonoma`.

`orden`: municipal si `nivel=municipal`; federal si `nivel` es federal/paraestatal o `estado` es
Nacional; si no, estatal (incluye brechas agregadas con estado 'todos'/'mayoría'). `scripts/qa.py`
valida valores y coherencia (municipal ⇒ municipio no nulo salvo agregados; no_oficial ⇒ poder null).
