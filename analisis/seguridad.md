# Hallazgos transversales de seguridad y gobernanza

**Corte:** 2026-10-20. Todo esto sale de **observación pasiva de fuentes públicas**: metadatos de
tiendas, Certificate Transparency (base pública de crt.sh) y un GET a páginas públicas. No se escaneó
infraestructura, no se probó ningún login ni se enviaron datos. Son señales para que la dependencia
revise, no vulnerabilidades confirmadas ni explotadas.

## 1. Entornos de prueba y sistemas internos visibles en Certificate Transparency

Al emitir un certificado TLS, el nombre del host queda público en los registros de CT para siempre.
Varias dependencias emiten certificados para hosts que delatan infraestructura interna o de prueba:

| Dependencia | Hosts observados en CT | Por qué importa |
|---|---|---|
| SAT | ~30 hosts `dev`/`uat` (digitaldev, digitaluat, `*.opv4dev`, buzondigitaldev, aduportaluat, everestuat) | Entornos no productivos nombrados públicamente |
| IMSS | `webmail.imss.gob.mx`, `ssoadmin.imss.gob.mx` | Correo web y admin de SSO expuestos por nombre |
| Campeche | `llave.pruebas.campeche.gob.mx` | Instancia de **pruebas** del sistema de identidad |
| Durango | `loginrecaudador`, `recaudador`, `sistemaingresos` | Logins de recaudación nombrados |
| Guanajuato | `api-sfia-dgi-tramites-{citas,ciudadano,consulta,gestion,solicitudes}`, `admin-sfia-tramites`, `apidoc-sfia-tramites` | Topología completa del backend de trámites |
| Oaxaca | `coolify-apitramitesdigitales`, `db-apitramitesdigitales` | Deploy en PaaS Coolify y **host de base de datos** nombrado |
| Hidalgo | `otrsfinanzas`, `otrshacienda` (OTRS), `bihacienda`, `bifinanzas` (BI) | Ticketing y BI de hacienda |
| Quintana Roo | `egresos-sefiplan`, `opergob`, `correspondencia`, `mail.sefiplan` | Ecosistema interno de finanzas; `ventanilladigital` en Railway (PaaS externo) |

Nombrar un host en CT no lo hace vulnerable, pero reduce el trabajo de reconocimiento de un atacante y
sugiere que entornos de prueba conviven con producción sin separación de dominios.

## 2. TLS obsoleto, incompleto o mal emitido

| Portal | Problema | Observado |
|---|---|---|
| REPUVE | Apache 2.4.6 + **OpenSSL 1.0.1e-fips** (EOL ~2014) en :8443 | federal |
| Cédula profesional (SEP) | cadena TLS **incompleta** (falta intermedio), nginx 1.17.1 | federal |
| DOF (`www.dof.gob.mx`) | certificado SAN mal emitido (solo sirve el apex) | federal |
| Querétaro — `transparencia.queretaro.gob.mx` | certificado **vencido** | estatal |
| Coahuila — `www.coahuila.gob.mx` | certificado no coincide con el host | estatal |
| BC — `www.identidadbc...` | certificado no coincide (¡es el de identidad digital!) | estatal |
| Colima — `www.transparencia.col.gob.mx` | certificado no coincide | estatal |
| Nayarit — `www.nayarit.gob.mx` | error de versión de protocolo TLS | estatal |
| Veracruz (apex y www) | "unable to verify the first certificate" (cadena incompleta) | estatal |

## 3. Stacks en fin de vida (banners públicos)

- **PHP 5.4.45** (EOL 2015) — portal de Coahuila.
- **PHP 5.6.40** (EOL 2018) — `tramitesbasicos` de Quintana Roo.
- **Oracle Application Server 11g** (legacy) — servicios digitales del IMSS.
- **Apache 2.4.6 / OpenSSL 1.0.2k / PHP 7.1.1** — portal de Michoacán.
- **Payara 4.1.1** con banner "badassfish" expuesto — `ipagos` de Chihuahua.
- **`cgiip.exe`** (CGI legado tipo ISAPI) — portal municipal de SLP capital.

