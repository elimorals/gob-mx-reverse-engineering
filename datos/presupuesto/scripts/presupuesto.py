#!/usr/bin/env python3
"""Regenera datos/presupuesto/{entidades,municipios}.json desde las descargas oficiales.

Uso:  python3 -I datos/presupuesto/scripts/presupuesto.py DIR_DESCARGAS

DIR_DESCARGAS debe contener (URLs en datos/presupuesto/FUENTE.md):
  conjunto_de_datos_efipem_estatal_csv.zip     INEGI EFIPEM anual estatal
  conjunto_de_datos_efipem_municipal_csv.zip   INEGI EFIPEM anual municipal
  conjunto_de_datos_efipem_trimestral_csv.zip  INEGI EFIPEM trimestral (solo para CDMX)
  PEF_2026.csv                                 SHCP, PEF aprobado 2026
  iter_00_cpv2020_csv.zip                      INEGI Censo 2020, ITER nacional
"""
import csv, glob, io, json, os, re, sys, zipfile

ANIO_EFIPEM = 2024        # último año con cifras definitivas (2025 es preliminar y municipal incompleto)
ANIO_PEF = 2026           # último PEF aprobado a oct-2026
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(REPO, 'datos', 'presupuesto')

U_EFIPEM_EST = 'https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_estatal_csv.zip'
U_EFIPEM_MUN = 'https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_municipal_csv.zip'
U_EFIPEM_TRI = 'https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_trimestral_csv.zip'
U_PEF = f'https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos/Bases_de_datos_presupuesto/CSV/PEF_{ANIO_PEF}.csv'

# cve_ent INEGI -> nombre tal como aparece en apps.json
ENTIDADES = {
    '01': 'Aguascalientes', '02': 'Baja California', '03': 'Baja California Sur', '04': 'Campeche',
    '05': 'Coahuila', '06': 'Colima', '07': 'Chiapas', '08': 'Chihuahua', '09': 'Ciudad de México',
    '10': 'Durango', '11': 'Guanajuato', '12': 'Guerrero', '13': 'Hidalgo', '14': 'Jalisco',
    '15': 'Estado de México', '16': 'Michoacán', '17': 'Morelos', '18': 'Nayarit', '19': 'Nuevo León',
    '20': 'Oaxaca', '21': 'Puebla', '22': 'Querétaro', '23': 'Quintana Roo', '24': 'San Luis Potosí',
    '25': 'Sinaloa', '26': 'Sonora', '27': 'Tabasco', '28': 'Tamaulipas', '29': 'Tlaxcala',
    '30': 'Veracruz', '31': 'Yucatán', '32': 'Zacatecas',
}
CVE_POR_NOMBRE = {v: k for k, v in ENTIDADES.items()}


def leer_csv_zip(z, nombre):
    with z.open(nombre) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))


def egresos_anuales(z, prefijo, anio, clave):
    """{clave: {'total':…, 'disp':…}} de 'Total de egresos' y 'Disponibilidad final' del año."""
    out = {}
    for r in leer_csv_zip(z, f'conjunto_de_datos/{prefijo}_{anio}.csv'):
        if r['TEMA'] != 'Egresos' or not r['VALOR'].strip():
            continue
        k = clave(r)
        if r['CATEGORIA'] == 'Tema' and r['DESCRIPCION_CATEGORIA'] == 'Total de egresos':
            out.setdefault(k, {})['total'] = int(r['VALOR'])
        elif r['CATEGORIA'] == 'Capítulo' and r['DESCRIPCION_CATEGORIA'] == 'Disponibilidad final':
            out.setdefault(k, {})['disp'] = int(r['VALOR'])
    return out


