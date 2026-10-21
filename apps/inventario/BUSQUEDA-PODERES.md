# Búsqueda dirigida de apps: poderes y autónomos

Fecha de búsqueda: **2026-10-21**. Tiendas: Google Play MX (`google_play_scraper`, lang=es, country=mx, 30 resultados) y App Store MX (iTunes Search/Lookup API, country=mx).
Apps nuevas registradas en `apps/inventario/poderes-autonomos.json`. Apps que ya estaban en `apps/apps.json` se marcan y no se duplican.

## Método y alcance (qué respalda un cero)

- **Play**: por cada celda estatal se buscaron 2 términos (ver tabla de términos) — 515 de 516 consultas respondieron; la única fallida fue `IVAI` (Veracruz/transparencia), pero `Transparencia Veracruz` sí respondió.
- **App Store**: la API de búsqueda devolvió HTTP 429 de forma sostenida. Cobertura iOS lograda: (a) búsqueda por celda con los mismos términos para las celdas marcadas `iOS✓`; (b) para **todas** las entidades, una búsqueda amplia por el nombre del estado (hasta 200 resultados) más búsquedas genéricas por tipo de ente (`Congreso`, `Congreso del Estado`, `Poder Judicial`, `Tribunal`, `Tribunal Electoral`, `Instituto Electoral`, `Instituto Estatal Electoral`, `Comisión de Derechos Humanos`, `Derechos Humanos`, `Instituto de Transparencia`, `Transparencia`, `Auditoría Superior`, `Legislatura`, `Tribunal de Justicia Administrativa`); (c) catálogo completo del desarrollador (lookup por artistId) de cada ente encontrado.
- Resultados filtrados por título/desarrollador y verificados a mano: solo cuenta como oficial si el desarrollador es el ente o la ficha remite a su dominio oficial.
- **Límite conocido**: una app con nombre comercial que no contenga el nombre del ente ni del estado puede no aparecer (ej.: `Violentómetro` de CODHECAM no salió con `CODHECAM` en Play, sí en iOS). Por eso “buscado, sin app oficial” significa *no encontrada con estos términos en ninguna de las dos tiendas*, no prueba absoluta de inexistencia.
- La matriz no incluye fiscalías (ya cubiertas en otros segmentos); se buscó `Fiscalía <estado>` en Play y no apareció ninguna fiscalía estatal nueva no registrada.

## Federal

