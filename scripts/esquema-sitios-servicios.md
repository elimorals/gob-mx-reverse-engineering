# Esquema: sitios web y servicios digitales

Inspirado en la sección "Estado real" de los README de [Skills_MX](https://github.com/elimorals/Skills_MX):
cada afirmación sobre un portal lleva fecha, URL y resultado observado.

## `inventario/sitios/<segmento>.json` — lista de objetos

```json
{
  "dependencia": "Servicio de Administración Tributaria",
  "siglas": "SAT",
  "nivel": "federal | autonomo | paraestatal | estatal | municipal | poder_legislativo | poder_judicial",
  "estado": "Nacional | <entidad>",
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
  "nivel": "...", "estado": "...",
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
