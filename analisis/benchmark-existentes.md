# Benchmark: ¿ya existe un inventario público de la presencia digital del gobierno de México?

**Fecha:** 2026-10-20
**Pregunta:** ¿Existe ya un directorio / repositorio / catálogo / base de datos público que categorice a detalle las APPS MÓVILES, SITIOS WEB y/o SERVICIOS en línea del gobierno de México (federal, estatal, municipal)? ¿Qué cubre cada uno, quién lo mantiene, y qué le falta frente a nuestro inventario (apps + sitios + servicios con evidencia técnica fechada: TLS, anti-bot, plataforma, subdominios de Certificate Transparency, cruce con MCPs)?

**Método:** WebSearch (modo extended) + verificación con WebFetch. Las URLs marcadas como verificadas se abrieron directamente. Dos portales oficiales (`catalogonacional.gob.mx`, `datos.gob.mx`) devolvieron **HTTP 403** a WebFetch — un dato en sí mismo: tienen anti-bot, justo una de las señales que nuestro inventario registra.

---

## Tabla comparativa

| # | Nombre | URL | Responsable | Qué cubre | Nivel de detalle | Vigente | Licencia | En qué se queda corto (vs. nuestro repo) |
|---|--------|-----|-------------|-----------|------------------|---------|----------|------------------------------------------|
| 1 | **dotgob-mx** (lo más parecido al eje de subdominios) | github.com/AlejandroTC/dotgob-mx ✅ verificado | Individual (AlejandroTC), **no oficial** | **Sitios/host**: subdominios `*.gob.mx` (federal/estatal/municipal, infra, correo) | Lista de hosts. 12,662 subdominios hallados, 4,910 "activos" (responden HTTP/S). "Activo" = responde (incluye 401/403/5xx, páginas default, errores CDN/DNS) | Sí. GitHub Action mensual (día 1). Corte 13/10/2026, 4 commits | MIT | Solo hosts, **sin apps ni servicios/trámites**. Sin categorización por servicio. **Sin TLS, sin fingerprint de plataforma, sin anti-bot, sin fecha por-host**. Mismo insumo que usamos (CT vía subfinder+httpx) pero sin la capa de evidencia |
| 2 | **Catálogo Nacional de Regulaciones, Trámites y Servicios (CNARTyS)** — antes CNTSE; incluye RFTS | catalogonacional.gob.mx/Buscador ⚠️ 403 a bot | CONAMER (federal) | **Servicios/trámites** de los 3 niveles de gobierno (requisitos, costos, pasos). Fuente legal: Ley Gral. de Mejora Regulatoria arts. 38-63 | Alto a nivel trámite (requisitos/costos/fundamento legal). Es el "registro legal" del trámite | Sí, es el catálogo oficial vigente | Datos públicos de gobierno | Es registro **jurídico-administrativo del trámite**, no un inventario **técnico**. **No cataloga apps ni la URL/host que presta el servicio**, ni TLS/plataforma/anti-bot. No lista sitios web como activos |
| 3 | **datos.gob.mx** (portal de datos abiertos) | datos.gob.mx ⚠️ 403 a bot | Gobierno federal (ATDT/coordinación datos abiertos). Corre CKAN | **Datasets**, no apps/sitios/servicios | ~1,652 datasets vía API CKAN `/api/3/action` (una fuente); otra nota reporta ~4,875 de 170 instituciones y un CKAN viejo de ~1,068. **Cifras en conflicto** | Parcialmente; históricamente intermitente (hay repos que "lo mantienen vivo") | Datos abiertos | No es inventario de presencia digital; es catálogo de conjuntos de datos. No tiene apps, ni TLS, ni host-level |
| 4 | **gob.mx/apps** (catálogo federal de apps) — **aparentemente extinto** | gob.mx/apps ⚠️ timeout / ya no visible | Gobierno federal | **Apps móviles** aprobadas | En 2019 (paper UNAM) listaba **38 apps de 17 instituciones**. Estándar 2017 mencionaba 14 apps certificadas | **No vigente / no verificable.** El home de gob.mx hoy es buscador de trámites; no se ve catálogo de apps | — | Si existió, era solo lista de apps federales (sin estatales/municipales), sin evidencia técnica. Hoy no hay sustituto público |
| 5 | **Programa Sectorial ATDT 2025-2030** | dof.gob.mx nota 5768198 (19/09/2025) | ATDT (José A. Peña Merino) | Estrategia/política (identidad digital, Llave MX, trámites digitalizados) | Documento de política, no inventario | Vigente (publicado 2025) | Oficial | No es un inventario; es el plan. No lista apps/sitios/servicios concretos con evidencia |
| 6 | **Buscador gob.mx (trámites federales + programas)** | gob.mx/busqueda ✅ verificado | Gobierno federal / ATDT | **Servicios/trámites federales** y programas sociales | Buscador orientado al ciudadano (CURP, pasaporte, IMSS, etc.) | Vigente | — | **Explícitamente excluye trámites estatales y municipales.** No lista apps. Sin evidencia técnica |
| 7 | **Sociedad civil (R3D, SocialTIC, Fundar, Codeando MX)** | r3d.mx, socialtic.org, etc. | ONGs | Vigilancia, privacidad, gobernanza de datos; Codeando MX = datos abiertos/hackatones | Investigaciones puntuales (p.ej. Pegasus: permisos de micrófono/cámara/contactos) | Activas pero temáticas | Varía | **No hay auditoría pública sistemática de permisos/privacidad de apps gubernamentales MX** catalogada como inventario. Trabajo por caso, no censo |
| 8 | **OCDE / OCDE-BID Digital Government Index** | oecd.org (DGI 2025, OCDE-BID 2023) | OCDE / BID | Ranking/índice de madurez de gobierno digital | Scores por país/dimensión (MX 0.51 en DGI 2025, bajo promedio OCDE 0.70) | Vigente (ediciones 2023-2026) | Publicaciones OCDE | Es **índice de política**, no inventario de activos. No lista apps/sitios/servicios ni evidencia técnica |