| Ente | Resultado | Términos buscados |
|---|---|---|
| Cámara de Diputados | app encontrada: INFOPAL Móvil (iOS 6756138567); sin versión Play | Cámara de Diputados; Diputados México; Diputados; INFOPAL; Cámara de Diputados Gaceta Parlamentaria |
| Senado de la República | buscado, sin app oficial ("Mi Senado" es del Senado de Colombia) | Senado de la República; Senado México; Senado |
| Auditoría Superior de la Federación | app encontrada: App Ciudadana ASF (com.selbor.asf3882 / 1450877663); ASF Niños (com.asfmx.games / 6476572243) | Auditoría Superior de la Federación; ASF; Auditoría Superior |
| Canal del Congreso | app encontrada: Canal del Congreso (com.cic.canalcongreso / 1291590905) | Canal del Congreso; Cámara de Diputados |
| SCJN | app encontrada: Consulta de Expedientes (iOS 1336583126, sin actualizar desde 2018); sin versión Play | Suprema Corte de Justicia; Suprema Corte de Justicia de la Nación; SCJN; Consulta de Expedientes SCJN; Semanario Judicial; Suprema Corte |
| CJF / Órgano de Administración Judicial | FiREL PJF ya en apps.json; nuevas: Reforma Penal (iOS 1110860272, 2016) y Escuela Judicial en Línea (com.openlms.escuelajudicial, publicada por Open LMS) | Consejo de la Judicatura Federal; Órgano de Administración Judicial; Poder Judicial de la Federación; Sistema Electrónico PJF; Juicio en línea; Justicia Federal; Judicatura; Reforma Penal CJF |
| TEPJF | Tribunal Abierto ya en apps.json; nada nuevo (IUS Electoral es de Esfera Estudios, privado) | Tribunal Electoral del Poder Judicial; TEPJF; Tribunal Electoral |
| Tribunal de Disciplina Judicial | buscado, sin app oficial | Tribunal de Disciplina Judicial |
| Defensoría Pública Federal | buscado, sin app oficial | Defensoría Pública Federal; Instituto Federal de Defensoría; Defensoría Pública |
| CONEVAL | buscado, sin app oficial | CONEVAL |
| Tribunales Agrarios | buscado, sin app oficial | Tribunal Superior Agrario; Tribunales Agrarios; Tribunal Agrario |
| TFJA | buscado, sin app oficial | TFJA; Tribunal Federal de Justicia Administrativa |
| TFCA / Centro Federal de Conciliación | buscado, sin app oficial | Tribunal Federal de Conciliación y Arbitraje; Centro Federal de Conciliación |
| INE | nuevas: APPrende INE Proceso Local (mx.ine.app.apprendeine / 1548078530), INE (iOS 996781654, 2021), INE Maps (iOS 1441837963, 2019) | INE; Instituto Electoral |
| INEGI | nueva: Brújula INEGI (mx.org.inegi.dggma.movil.brujula); resto ya en repo | INEGI |
| CNDH / Banxico / COFECE / FGR | nada nuevo (lo hallado ya está en el repo) | CNDH; Banxico; COFECE; FGR |
| UNAM | nuevas (selección, no exhaustiva): Credencial SI, Descarga Cultura.UNAM, S.O.S UNAM. La UNAM tiene ~16 apps en iOS; no se cargaron todas para no saturar | UNAM |
| IPN / UAM | IPN Oficial ya en apps.json; UAM: sin app oficial de la UAM México | IPN; UAM |

## Entidades federativas

Leyenda: `encontrada` = app oficial (android / ios); `sin app` = buscado, sin app oficial; `iOS✓` = además hubo búsqueda iOS específica por celda.

