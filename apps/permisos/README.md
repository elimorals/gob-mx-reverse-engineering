# Capa de permisos y privacidad — apps del gobierno de México

Fecha: 2026-10-21 · Alcance: **351 apps con Android** (solo México) · Sin descarga ni ejecución de APKs.

> Cobertura: las **20** más instaladas / sensibles se curaron a detalle (incluye el juicio "no cuadra con el propósito"); las otras **331** se clasificaron de forma **mecánica** a partir de los grupos de permisos de Google Play. 311 de 351 declaran algún permiso peligroso. Los hallazgos cualitativos de abajo son de las 20 curadas.

## Qué es esto

Para cada app se listan los **permisos peligrosos** (dangerous permissions de Android)
que declara en Google Play y se marca cuáles **no cuadran con el propósito** de la app.
Todo con fuentes públicas que no requieren el binario.

Resultado por app en `permisos.json`.

## Selección de apps (20)

- **15 más instaladas** con `android_id`, ordenadas por `play.realInstalls` de `apps/apps.json`:
  CFE Contigo, Banco del Bienestar, IMSS Digital, AforeMóvil, SAT Móvil, Mi Cuenta Infonavit,
  BilletesMx (Banxico), App CDMX, Urbani, Licencia Federal Digital, BanjeCel, Mi Policía,
  911 CDMX, Valida INE-QR, Tarjeta Rosa.
- **5 de sector sensible** (identidad / seguridad / pánico) aunque con menos instalaciones:
  Llave EdoMex (identidad), Identidad Digital BC (identidad), Seguridad Inmediata (botón de alerta),
  REFAyGN (SEDENA), Botón de Auxilio Escudo Urbano (pánico C5 Jalisco).

## Fuentes y método

1. **Permisos declarados — Google Play** (`google_play_scraper.permissions`, lang=es, country=mx).
   Devuelve las categorías y las cadenas en español que Play muestra al usuario. Se mapean a
   las constantes de Android y se clasifican las peligrosas:
   `ACCESS_FINE/COARSE_LOCATION`, `CAMERA`, `RECORD_AUDIO`, `READ_CONTACTS`, `GET_ACCOUNTS`,
   `READ_PHONE_STATE`, `CALL_PHONE`, `READ/WRITE_EXTERNAL_STORAGE`, `READ/WRITE_CALENDAR`.
   Las 20 apps devolvieron permisos correctamente.
2. **Trackers + permisos del APK — Exodus Privacy**: **no disponible**. La API pública
   (`/api/search/<id>`) hoy responde **401 Unauthorized** (requiere token de cuenta registrada),
   y las páginas HTML de reporte (`/en/reports/<id>/latest/`) devuelven **contenido señuelo
   anti-scraping** (texto aleatorio, no el reporte). Por eso `trackers: []` en todas y la
   fuente es solo `["google-play"]`. **No se inventó ningún tracker.**

### Cómo se decide "no cuadra con el propósito"

A cada app se le asigna un tipo (emergencia, financiera, fiscal, identidad, transporte,
portal, super-app, realidad aumentada, programa social, utility, seguridad) y un conjunto de
permisos peligrosos **razonables** para ese tipo. Los que se declaran fuera de ese conjunto se
marcan como injustificados. Ejemplos de criterio:
- **Emergencia / pánico / policía**: ubicación, cámara, micrófono, llamar y contactos SÍ cuadran.
- **Financiera / fiscal**: cámara (escaneo de documento/ID) y almacenamiento cuadran; micrófono,
  ubicación y contactos NO.
- **Identidad / lector QR**: cámara cuadra; ubicación, micrófono y contactos NO.
- **Realidad aumentada (BilletesMx)**: solo cámara cuadra.

Es una heurística declarativa: marca lo que **declara** Play, no el uso real en runtime
(para eso haría falta análisis dinámico del APK, fuera de este piloto).

## Hallazgos

### Permisos peligrosos injustificados (top)
Empate en 3 permisos injustificados cada una:
1. **IMSS Digital** (salud, 32M instalaciones) — pide **RECORD_AUDIO** (micrófono) y
   **READ/WRITE_CALENDAR** además de 10 permisos peligrosos en total. El micrófono en una app de
   derechohabientes del IMSS no tiene uso evidente.
2. **Banco del Bienestar** y **BanjeCel** (banca) — ambas piden **ubicación precisa + aproximada**
   y **READ_CONTACTS**. Un banco leyendo la agenda de contactos es la bandera más fuerte del lote.
3. **Licencia Federal Digital** (identidad/SCT, 2M) — una app que **muestra** un documento pide
   **ubicación + micrófono (RECORD_AUDIO)**.

Otros notables: **SAT Móvil** (fiscal) pide **micrófono**; **AforeMóvil / Infonavit** piden
ubicación precisa sin función de mapa aparente; **BilletesMx** (AR de Banxico) pide
almacenamiento más allá de la cámara.

### Micrófono (RECORD_AUDIO) sin propósito claro
Aparece en 4 apps donde no se ve para qué: **IMSS Digital, SAT Móvil, Licencia Federal Digital, Urbani**.

### Las que SÍ cuadran
Las apps de emergencia (**911 CDMX, Seguridad Inmediata, Mi Policía, Botón de Auxilio**) piden
ubicación, cámara, micrófono, llamar y contactos — todo coherente con un botón de pánico.
**Valida INE-QR** es el modelo de mínimo privilegio: solo **CAMERA**. **REFAyGN (SEDENA)** no
declara ningún permiso peligroso en Play.

### Trackers
**No se pudo determinar** por app: Exodus Privacy quedó inaccesible (ver Fuentes). El hallazgo de
"apps con más trackers" queda pendiente de una fuente con token de Exodus o de análisis directo
del APK (fuera del alcance de este piloto).

## Limitaciones

- Extendido a las 351 apps con `android_id`. Las 20 curadas traen juicio manual; las demás, clasificación mecánica.
- Sin datos de Exodus: no hay trackers ni el set de permisos extraído del APK (que suele ser más
  amplio que el que Play muestra al usuario).
- "No cuadra con el propósito" se juzga sobre permisos **declarados**, no sobre uso real.
- Google Play agrupa y traduce; cadenas sin mapeo conocido (Wi-Fi, "pulsar teclas", "recibir datos
  de Internet") no se cuentan como peligrosas.
