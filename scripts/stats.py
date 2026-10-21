"""Estadísticas para la comparación. Lee apps/apps.json y sitios/*.json."""
import json
from collections import Counter
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
apps = json.loads((raiz / "apps/apps.json").read_text())

sitios = []
for f in sorted((raiz / "sitios").glob("*.json")):
    try:
        sitios += json.loads(f.read_text())
    except Exception as e:
        print("!! no parsea", f.name, e)


def cuenta(items, campo):
    return Counter((i.get(campo) or "—") for i in items).most_common()


print("=== APPS ===", len(apps))
print("por nivel:", cuenta(apps, "nivel"))
print("por sector:", cuenta(apps, "sector"))
print("por estatus:", cuenta(apps, "estatus"))
print("con android:", sum(bool(a.get("android_id")) for a in apps),
      "| con ios:", sum(bool(a.get("ios_id")) for a in apps),
      "| ambos:", sum(bool(a.get("android_id")) and bool(a.get("ios_id")) for a in apps))
print("requiere_cuenta:", cuenta(apps, "requiere_cuenta"))
# top por instalaciones reales (Android)
coninst = [(a.get("play", {}).get("realInstalls") or 0, a["nombre"], a.get("siglas")) for a in apps if a.get("play")]
print("top10 instalaciones Android:")
for n, nom, sig in sorted(coninst, reverse=True)[:10]:
    print(f"   {n:>12,}  {nom} ({sig})")
# apps estancadas: score bajo
malas = [(a.get("play", {}).get("score"), a["nombre"]) for a in apps
         if a.get("play") and (a["play"].get("score") or 5) < 3 and a["play"].get("ratings")]
print("apps con score Play <3:", sorted(x for x in malas if x[0]))

print("\n=== SITIOS ===", len(sitios))
print("por nivel:", cuenta(sitios, "nivel"))
print("por plataforma:", cuenta(sitios, "plataforma"))
print("por anti_bot:", cuenta(sitios, "anti_bot"))
print("por autenticacion:", cuenta(sitios, "autenticacion"))

# estados sin app propia (nivel estatal): comparar 32 entidades
ENTIDADES = ["Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas", "Chihuahua",
             "Coahuila", "Colima", "Durango", "Ciudad de México", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco",
             "México", "Estado de México", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla",
             "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
             "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"]
apps_est = Counter(a.get("estado") for a in apps if a.get("nivel") == "estatal")
print("\napps estatales por entidad:")
for e in sorted(apps_est, key=lambda x: -apps_est[x]):
    print(f"   {apps_est[e]:>2}  {e}")