| Entidad | Congreso / ASE | Poder Judicial / TSJ | OPLE | CEDH | Transparencia | Tribunal electoral |
|---|---|---|---|---|---|---|
| Aguascalientes | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ |
| Baja California | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ |
| Baja California Sur | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ |
| Campeche | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | encontrada: Violentómetro (CODHECAM) (com.violento.violentometro / 6469552531) | sin app iOS✓ | sin app iOS✓ |
| Chiapas | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ |
| Chihuahua | sin app iOS✓ | sin app iOS✓ | encontrada: IEE Chihuahua (ya en apps.json) | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ |
| Ciudad de México | sin app iOS✓ | encontrada: Firma.Judicial (mx.gob.cdmx.pjcdmx.firmajudicial / —) | encontrada: IECM Sistema Electrónico (SEI) (com.iecmutsi.seiiecm / —); SEI Offline (— / 6757507187); IECM (apoyo ciudadano / consultas) (— / 1334921386); CNNA IECM (com.iecm.cnna / 6786408788) | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ |
| Coahuila | sin app iOS✓ | encontrada: App Token PJ Coahuila (— / 1669177678) | sin app iOS✓ | sin app iOS✓ | sin app iOS✓ | sin app |
| Colima | sin app | sin app | sin app | sin app | sin app | sin app |
| Durango | sin app | sin app | sin app | sin app | sin app | sin app |
| Estado de México | sin app | encontrada: PJEdomex (com.pjedomex.pjedomex / 1398575467); SOS PJEdomex (com.pjedomex.sospjedomex.sospjedomex / 1587030797); EJEM (gob.mx.ejem.ejem / 1569203423) | sin app | sin app | sin app | sin app |
| Guanajuato | sin app | encontrada: Archivo Electrónico QR (mx.gob.poderjudicialgto.archivo_electronico_app_v2 / 6747139601); Archivo Electrónico PJEG (— / 1327933515); Botón de pánico PJEG (— / 6779694093) | sin app | sin app | sin app | sin app |
| Guerrero | sin app | sin app | sin app | sin app | sin app | sin app |
| Hidalgo | encontrada: DECIDASEH (— / 6476421353) | encontrada: APP-PJHIDALGO (com.pjhidalgo.portal.Portal / 1453894226); PJHGO (com.pjeh.app / —) | sin app | sin app | sin app | sin app |
| Jalisco | sin app | encontrada: Judicial TV Jalisco (mx.conceptowsmx.pjej / 6754987344) | sin app | sin app | sin app | sin app |
| Michoacán | sin app | encontrada: TRIBELEC (tribunal.electronico.michoacan2 / 1550547212); Temis Poder Judicial Michoacán (com.pjm.temis / 6550889063); CEDETICket (— / 6444897013) | encontrada: IEM Proceso 24-25 (— / 6744945327) | sin app | sin app | sin app |
| Morelos | sin app | sin app | sin app | sin app | sin app | sin app |
| Nayarit | sin app | sin app | sin app | sin app | sin app | sin app |
| Nuevo León | sin app | encontrada: Tribunal Virtual (com.test.tribunalvirtual / 870659641); SIS PJENL (gob.pjenl.www / 6447005027); Criterios PJENL (mx.gob.pjenl.criteriosmovil / 1534892623) | sin app | sin app | sin app | sin app |
| Oaxaca | sin app | sin app | sin app | sin app | sin app | sin app |
| Puebla | encontrada: App Ciudadana ASEP (mx.gob.auditoriapuebla.app1 / 6744423721) | sin app | sin app | sin app | sin app | sin app |
| Querétaro | encontrada: Legislapp QRO MX (com.mobtk.legislapp / 6443885764) | encontrada: Poder Judicial Qro. (mx.gob.tribunalqro.expediente / 1515996756) | sin app | sin app | sin app | sin app |
| Quintana Roo | sin app | sin app | sin app | sin app | sin app | sin app |
| San Luis Potosí | sin app | sin app | sin app | sin app | sin app | sin app |
| Sinaloa | encontrada: Congreso Sinaloa (com.jesus.adan91.eventoscongreso / 6751862635) | encontrada: PJESinaloa (ya en apps.json) | encontrada: IEES Elecciones Juveniles (mx.ieesinaloa.eleccionesjuvenilesapp2 / 1607696851) | sin app | sin app | sin app |
| Sonora | sin app | sin app | encontrada: IEESonora (— / 6736837552) | sin app | sin app | sin app |
| Tabasco | encontrada: OSFE Tabasco (com.osfetabascogobmx.tesken / 1571322410); Auditesken (art.osfe.auditesken / 1591449791) | sin app | sin app | sin app | sin app | sin app |
| Tamaulipas | sin app | encontrada: Soy PJ Tamaulipas (ya en apps.json) | sin app | sin app | sin app | sin app |
| Tlaxcala | sin app | sin app | sin app | sin app | sin app | sin app |
| Veracruz | encontrada: App Georreferenciación Obras (ORFIS) (com.orfis.appSimver / —); Revisión Física de Obra ORFIS (com.orfis.datop / —) | encontrada: Veracruzana Protegida PJEV (— / 6749559583) | sin app | sin app | sin app | sin app |
| Yucatán | sin app | encontrada: PJYucatan (ya en apps.json) | sin app | sin app | sin app | sin app |
| Zacatecas | sin app | sin app | sin app | encontrada: Derechos Humanos Zacatecas (— / 1616955352) | sin app | sin app |

Otros hallazgos estatales fuera de las 6 columnas: tribunales de justicia administrativa (autónomos) de Querétaro (TJAQRO, SITJA Móvil) y Zacatecas (SIT-ZAC).

## Términos por celda (Play; y iOS en celdas iOS✓)

