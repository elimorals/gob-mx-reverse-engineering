# Presencia digital del gobierno de México — comparación a detalle

**Corte:** 2026-10-20. **Método:** observación pasiva de fuentes públicas (tiendas de apps,
Certificate Transparency, un GET a páginas públicas) + búsqueda web. Sin escaneo intrusivo,
login ajeno ni envío de datos personales.

**Cobertura del inventario:** 466 apps únicas · 231 portales web · 12,812 subdominios `.gob.mx` (6,036 propios por CT + dotgob-mx)
vistos en Certificate Transparency. Los datos crudos están en `apps/`, `sitios/` y `servicios/`;
esto es la lectura.

> Aviso de completitud: "no encontrado" no es "no existe". Las tiendas (Google Play 429, App Store
> 403) y crt.sh (502) limitaron solicitudes durante la recolección. Cada hueco está marcado en los
> JSON. Las cifras son piso, no techo.

---

## 1. Panorama en números

### Apps por nivel de gobierno

| Nivel | Apps | % |
|---|---:|---:|
| Estatal | 277 | 59% |
| Federal (secretarías) | 64 | 14% |
| Municipal | 64 | 14% |
| Paraestatal | 38 | 8% |
| Autónomo | 19 | 4% |
| No oficial (imita a una institución) | 4 | 1% |

### Apps por sector

| Sector | Apps | | Sector | Apps |
|---|---:|---|---|---:|
| Otro | 99 | | Finanzas | 20 |
| Seguridad (911/botón/C5) | 95 | | Fiscal | 15 |
| Movilidad/transporte | 52 | | Clima | 13 |
| Trámites (ventanilla) | 33 | | Vivienda | 13 |
| Salud | 33 | | Identidad | 12 |
| Educación | 32 | | Energía | 12 |
| Turismo | 23 | | Trabajo | 11 |
| | | | Elecciones | 5 |

**Lectura:** el grueso no es trámite ni identidad, es **seguridad** (95 apps de 911 / botón de pánico /
C5). Es el sector con más apps y, a la vez, de los peor calificados (ver §4): casi todos los estados
tienen su propia app de pánico, casi ninguna funciona bien.

### Cobertura por plataforma

- **Android:** 351 apps (75%) · **iOS:** 326 (70%) · **ambas:** 246 (53%).
- Una de cada dos apps de gobierno vive en una sola tienda. Las solo-iOS son comunes a nivel estatal
  (Sinaloa solo publica en iOS); las solo-Android abundan en municipios.

### Estatus

| Estatus | Apps | |
|---|---:|---|
| Activa | 292 | 63% |
| Desconocido | 78 | 17% |
| **Sin actualizar >2 años** | **76** | **16%** |
| **Retirada** | **20** | **4%** |

**Uno de cada cinco productos (96 apps) está abandonado o muerto** pero varios siguen publicados y
descargables. Abandonware de gobierno: sigue pidiendo permisos y datos sin nadie detrás.

---

## 2. Las que sí importan (por adopción real)

Top 10 por instalaciones reales en Android. La presencia digital del Estado se concentra en un puñado
de apps **federales de dinero y salud**; todo lo demás es cola larga.

| Instalaciones | App | Dependencia |
|---:|---|---|
| 37.4 M | CFE Contigo | CFE |
| 35.4 M | Banco del Bienestar Móvil | Banco del Bienestar |
| 32.3 M | IMSS Digital | IMSS |
| 22.1 M | AforeMóvil | CONSAR / Procesar |
| 12.3 M | SAT Móvil | SAT |
| 8.6 M | Mi Cuenta Infonavit Móvil | Infonavit |
| 7.2 M | BilletesMx | Banxico |
| 6.4 M | App CDMX | CDMX / ADIP |
| 2.9 M | Urbani (transporte NL) | *proveedor privado* |
| 2.1 M | Licencia Federal Digital | SICT |

Fuera del top: **la única app subnacional que compite con las federales es App CDMX.** Ningún otro
estado ni municipio tiene una app con tracción comparable. El décimo lugar lo ocupa una app que
**publica un proveedor privado**, no el gobierno.

---

## 3. Sitios web: qué se encontró

231 portales. Todos los 32 estados, la CDMX y los 25 municipios grandes **tienen portal**: no hay
entidad sin presencia web. El problema no es ausencia, es **estado**.

### Plataformas (las identificables)