def poblacion(d):
    """{(cve_ent, cve_mun): POBTOT}; cve_mun '000' = total estatal."""
    z = zipfile.ZipFile(os.path.join(d, 'iter_00_cpv2020_csv.zip'))
    nombre = next(n for n in z.namelist() if n.endswith('.csv') and 'conjunto_de_datos_iter' in n)
    pob = {}
    with z.open(nombre) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            if r['LOC'] == '0000' and r['ENTIDAD'] != '00':
                pob[(r['ENTIDAD'], r['MUN'])] = int(r['POBTOT'])
    nacional = sum(v for (e, m), v in pob.items() if m == '000')
    assert nacional == 126014024, nacional  # total nacional Censo 2020
    return pob


def inventario_municipal():
    """{(estado, nombre en inventario)} de apps.json y sitios/*.json con nivel/orden municipal."""
    nombres = set()
    regs = json.load(open(os.path.join(REPO, 'apps', 'apps.json'), encoding='utf-8'))
    for f in sorted(glob.glob(os.path.join(REPO, 'sitios', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        regs += d if isinstance(d, list) else []
    for a in regs:
        if isinstance(a, dict) and 'municipal' in (a.get('nivel'), a.get('orden')):
            for campo in ('dependencia', 'municipio'):
                if a.get(campo):
                    nombres.add((a['estado'], a[campo]))
    return nombres


def resolver(estado, alias, catalogo):
    """Municipio oficial INEGI cuyo nombre aparece como palabra completa en el alias (el más largo)."""
    cve_ent = CVE_POR_NOMBRE[estado]
    cands = [(m, nom) for (e, m), nom in catalogo.items()
             if e == cve_ent and re.search(r'(?<!\w)' + re.escape(nom) + r'(?!\w)', alias)]
    if not cands:
        raise SystemExit(f'sin municipio INEGI para {estado!r} / {alias!r}')
    largo = max(len(n) for _, n in cands)
    cands = [c for c in cands if len(c[1]) == largo]
    if len(cands) > 1:
        raise SystemExit(f'ambiguo {estado!r} / {alias!r}: {cands}')
    return cve_ent, cands[0][0], cands[0][1]


def main(d):
    pob = poblacion(d)

    # --- PEF: Ramo 28 y 33 por entidad (34 = no distribuible geográficamente, se omite)
    ramos = {}
    with open(os.path.join(d, f'PEF_{ANIO_PEF}.csv'), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r['ID_RAMO'] in ('28', '33'):
                k = (r['ID_ENTIDAD_FEDERATIVA'].zfill(2), r['ID_RAMO'])
                ramos[k] = ramos.get(k, 0) + float(r[f'MONTO_PEF_{ANIO_PEF}'])

    # --- EFIPEM estatal anual (31 gobiernos; CDMX no está en la serie anual)
    z = zipfile.ZipFile(os.path.join(d, 'conjunto_de_datos_efipem_estatal_csv.zip'))
    est = egresos_anuales(z, 'efipem_estatal_anual_tr_cifra', ANIO_EFIPEM, lambda r: r['CVE_ENT'].strip())
    # CDMX: trimestral, acumulado al 4T, clasificación económica
    zt = zipfile.ZipFile(os.path.join(d, 'conjunto_de_datos_efipem_trimestral_csv.zip'))
    tri = next(n for n in zt.namelist() if n.startswith('conjunto_de_datos/') and n.endswith('.csv'))
    cdmx = next((int(r['VALOR']) for r in leer_csv_zip(zt, tri)
                 if r['CVE_ENT'].strip() == '09' and r['ANIO'] == str(ANIO_EFIPEM) and r['TRIMESTRE'] == '4T'
                 and r['CLASIFICADOR'].startswith('CEG') and r['DESCRIPCION_CLASIFICADOR'] == 'Total de egresos'), None)

    entidades = []
    for cve, nombre in ENTIDADES.items():
        notas = []
        if cve in est:
            eg = {'anio': ANIO_EFIPEM, 'total_mxn': est[cve].get('total'),
                  'disponibilidad_final_mxn': est[cve].get('disp'), 'fuente': U_EFIPEM_EST}
        elif cve == '09' and cdmx is not None:
            eg = {'anio': ANIO_EFIPEM, 'total_mxn': cdmx, 'disponibilidad_final_mxn': None, 'fuente': U_EFIPEM_TRI}
            notas.append('CDMX no está en la EFIPEM anual estatal (31 gobiernos). Se usa la EFIPEM trimestral '
                         f'acumulada al 4T {ANIO_EFIPEM} (cifras preliminares, clasificación económica, sin '
                         'disponibilidad final): no es estrictamente comparable con las otras 31.')
        else:
            eg = None
        if cve == '15':
            notas.append('Edomex: la EFIPEM anual incluye los tres poderes, organismos auxiliares y autónomos.')
        r28, r33 = ramos.get((cve, '28')), ramos.get((cve, '33'))
        entidades.append({
            'estado': nombre, 'cve_ent': cve, 'municipio': None, 'cve_mun': None,
            'poblacion_2020': pob.get((cve, '000')),
            'egresos_inegi': eg,
            'transferencias_pef': {'anio': ANIO_PEF, 'ramo28_mxn': round(r28) if r28 is not None else None,
                                   'ramo33_mxn': round(r33) if r33 is not None else None, 'fuente': U_PEF},
            'notas': ' '.join(notas) or None,
        })

    # --- Municipios del inventario
    zm = zipfile.ZipFile(os.path.join(d, 'conjunto_de_datos_efipem_municipal_csv.zip'))
    catalogo = {(r['CVE_ENT'].strip(), r['CVE_MUN'].strip()): r['NOM_MUN'].strip()
                for r in leer_csv_zip(zm, 'catalogos/tc_municipio.csv')}
    alias = {}
    for estado, nom in sorted(inventario_municipal()):
        alias.setdefault(resolver(estado, nom, catalogo), set()).add(nom)
    pendientes = set(alias)
    egm = {}
    for anio in range(ANIO_EFIPEM, ANIO_EFIPEM - 6, -1):   # año base; si falta, el más reciente anterior
        datos = egresos_anuales(zm, 'efipem_municipal_anual_tr_cifra', anio,
                                lambda r: (r['CVE_ENT'].strip(), r['CVE_MUN'].strip()))
        for k in list(pendientes):
            if (k[0], k[1]) in datos and datos[(k[0], k[1])].get('total') is not None:
                egm[k] = (anio, datos[(k[0], k[1])])
                pendientes.discard(k)
        if not pendientes:
            break

    municipios = []
    for (cve_ent, cve_mun, nom), al in sorted(alias.items()):
        anio_v = egm.get((cve_ent, cve_mun, nom))
        notas = None
        if anio_v and anio_v[0] != ANIO_EFIPEM:
            notas = f'Sin dato EFIPEM {ANIO_EFIPEM}; se usa {anio_v[0]}.'
        municipios.append({
            'estado': ENTIDADES[cve_ent], 'cve_ent': cve_ent, 'municipio': nom, 'cve_mun': cve_ent + cve_mun,
            'poblacion_2020': pob.get((cve_ent, cve_mun)),
            'egresos_inegi': {'anio': anio_v[0], 'total_mxn': anio_v[1]['total'],
                              'disponibilidad_final_mxn': anio_v[1].get('disp'), 'fuente': U_EFIPEM_MUN}
                             if anio_v else None,
            'transferencias_pef': None,
            'alias': sorted(al),
            'notas': notas,
        })

    for nombre, filas in (('entidades.json', entidades), ('municipios.json', municipios)):
        with open(os.path.join(OUT, nombre), 'w', encoding='utf-8') as f:
            json.dump(filas, f, ensure_ascii=False, indent=1)
            f.write('\n')
    print(f'entidades: {len(entidades)} ({sum(1 for e in entidades if e["egresos_inegi"])} con egresos); '
          f'municipios: {len(municipios)} ({sum(1 for m in municipios if m["egresos_inegi"])} con egresos)')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