| Entidad | Congreso / ASE | Poder Judicial | OPLE | CEDH | Transparencia | Tribunal electoral |
|---|---|---|---|---|---|---|
| Aguascalientes | Congreso del Estado de Aguascalientes; Congreso Aguascalientes; OSFAGS; Auditoría Superior Aguascalientes | Poder Judicial Aguascalientes; Tribunal Superior de Justicia Aguascalientes | IEE Aguascalientes; Instituto Electoral Aguascalientes | CDHEA; Derechos Humanos Aguascalientes | ITEA; Transparencia Aguascalientes | TEEA; Tribunal Electoral Aguascalientes |
| Baja California | Congreso del Estado de Baja California; Congreso Baja California; ASEBC; Auditoría Superior Baja California | Poder Judicial Baja California; Tribunal Superior de Justicia Baja California | IEEBC; Instituto Electoral Baja California | CEDHBC; Derechos Humanos Baja California | ITAIPBC; Transparencia Baja California | TJEBC; Tribunal Electoral Baja California |
| Baja California Sur | Congreso del Estado de Baja California Sur; Congreso BCS; OSFE BCS; Auditoría Superior BCS | Poder Judicial Baja California Sur; Tribunal Superior de Justicia BCS | IEEBCS; Instituto Electoral BCS | CEDHBCS; Derechos Humanos BCS | ITAIBCS; Transparencia BCS | TEEBCS; Tribunal Electoral BCS |
| Campeche | Congreso del Estado de Campeche; Congreso Campeche; ASECAM; Auditoría Superior Campeche | Poder Judicial Campeche; Tribunal Superior de Justicia Campeche | IEEC Campeche; Instituto Electoral Campeche | CODHECAM; Derechos Humanos Campeche | COTAIPEC; Transparencia Campeche | TEEC Campeche; Tribunal Electoral Campeche |
| Chiapas | Congreso del Estado de Chiapas; Congreso Chiapas; ASE Chiapas; Auditoría Superior Chiapas | Poder Judicial Chiapas; Tribunal Superior de Justicia Chiapas | IEPC Chiapas; Instituto Electoral Chiapas | CEDH Chiapas; Derechos Humanos Chiapas | ITAIPCH; Transparencia Chiapas | TEECH; Tribunal Electoral Chiapas |
| Chihuahua | Congreso del Estado de Chihuahua; Congreso Chihuahua; ASE Chihuahua; Auditoría Superior Chihuahua | Poder Judicial Chihuahua; Tribunal Superior de Justicia Chihuahua | IEE Chihuahua; Instituto Electoral Chihuahua | CEDH Chihuahua; Derechos Humanos Chihuahua | ICHITAIP; Transparencia Chihuahua | TEE Chihuahua; Tribunal Electoral Chihuahua |
| Ciudad de México | Congreso del Estado de Ciudad de México; Congreso CDMX; ASCM; Auditoría Superior CDMX | Poder Judicial Ciudad de México; Tribunal Superior de Justicia CDMX | IECM; Instituto Electoral CDMX | CDHCM; Derechos Humanos CDMX | INFO CDMX; Transparencia CDMX | TECDMX; Tribunal Electoral CDMX |
| Coahuila | Congreso del Estado de Coahuila; Congreso Coahuila; ASE Coahuila; Auditoría Superior Coahuila | Poder Judicial Coahuila; Tribunal Superior de Justicia Coahuila | IEC Coahuila; Instituto Electoral Coahuila | CDHEC Coahuila; Derechos Humanos Coahuila | ICAI Coahuila; Transparencia Coahuila | TECZ; Tribunal Electoral Coahuila |
| Colima | Congreso del Estado de Colima; Congreso Colima; OSAFIG; Auditoría Superior Colima | Poder Judicial Colima; Tribunal Superior de Justicia Colima | IEE Colima; Instituto Electoral Colima | CDHEC Colima; Derechos Humanos Colima | INFOCOL; Transparencia Colima | TEE Colima; Tribunal Electoral Colima |
| Durango | Congreso del Estado de Durango; Congreso Durango; EASE Durango; Auditoría Superior Durango | Poder Judicial Durango; Tribunal Superior de Justicia Durango | IEPC Durango; Instituto Electoral Durango | CEDH Durango; Derechos Humanos Durango | IDAIP; Transparencia Durango | TEED; Tribunal Electoral Durango |
| Estado de México | Congreso del Estado de Estado de México; Congreso Edomex; OSFEM; Auditoría Superior Edomex | Poder Judicial Estado de México; Tribunal Superior de Justicia Edomex | IEEM; Instituto Electoral Edomex | CODHEM; Derechos Humanos Edomex | INFOEM; Transparencia Edomex | TEEM Edomex; Tribunal Electoral Edomex |
| Guanajuato | Congreso del Estado de Guanajuato; Congreso Guanajuato; ASEG; Auditoría Superior Guanajuato | Poder Judicial Guanajuato; Tribunal Superior de Justicia Guanajuato | IEEG; Instituto Electoral Guanajuato | PRODHEG; Derechos Humanos Guanajuato | IACIP; Transparencia Guanajuato | TEEG; Tribunal Electoral Guanajuato |
| Guerrero | Congreso del Estado de Guerrero; Congreso Guerrero; ASE Guerrero; Auditoría Superior Guerrero | Poder Judicial Guerrero; Tribunal Superior de Justicia Guerrero | IEPC Guerrero; Instituto Electoral Guerrero | CDHEG Guerrero; Derechos Humanos Guerrero | ITAIGro; Transparencia Guerrero | TEE Guerrero; Tribunal Electoral Guerrero |
| Hidalgo | Congreso del Estado de Hidalgo; Congreso Hidalgo; ASEH; Auditoría Superior Hidalgo | Poder Judicial Hidalgo; Tribunal Superior de Justicia Hidalgo | IEEH; Instituto Electoral Hidalgo | CDHEH; Derechos Humanos Hidalgo | ITAIH; Transparencia Hidalgo | TEEH; Tribunal Electoral Hidalgo |
| Jalisco | Congreso del Estado de Jalisco; Congreso Jalisco; ASEJ; Auditoría Superior Jalisco | Poder Judicial Jalisco; Tribunal Superior de Justicia Jalisco | IEPC Jalisco; Instituto Electoral Jalisco | CEDHJ; Derechos Humanos Jalisco | ITEI; Transparencia Jalisco | TEJ Jalisco; Tribunal Electoral Jalisco |
| Michoacán | Congreso del Estado de Michoacán; Congreso Michoacán; ASM Michoacán; Auditoría Superior Michoacán | Poder Judicial Michoacán; Tribunal Superior de Justicia Michoacán | IEM Michoacán; Instituto Electoral Michoacán | CEDH Michoacán; Derechos Humanos Michoacán | IMAIP; Transparencia Michoacán | TEEM Michoacán; Tribunal Electoral Michoacán |
| Morelos | Congreso del Estado de Morelos; Congreso Morelos; ESAF Morelos; Auditoría Superior Morelos | Poder Judicial Morelos; Tribunal Superior de Justicia Morelos | IMPEPAC; Instituto Electoral Morelos | CDHMorelos; Derechos Humanos Morelos | IMIPE; Transparencia Morelos | TEEM Morelos; Tribunal Electoral Morelos |
| Nayarit | Congreso del Estado de Nayarit; Congreso Nayarit; ASEN; Auditoría Superior Nayarit | Poder Judicial Nayarit; Tribunal Superior de Justicia Nayarit | IEE Nayarit; Instituto Electoral Nayarit | CDDH Nayarit; Derechos Humanos Nayarit | ITAI Nayarit; Transparencia Nayarit | TEE Nayarit; Tribunal Electoral Nayarit |
| Nuevo León | Congreso del Estado de Nuevo León; Congreso Nuevo León; ASENL; Auditoría Superior Nuevo León | Poder Judicial Nuevo León; Tribunal Superior de Justicia Nuevo León | IEEPCNL; Instituto Electoral Nuevo León | CEDHNL; Derechos Humanos Nuevo León | COTAI NL; Transparencia Nuevo León | TEE Nuevo León; Tribunal Electoral Nuevo León |
| Oaxaca | Congreso del Estado de Oaxaca; Congreso Oaxaca; OSFE Oaxaca; Auditoría Superior Oaxaca | Poder Judicial Oaxaca; Tribunal Superior de Justicia Oaxaca | IEEPCO; Instituto Electoral Oaxaca | DDHPO; Derechos Humanos Oaxaca | OGAIPO; Transparencia Oaxaca | TEEO; Tribunal Electoral Oaxaca |
| Puebla | Congreso del Estado de Puebla; Congreso Puebla; ASE Puebla; Auditoría Superior Puebla | Poder Judicial Puebla; Tribunal Superior de Justicia Puebla | IEE Puebla; Instituto Electoral Puebla | CDH Puebla; Derechos Humanos Puebla | ITAIPUE; Transparencia Puebla | TEEP; Tribunal Electoral Puebla |
| Querétaro | Congreso del Estado de Querétaro; Congreso Querétaro; ESFE Querétaro; Auditoría Superior Querétaro | Poder Judicial Querétaro; Tribunal Superior de Justicia Querétaro | IEEQ; Instituto Electoral Querétaro | DDHQ; Derechos Humanos Querétaro | INFOQRO; Transparencia Querétaro | TEEQ; Tribunal Electoral Querétaro |
| Quintana Roo | Congreso del Estado de Quintana Roo; Congreso Quintana Roo; ASEQROO; Auditoría Superior Quintana Roo | Poder Judicial Quintana Roo; Tribunal Superior de Justicia Quintana Roo | IEQROO; Instituto Electoral Quintana Roo | CDHEQROO; Derechos Humanos Quintana Roo | IDAIPQROO; Transparencia Quintana Roo | TEQROO; Tribunal Electoral Quintana Roo |
| San Luis Potosí | Congreso del Estado de San Luis Potosí; Congreso San Luis Potosí; ASE SLP; Auditoría Superior San Luis Potosí | Poder Judicial San Luis Potosí; Tribunal Superior de Justicia San Luis Potosí | CEEPAC; Instituto Electoral San Luis Potosí | CEDH SLP; Derechos Humanos San Luis Potosí | CEGAIP; Transparencia San Luis Potosí | TEESLP; Tribunal Electoral San Luis Potosí |
| Sinaloa | Congreso del Estado de Sinaloa; Congreso Sinaloa; ASE Sinaloa; Auditoría Superior Sinaloa | Poder Judicial Sinaloa; Tribunal Superior de Justicia Sinaloa | IEES Sinaloa; Instituto Electoral Sinaloa | CEDH Sinaloa; Derechos Humanos Sinaloa | CEAIP Sinaloa; Transparencia Sinaloa | TEESIN; Tribunal Electoral Sinaloa |
| Sonora | Congreso del Estado de Sonora; Congreso Sonora; ISAF Sonora; Auditoría Superior Sonora | Poder Judicial Sonora; Tribunal Superior de Justicia Sonora | IEE Sonora; Instituto Electoral Sonora | CEDH Sonora; Derechos Humanos Sonora | ISTAI; Transparencia Sonora | TEE Sonora; Tribunal Electoral Sonora |
| Tabasco | Congreso del Estado de Tabasco; Congreso Tabasco; OSFE Tabasco; Auditoría Superior Tabasco | Poder Judicial Tabasco; Tribunal Superior de Justicia Tabasco | IEPCT; Instituto Electoral Tabasco | CEDH Tabasco; Derechos Humanos Tabasco | ITAIP Tabasco; Transparencia Tabasco | TET Tabasco; Tribunal Electoral Tabasco |
| Tamaulipas | Congreso del Estado de Tamaulipas; Congreso Tamaulipas; ASE Tamaulipas; Auditoría Superior Tamaulipas | Poder Judicial Tamaulipas; Tribunal Superior de Justicia Tamaulipas | IETAM; Instituto Electoral Tamaulipas | CODHET; Derechos Humanos Tamaulipas | ITAIT; Transparencia Tamaulipas | TRIELTAM; Tribunal Electoral Tamaulipas |
| Tlaxcala | Congreso del Estado de Tlaxcala; Congreso Tlaxcala; OFS Tlaxcala; Auditoría Superior Tlaxcala | Poder Judicial Tlaxcala; Tribunal Superior de Justicia Tlaxcala | ITE Tlaxcala; Instituto Electoral Tlaxcala | CEDHT; Derechos Humanos Tlaxcala | IAIP Tlaxcala; Transparencia Tlaxcala | TET Tlaxcala; Tribunal Electoral Tlaxcala |
| Veracruz | Congreso del Estado de Veracruz; Congreso Veracruz; ORFIS; Auditoría Superior Veracruz | Poder Judicial Veracruz; Tribunal Superior de Justicia Veracruz | OPLE Veracruz; Instituto Electoral Veracruz | CEDHV; Derechos Humanos Veracruz | IVAI; Transparencia Veracruz | TEV Veracruz; Tribunal Electoral Veracruz |
| Yucatán | Congreso del Estado de Yucatán; Congreso Yucatán; ASEY; Auditoría Superior Yucatán | Poder Judicial Yucatán; Tribunal Superior de Justicia Yucatán | IEPAC; Instituto Electoral Yucatán | CODHEY; Derechos Humanos Yucatán | INAIP Yucatán; Transparencia Yucatán | TEEY; Tribunal Electoral Yucatán |
| Zacatecas | Congreso del Estado de Zacatecas; Congreso Zacatecas; ASE Zacatecas; Auditoría Superior Zacatecas | Poder Judicial Zacatecas; Tribunal Superior de Justicia Zacatecas | IEEZ; Instituto Electoral Zacatecas | CDHEZ; Derechos Humanos Zacatecas | IZAI; Transparencia Zacatecas | TRIJEZ; Tribunal Electoral Zacatecas |