### Comparadores internacionales (modelo, no de México)

| Nombre | URL | Responsable | Qué es | Nota para comparar |
|--------|-----|-------------|--------|--------------------|
| **cisagov/dotgov-data** | github.com/cisagov/dotgov-data ✅ verificado | CISA (gobierno EUA) | Lista **oficial** de dominios `.gov` (federal/estatal/tribal/ciudad/condado). Actualización **diaria**, CC0 | Análogo oficial de dotgob-mx. Solo dominios 2º nivel (no hosts), sin apps/servicios. Nota: "no todos los dominios corren un servicio" |
| **analytics.usa.gov** (DAP) | analytics.usa.gov | GSA/TTS (18F disuelto 01/03/2025) | Analítica web de >500 dominios federales / ~7000 hostnames | Dato de uso, no inventario con evidencia técnica. Dataset en data.gov desactualizado (feb-2022) |
| **GOV.UK Government service register / Service Manual** | registers.service.gov.uk, gov.uk/service-manual | Cabinet Office / GDS | Registro de servicios con dominio GOV.UK (174 registros, 5 campos) | **GOV.UK Registers deprecado desde 15/03/2021**. El register quedó estático (última act. jul-2017). Modelo centralizado que no cuajó |

---

## Prosa: qué hay y qué falta

**El espacio está fragmentado en tres silos que nunca se cruzan.** (1) Lo **jurídico-administrativo** del trámite vive en el CNARTyS/RFTS de CONAMER: dice qué pide un trámite, cuánto cuesta y su fundamento legal, pero no dice en qué URL/app se presta ni nada técnico. (2) Lo **de datos** vive en datos.gob.mx (CKAN): datasets, no presencia digital. (3) Lo **de infraestructura/host** solo existe de forma no oficial en **dotgob-mx**, un repo individual que enumera subdominios `.gob.mx` por Certificate Transparency (subfinder) y filtra con httpx. Nadie los une.

**Lo más parecido a nuestro repo es dotgob-mx**, y comparte exactamente nuestra misma técnica de descubrimiento (CT + probe HTTP). Pero se queda en la lista de hosts: 12,662 subdominios, 4,910 "activos" donde "activo" solo significa "responde algo" (incluye 401/403/5xx, páginas default, errores de CDN). **No tiene apps, no tiene servicios/trámites, no categoriza, y sobre todo no tiene la capa de evidencia que define nuestro inventario**: sin TLS fechado, sin fingerprint de plataforma/tecnología, sin detección de anti-bot, sin fecha de verificación por host. Es decir, dotgob-mx produce el *insumo crudo* (el eje subdominios-CT) que nuestro repo *enriquece*.

**El catálogo federal de apps (gob.mx/apps) está de facto muerto.** Hubo uno: un paper de UNAM (2019) documenta 38 apps de 17 instituciones, y el estándar de 2017 hablaba de 14 apps certificadas. Hoy el home de gob.mx es un buscador de trámites y no se ve catálogo de apps; WebFetch a gob.mx/apps dio timeout. **No existe hoy ningún inventario público de apps móviles del gobierno mexicano** — ni federal, y mucho menos estatal/municipal. Hay que ir tienda por tienda (App Store / Google Play por dependencia: CDMX, EdoMex, IMSS, SAT, Infonavit…).

**La sociedad civil no ha hecho el censo.** R3D, SocialTIC, ARTICLE 19 han hecho investigación potente de vigilancia/privacidad (Pegasus, permisos abusivos, Código Fiscal), y Codeando México trabaja datos abiertos — pero **no hay una auditoría sistemática y catalogada de permisos/privacidad de las apps gubernamentales** como inventario reutilizable. Es trabajo por caso, no censo.