| Familia | Portales |
|---|---:|
| CMS federal gob.mx | 31 |
| WordPress | ~22 |
| ASP.NET / IIS | ~15 |
| Drupal | ~10 |
| Joomla | ~7 |
| Node/React/Next/Angular | ~7 |
| CMS propio CDMX (October CMS) | 6 |
| Desconocido / tras WAF | ~54 |

El federal está relativamente estandarizado (CMS gob.mx). **Estados y municipios son un mosaico sin
norma común:** desde Next.js en Vercel (Morelia) hasta PHP legado con `cgiip.exe` (SLP capital) y
Payara con el banner "badassfish" expuesto (Chihuahua).

### Autenticación e identidad digital

- **151 portales no piden cuenta** (consulta pública o informativos).
- Identidad digital fragmentada: **Llave MX** (federal), **Llave CDMX**, **Identidad Digital BC**,
  **Gobierno Digital EdoMex**, Nayarit, Morelia ID… cada quien su SSO. No hay una identidad única.

---

## 4. Calidad: el patrón se repite

**73 apps tienen calificación menor a 3.0 en Google Play** (de las que tienen reseñas). No son casos
aislados; es el estado normal de la app subnacional. Las peores son, en orden:

| Score | App | Qué es |
|---:|---|---|
| 1.2 | Gasoapp | Precios de gasolina (CRE) |
| 1.2 | Mi IFT | Herramientas usuario (IFT, **ya extinto**) |
| 1.3 | Mi Macro Periférico | Transporte Guadalajara |
| 1.5 | Taxi Campeche | Transporte |
| 1.6 | Chihuahua Pagos 2.0 | Pagos municipales |
| 1.7 | 911 CDMX | Emergencias |
| 1.7 | Guadalajara App | Ciudadana municipal |
| 1.9 | VUCEM Móvil | Comercio exterior (federal) |

Los sectores que concentran las malas notas: **transporte, pagos municipales y emergencias (911).**
Justo los de contacto diario con el ciudadano.

---

## 5. Qué servicios FALTAN (brechas)

Cruzando apps + sitios + lo que cada dependencia ofrece:

### 5.1 Dependencias federales grandes sin app
SEGOB, SEP, Secretaría de Salud (la dependencia, no el IMSS), Bienestar, Economía, SEDATU, Secretaría
de las Mujeres, SECIHTI, INM, CONAPRED, CENAPRED, CONADE. Varias se apoyan solo en el portal web.

### 5.2 Transporte masivo sin app oficial
Metro CDMX, Metrobús, Cablebús, Mi Tren/SITEUR (GDL), Mexibús, Metrorrey, RUTA (Puebla). Donde hay
app de transporte, con frecuencia **la publica un proveedor privado** (Urbani, Mi Macro, ECOBICI/Lyft,
tarjeta Movimex en Stori), no el gobierno. La tarjeta de transporte como producto privado tercerizado
es el patrón dominante.

### 5.3 Servicios que existen en web pero NO en app (o al revés)
- **DIF:** ningún estado tiene app del DIF. Servicio social ausente del canal móvil.
- **Agua estatal:** solo aparecen organismos sueltos (JMAS Juárez, SIAPA, CESPT, JCAS). La mayoría no
  tiene canal digital de consulta/pago de agua.
- **Fiscalías/denuncia:** muy pocas apps (IdSonora, alguna más). La denuncia en línea vive en web con
  CAPTCHA, no en app.
- **Salud estatal:** tras bajar las apps de COVID, casi no queda app de salud subnacional.

### 5.4 Pago en línea intermitente
Varios portales de pago estaban "en mantenimiento" o caídos el día del corte (SACMEX 503, Chihuahua y
Hermosillo "pago en línea en mantenimiento", hacienda de Chiapas resetea conexión).

---

## 6. Dónde está, dónde no: mapa estado por estado (apps)

| Mucho (≥15) | Medio (7–14) | Poco (≤6) |
|---|---|---|
| Tamaulipas (18), Hidalgo (17), Jalisco (17), Chihuahua (16), Sonora (16), Chiapas (15), CDMX (15) | Guanajuato (12), Querétaro (11), Quintana Roo (11), BC (10), Campeche (10), Tabasco (10), Veracruz (10), Aguascalientes (9), Tlaxcala (9), Edomex (8), Nuevo León (7) | Guerrero, Michoacán, Oaxaca (6); Puebla, SLP (5); Coahuila, Durango, Morelos, Yucatán, Zacatecas (4); Sinaloa (3); BCS, Nayarit (2); **Colima (1)** |