Búsquedas iOS amplias por entidad: el nombre de cada estado (y `CDMX`, `Edomex`). Búsquedas Play genéricas extra: Congreso del Estado; H. Congreso del Estado; Legislatura del Estado; LXVI/LXV Legislatura; diputados locales; Poder Judicial del Estado; Tribunal Superior de Justicia del Estado; Consejo de la Judicatura del Estado; expediente judicial electrónico; boletín judicial; tribunal virtual; Instituto Electoral del Estado; Instituto Estatal Electoral; Organismo Público Local Electoral; PREP; Tribunal Electoral del Estado; Comisión Estatal de Derechos Humanos; Comisión de Derechos Humanos del Estado; Instituto de Transparencia; acceso a la información pública; Auditoría Superior del Estado; Órgano de Fiscalización Superior; Tribunal de Justicia Administrativa; Tribunal de Conciliación y Arbitraje; Defensoría Pública; Fiscalía General del Estado.

## Descartados (no oficiales o fuera de México)

- CDHQ (iOS 6800507244): de Experiencia de Impactos Digitales SA de CV, plataforma privada, no la Defensoría de Querétaro.
- Ciudad Judicial (com.mstudio.ciudadjudicial / 1590388319): app de un particular para gestionar casos en Jalisco.
- Mi Senado (gov.senado.app / 1473999707): Senado de Colombia.
- IUS Electoral (iOS 703268348): Esfera Estudios S de RL de CV (editorial privada).
- Legislación UNAM, Congreso UABC, apps de congresos académicos: no son del poder legislativo.
- No mas extorsiones (Consejo Ciudadano CDMX): organismo ciudadano, no poder ni autónomo.

## Para el orquestador: IDs que faltan en entradas existentes de apps.json (no se editaron)

- Bibliotecas UNAM: Android `mx.unam.dgb.android.bibliotecasunam` (hoy `android_id` null).
- Mi INE – Mi Voto donde esté: iOS `6784030897` (hoy `ios_id` null).
- PJESinaloa: iOS `6479665223` (hoy `ios_id` null).
- Valida INE-QR: iOS `1515385147` (hoy `ios_id` null, si aplica).