## 4. Apps: huella de proveedor descuidada

- **Paquetes de preproducción en producción:** `com.qvantel.bienestar.preprod` (Internet para el
  Bienestar / CFE TEIT), con **+100,000 instalaciones**. El sufijo `preprod` en una app masiva sugiere
  que se publicó un build de entorno de pruebas.
- **Nombres de paquete de prueba:** `com.mycompany.appprueba`, `com.anonymous.appjeje` en apps
  estatales — plantillas de framework sin renombrar.
- **Soporte en Gmail:** Guardia Nacional y REFAyGN (SEDENA) usan direcciones `@gmail.com` como contacto
  oficial en la ficha de tienda.
- **Prefijo heredado:** Financiera para el Bienestar (Finabien) aún publica bajo paquete `telecomm`.
- **Proveedores recurrentes** detrás de muchas apps estatales de seguridad: Seguritech, CityShob,
  Hitech, Cosmocolor, Egob-Express. Centinela Chihuahua está ligada a la plataforma de vigilancia
  Centinela (Seguritech).
- **Apps publicadas bajo la cuenta del proveedor, no del gobierno:** TSUNAMI MX (SEMAR, vía Tensegrity
  Services), Urbani (NL, Inatel), Mi Macro Periférico (Idear Electrónica), ECOBICI (Lyft), SIAT
  Monterrey (Soluciones SIG), Licencia Digital Tlaxcala (DC Soluciones).

## 5. Fallas funcionales y de privacidad reportadas (fuentes públicas)

- **ConsulApp Contigo (SRE):** una revisión interna reportada por prensa indicó que el botón de auxilio
  mostraba confirmación al usuario **sin notificar realmente** al Centro de Información y Asistencia a
  Mexicanos (CIAM).
- **Apoyo Ciudadano (INE):** en 2017 se denunció que las fotos de credenciales **quedaban almacenadas**
  en los teléfonos de los auxiliares; fallas adicionales en 2017 y 2023; ~52 mil firmas irregulares en
  la revocación de mandato.
- **Banco del Bienestar:** quejas recurrentes por saturación y cierres de sesión (2024, 2025).
- **Ko'ox / Koox Contigo (Campeche):** el Congreso estatal pidió revisar su manejo de datos personales.
- **Identidad Digital BC:** quejas de usuarios sobre funcionamiento.

## 6. Bloqueo a clientes no-navegador (no es falla, es configuración)

Infonavit (completo), `presidente.gob.mx` y Banco del Bienestar responden 403/timeout tras Akamai a
clientes que no son navegador. Es defensa anti-bot legítima, pero impide verificación automatizada y
monitoreo de disponibilidad por terceros.

## 7. Posible defacement de contenido

- **Tlajomulco:** enlaces de spam/SEO inyectados en la sección "Plataforma Nacional de Transparencia"
  del portal — señal de compromiso de contenido o de un plugin vulnerable.

## 8. Cambios institucionales ya visibles en los dominios

No es seguridad, pero importa para cualquier integración:
- `cjf.gob.mx` → redirige a `oaj.gob.mx` (reforma judicial: CJF → Órgano de Administración Judicial).
- SFP → Secretaría Anticorrupción y Buen Gobierno (`gob.mx/buengobierno`).
- CONACYT → SECIHTI, que **redirige fuera de `.gob.mx`** a `secihti.mx` (WordPress/LiteSpeed).
- **IFT e INAI extintos** (reforma de autónomos) con portal aún en línea; funciones migran a ATDT y SABG.
- IMPI: `marcanet.impi.gob.mx` ya no resuelve en DNS; migró a `marcia.impi.gob.mx`.

---

### Recomendación de uso

Cada fila de este documento tiene su evidencia fechada en los JSON (`sitios/*.json` campo `estado_real`,
`apps/apps.json`). Antes de actuar sobre cualquier hallazgo, cruzarlo contra la fuente viva: una app o
portal cambia de un día a otro. Este corte es del 2026-10-20.