**Que un estado tenga muchas apps no significa que sean buenas** (Chihuahua: 16 apps, varias con score
<2). Y los grandes por población no lideran: **Nuevo León tiene 7, Estado de México 8.** Colima tiene
una sola app (emergencias).

---

## 7. Cruce con Skills_MX (tu proyecto)

[Skills_MX](https://github.com/elimorals/Skills_MX) ya tiene **83 MCP servers / 417 tools** que operan
contra una parte de estos portales. Este inventario sirve para priorizar qué MCP falta construir:

- **Ya cubierto por MCP:** SAT, IMSS, Infonavit, CFE, CURP/RENAPO, DOF, Banxico, CONAGUA/REPDA,
  COFEPRIS, CONDUSEF, CNBV, CRE, IMPI, INE, SEP (cédula), REPUVE, REPSE, SEDATU, no-penales, Llave MX,
  predial/multas municipales de CDMX, GDL, Monterrey, Mérida, Querétaro, Puebla, Tijuana, EdoMex.
- **Sin MCP y con demanda clara:** municipios grandes sin predial (Morelia, Hermosillo, Culiacán,
  Cancún, Saltillo, Torreón, Aguascalientes, San Nicolás, Mexicali, San Pedro, Chihuahua); agua
  estatal fuera de los 4 organismos ya cubiertos; identidad digital estatal (BC, EdoMex); VUCEM.

El repo es el **mapa**; Skills_MX es la **interacción**. Cada portal en `sitios/*.json` trae en `notas`
el MCP correspondiente cuando existe.

---

## 8. Hallazgos de seguridad y gobernanza

Detalle completo en [`seguridad.md`](seguridad.md). Resumen:

- **Entornos de prueba y sistemas internos expuestos en Certificate Transparency:** SAT (~30 hosts
  dev/uat), IMSS (`webmail`, `ssoadmin`), Campeche (`llave.pruebas`), Durango (logins de recaudación),
  Guanajuato (backend SFIA nombrado), Oaxaca (host de BD), Hidalgo (OTRS/BI de hacienda), QRoo (SEFIPLAN).
- **TLS obsoleto o roto:** REPUVE (OpenSSL 2014, EOL), cédula profesional SEP (cadena incompleta), DOF
  (certificado mal emitido), varios portales estatales con certificado vencido o que no coincide.
- **Stacks al final de su vida:** PHP 5.4 (Coahuila), PHP 5.6 (QRoo), Oracle App Server 11g (IMSS),
  Apache 2.4.6.
- **Apps publicadas por proveedores con huella descuidada:** nombres de paquete de preproducción
  (`com.qvantel.bienestar.preprod` con +100k instalaciones) o de prueba (`com.mycompany.appprueba`),
  contactos de soporte en Gmail (Guardia Nacional, SEDENA), proveedores recurrentes (Seguritech,
  CityShob, Hitech).
- **Fallas funcionales reportadas:** ConsulApp (SRE) confirmaba el botón de auxilio sin avisar al
  centro consular; Apoyo Ciudadano (INE) dejaba fotos de credenciales en los teléfonos.
- **Posible defacement de contenido:** Tlajomulco con enlaces de spam/SEO inyectados en transparencia.

---

## 9. Conclusiones

1. **La presencia digital del Estado mexicano es amplia pero poco profunda.** 466 apps y 231 portales,
   pero el uso real se concentra en ~8 apps federales de dinero y salud.
2. **El nivel subnacional produce mucho y mantiene poco:** 59% de las apps son estatales, y es ahí
   donde se concentran el abandono (16% sin actualizar >2 años) y las malas calificaciones.
3. **Seguridad como el sector más grande y peor ejecutado:** 95 apps de 911/pánico, casi todas mal
   calificadas.
4. **No hay norma técnica común subnacional:** plataformas, identidad y calidad varían por capricho de
   cada administración.
5. **La tercerización es la regla en transporte** y deja huella: apps bajo cuentas de proveedores,
   paquetes de prueba, soporte en Gmail.
6. **La deuda de seguridad es estructural:** TLS y stacks EOL, y entornos internos visibles en
   Certificate Transparency sin que nadie los oculte.
