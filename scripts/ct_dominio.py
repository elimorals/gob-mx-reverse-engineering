"""Subdominios de UN dominio desde Certificate Transparency (base pública de crt.sh). Pasivo.

uso: python3 -I ct_dominio.py sat.gob.mx          # imprime hosts, uno por línea
Filtra hosts claramente internos/no-productivos (dev, qa, uat, test, pre, int, local).
"""
import re
import subprocess
import sys

dom = sys.argv[1].lower().lstrip("*.")
sql = ("SELECT DISTINCT lower(name_value) FROM certificate_and_identities "
       f"WHERE plainto_tsquery('certwatch', '{dom}') @@ identities(certificate) "
       "AND name_type IN ('2.5.4.3','dNSName')")
out = subprocess.run(["psql", "-h", "crt.sh", "-p", "5432", "-U", "guest", "-d", "certwatch",
                      "-At", "-c", sql], capture_output=True, text=True, timeout=120)
if out.returncode:
    sys.exit("crt.sh: " + out.stderr.strip()[:200])

interno = re.compile(r"(^|[.-])(dev|qa|uat|test|pre|stage|staging|int|sandbox|local|demo|lab)([.-]|$)")
hosts = {h.strip().lstrip("*.") for h in out.stdout.splitlines()
         if h.strip().lstrip("*.").endswith("." + dom) or h.strip().lstrip("*.") == dom}
for h in sorted(h for h in hosts if not interno.search(h)):
    print(h)
