# Esquema de cada segmento (`segmentos/<segmento>.json`)

Lista JSON de objetos:

```json
{
  "nombre": "IMSS Digital",
  "dependencia": "Instituto Mexicano del Seguro Social",
  "siglas": "IMSS",
  "nivel": "federal | autonomo | paraestatal | estatal | municipal",
  "estado": "Nacional | <entidad federativa>",
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
  `/Users/elias/Downloads/gob-mx-reverse-engineering/.venv/bin/python -I /Users/elias/Downloads/gob-mx-reverse-engineering/scripts/tienda.py {play-buscar|play|ios-buscar|ios} "<arg>"`
- (alternativa directa) scraper:
  `/Users/elias/Downloads/gob-mx-reverse-engineering/.venv/bin/python -I -c "from google_play_scraper import app; d=app('<id>',lang='es',country='mx'); print(d['title'],d['developer'],d['installs'],d['updated'])"`
  Búsqueda: `from google_play_scraper import search; search('<término>',lang='es',country='mx',n_hits=30)` (el primer resultado a veces trae appId None: ignóralo).
- Verifica `ios_id` con `curl -s 'https://itunes.apple.com/search?term=<término>&country=mx&entity=software&limit=25'` o `https://itunes.apple.com/lookup?id=<id>&country=mx`.
- No inventes IDs. Si no lo pudiste verificar, `null` y dilo en `notas`.
- Incluye apps retiradas si hay fuente (y marca `estatus`).