**Lo internacional confirma el patrón y el hueco.** EUA (cisagov/dotgov-data, CC0, diario) y Reino Unido (GOV.UK register) son listas **oficiales de dominios/servicios**, no inventarios técnicos con evidencia por host; y el modelo centralizado de registers de GOV.UK se deprecó en 2021. Ninguno cruza apps + sitios + servicios + evidencia técnica fechada.

**Dato colateral relevante:** `catalogonacional.gob.mx` y `datos.gob.mx` devolvieron **403 a un bot**. Eso valida que el campo de "anti-bot" de nuestro inventario captura algo real y no documentado en ningún otro lado.

---

## Respuesta directa (5-8 líneas)

**¿Existe ya algo equivalente a nuestro repo?** No. Hay tres silos oficiales que no se cruzan (CNARTyS = trámites jurídicos, datos.gob.mx = datasets, buscador gob.mx = trámites federales sin estatal/municipal) y un repo individual no oficial para subdominios. Ninguno junta apps + sitios + servicios con evidencia técnica. **Lo más parecido es dotgob-mx** (github.com/AlejandroTC/dotgob-mx, MIT, mensual): usa nuestra misma técnica (Certificate Transparency + httpx) y lista ~4,910 hosts activos, pero **le falta todo lo que nos distingue**: apps, servicios, categorización, y la capa de evidencia (TLS, plataforma, anti-bot, fecha por host). El catálogo federal de apps (gob.mx/apps) está extinto; no hay sustituto público. **Nuestro repo sí aporta algo nuevo:** es el único que (a) cruza las tres capas — apps + sitios + servicios —, (b) adjunta evidencia técnica fechada por activo (TLS, anti-bot, plataforma, subdominios de CT) y (c) la cruza con MCPs. En términos simples: dotgob-mx y CONAMER producen insumos crudos; nuestro inventario es la capa de enriquecimiento que nadie más tiene.

---

## Fuentes

- [github.com/AlejandroTC/dotgob-mx](https://github.com/AlejandroTC/dotgob-mx) (verificado)
- [github.com/cisagov/dotgov-data](https://github.com/cisagov/dotgov-data) (verificado)
- [gob.mx/busqueda — buscador de trámites](https://www.gob.mx/busqueda) (verificado; excluye estatal/municipal)
- [Guía del CNTSE — gob.mx/wikiguias](https://www.gob.mx/wikiguias/articulos/guia-del-catalogo-nacional-de-tramites-y-servicios-del-estado-cntse-174035)
- [CNARTyS / CONAMER (consulmex SRE)](https://consulmex.sre.gob.mx/milan/index.php/es/avisos/148-catalogo-nacional-de-regulaciones-tramites-y-servicios-cnartys-de-la-comision-nacional-de-mejora-regulatoria-conamer)
- [Programa Sectorial ATDT 2025-2030 — DOF 19/09/2025](https://dof.gob.mx/nota_detalle.php?codigo=5768198&fecha=19%2F09%2F2025)
- [api-evangelist/datos-gob-mx (perfil de la API CKAN)](https://github.com/api-evangelist/datos-gob-mx)
- [chekos/datos-gob-en-vivo-2026 — nota sobre plataformas datos.gob.mx](https://github.com/chekos/datos-gob-en-vivo-2026/blob/main/docs/00-nota-sobre-plataformas-datos-gob-mx.md)
- [18F — a complete list of .gov domains (2014)](https://github.com/18F/18f.gsa.gov/blob/master/_posts/2014-12-18-a-complete-list-of-gov-domains.md)
- [analytics.usa.gov dataset — data.gov](https://catalog.data.gov/dataset/analytics-usa-gov)
- [GOV.UK Government service register — data.gov.uk](https://www.data.gov.uk/dataset/8b41775a-4d5d-4f2e-a521-a648a9d48616/government-service-register)
- [GOV.UK Registers deprecation](https://www.registers.service.gov.uk/registers/government-service)
- [OCDE Digital Government Outlook 2026: Mexico](https://www.oecd.org/en/publications/digital-government-outlook-2026_d46c0555-en/mexico_0be7c60e-en.html)
- [OCDE-BID Índice de Gobierno Digital ALC 2023 (PDF)](https://www.oecd.org/content/dam/oecd/es/publications/reports/2024/11/2023-oecd-idb-digital-government-index-of-latin-america-and-the-caribbean_5a9af6c4/7dc415b7-es.pdf)
- [R3D — Gobierno Espía (Pegasus, permisos de dispositivo)](https://r3d.mx/2017/06/19/gobierno-espia/)
- [SocialTIC — Gobernanza de Datos en México (PDF)](https://www.socialtic.org/wp-content/uploads/2022/03/Gobernanza_Democratica_Datos_Mexico_-carencias_oportunidades.pdf)
