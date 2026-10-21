"""Consulta Google Play y App Store (MX).

uso:
  tienda.py play-buscar "<término>"      # appId | título | desarrollador | instalaciones
  tienda.py play "<appId>"               # ficha completa resumida (JSON)
  tienda.py ios-buscar "<término>"       # trackId | nombre | vendedor
  tienda.py ios "<trackId>"              # ficha resumida (JSON)
"""
import json
import sys
import urllib.parse
import urllib.request

from google_play_scraper import app, search

PLAY_CAMPOS = ["title", "developer", "developerEmail", "developerWebsite", "installs", "realInstalls",
               "score", "ratings", "reviews", "updated", "version", "released", "genre", "contentRating",
               "containsAds", "free", "url"]
IOS_CAMPOS = ["trackId", "trackName", "sellerName", "artistName", "version", "currentVersionReleaseDate",
              "releaseDate", "averageUserRating", "userRatingCount", "primaryGenreName", "minimumOsVersion",
              "fileSizeBytes", "trackViewUrl"]


def itunes(ruta, **q):
    url = f"https://itunes.apple.com/{ruta}?" + urllib.parse.urlencode({"country": "mx", **q})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["results"]


def main(cmd, arg):
    if cmd == "play-buscar":
        for x in search(arg, lang="es", country="mx", n_hits=30):
            if x["appId"]:
                print(x["appId"], "|", x["title"], "|", x["developer"], "|", x.get("installs"))
    elif cmd == "play":
        d = app(arg, lang="es", country="mx")
        print(json.dumps({k: d.get(k) for k in PLAY_CAMPOS}, ensure_ascii=False, default=str))
    elif cmd == "ios-buscar":
        for a in itunes("search", term=arg, entity="software", limit=50):
            print(a["trackId"], "|", a["trackName"], "|", a["sellerName"])
    elif cmd == "ios":
        r = itunes("lookup", id=arg)
        print(json.dumps({k: r[0].get(k) for k in IOS_CAMPOS} if r else None, ensure_ascii=False))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(*sys.argv[1:3])
