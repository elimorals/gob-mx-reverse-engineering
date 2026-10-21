# Esquema: sitios web y servicios digitales

Inspirado en la sección "Estado real" de los README de [Skills_MX](https://github.com/elimorals/Skills_MX):
cada afirmación sobre un portal lleva fecha, URL y resultado observado.

## `inventario/sitios/<segmento>.json` — lista de objetos

```json
{
  "dependencia": "Servicio de Administración Tributaria",
  "siglas": "SAT",
  "nivel": "federal | autonomo | paraestatal | estatal | municipal | poder_legislativo | poder_judicial  (heredado)",
  "estado": "Nacional | <entidad>",
  "orden": "federal | estatal | municipal",
  "poder": "ejecutivo | legislativo | judicial | autonomo",
  "subtipo": "null | paraestatal | desconcentrado | universidad_autonoma | extinto | <texto corto>",
  "municipio": "nombre oficial INEGI si orden=municipal; si no, null",
  "url": "https://www.sat.gob.mx",
  "tipo": "portal_institucional | ventanilla_tramites | pagos | consulta_publica | datos_abiertos | transparencia | identidad | citas | sistema_interno_expuesto | otro",
  "proposito": "1-2 frases",
  "servicios_en_linea": ["consulta CFDI", "constancia de situación fiscal", "..."],
  "autenticacion": "ninguna | CURP | RFC+contraseña | e.firma | Llave MX | Llave CDMX | cuenta propia | otra",
  "anti_bot": "ninguno | reCAPTCHA | reCAPTCHA Enterprise | hCaptcha | ALTCHA | CAPTCHA imagen | Akamai | Cloudflare | Radware | Imperva | F5 | desconocido",
  "plataforma": "gob.mx (CMS federal) | WordPress | Drupal | Joomla | ASP.NET | Java/JSF | Angular | React | Ember | Oracle | SAP | desconocido",
  "api_publica": "URL de API/datos abiertos o null",
  "estado_real": [{"fecha": "2026-10-20", "url": "...", "resultado": "200 / challenge Akamai / TLS inválido / timeout ..."}],
  "fuentes": ["URLs"],
  "notas": "incidentes (hackeos, fugas, caídas), proveedor, dominios fuera de gob.mx, etc."
}
```

## `inventario/servicios/<segmento>.json` — trámites/servicios y su canal

```json
{
  "servicio": "Renovación de licencia de conducir",
  "dependencia": "Secretaría de Movilidad",
  "nivel": "...", "estado": "...", "orden": "...", "poder": "...", "subtipo": null, "municipio": null,
  "sector": "salud | fiscal | seguridad | movilidad | identidad | finanzas | educación | trabajo | vivienda | energía | agua | justicia | registro_civil | propiedad | empresa | otro",
  "canales": {"web": "completo | parcial | solo_informativo | no", "app": "completo | parcial | no",
              "presencial_obligatorio": true, "whatsapp_telefono": false},
  "url_web": "...", "app_relacionada": "android_id o nombre",
  "autenticacion": "...",
  "acceso_programatico": "api_publica | web_sin_captcha | web_con_captcha | requiere_login | solo_presencial",
  "brecha": "qué falta: p.ej. 'no hay pago en línea', 'solo existe en 3 estados', 'app sin el trámite que sí está en web'",
  "fuentes": ["URLs"]
}
```

Reglas:
- No inventes URLs. Verifica con WebFetch o con el fingerprint (`scripts/fingerprint.py`). Si no pudiste, dilo en `notas`.
- `acceso_programatico` sigue la taxonomía de Skills_MX: real/API, entrega a humano (CAPTCHA o login), sin API pública.
- Solo observación pasiva: GET de páginas públicas. Nada de fuerza bruta, escaneo de puertos, login con credenciales ajenas ni envío de datos personales.
- `orden`/`poder`/`subtipo`/`municipio`: mismas reglas que en apps (ver `scripts/esquema.md`, sección
  "Orden de gobierno y poder"). `servicios/cnts-federal.json` (6,125 trámites) no los trae en disco:
  `gobmx.servicios()` y el build los asignan al cargar con el mismo clasificador (todos orden federal,
  poder ejecutivo; subtipo paraestatal/desconcentrado por patrón).

## Subdominios → entidad / municipio (`sitios/subdominios/slugs.json`)

La columna `dependencia_o_estado` de `subdominios-consolidado.csv` es el slug del dominio (la
etiqueta antes de `.gob.mx`: `cdmx`, `nuevo-leon`, `monterrey`, `asenl`, `sat`…). `slugs.json`
mapea a mano `estados` (slug → entidad: gobierno estatal y sus órganos) y `municipios`
(slug → [entidad, municipio INEGI]). Solo slugs inequívocos: homónimos (guadalupe, santiago,
allende…), alcaldías de CDMX y dependencias federales quedan sin asignar. La cobertura se publica
en `window.GOBMX.subdominios.mapeo_lugar`.

## Comparación entre entidades y municipios

`gobmx.py comparar` / tool MCP `comparar` / bloques `entidades` y `municipios` de `web/data.js`
salen de la misma función (`gobmx.metricas`). Solo se compara **estatal↔estatal** o
**municipal↔municipal**; el orden federal se rechaza (presupuesto, extensión y población no
comparables). Métricas: apps, apps activas, instalaciones (Play), sitios, subdominios mapeados,
cobertura de poderes (de 4, con ≥1 app o sitio) y, si existe `datos/presupuesto/{entidades,municipios}.json`,
tasas por 100 mil habitantes (Censo 2020) y por cada mil millones de pesos de egreso (INEGI EFIPEM).
Sin dato de presupuesto las tasas son `null`, nunca 0.
