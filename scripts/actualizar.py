#!/usr/bin/env python3
"""
Descarga el histórico de Primitiva, Bonoloto y EuroDreams y reconstruye index.html.

Uso:
    python3 scripts/actualizar.py                # descarga datos nuevos + reconstruye
    python3 scripts/actualizar.py --sin-descarga # solo reconstruye con datos/*.json

Solo usa la librería estándar de Python (3.8+). Fuente de datos: hojas públicas
de lotoideas.com, que recopilan los resultados oficiales de Loterías y Apuestas del Estado.
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
PLANTILLA = RAIZ / "scripts" / "plantilla.html"
SALIDA = RAIZ / "index.html"

_SHEET = "https://docs.google.com/spreadsheets/d/e/{key}/pub?{q}"
JUEGOS = {
    "primitiva": {
        "max": 49,
        "urls": [
            _SHEET.format(key="2PACX-1vTov1BuA0nkVGTS48arpPFkc9cG7B40Xi3BfY6iqcWTrMwCBg5b50-WwvnvaR6mxvFHbDBtYFKg5IsJ", q="gid=0&single=true&output=csv"),
            _SHEET.format(key="2PACX-1vTov1BuA0nkVGTS48arpPFkc9cG7B40Xi3BfY6iqcWTrMwCBg5b50-WwvnvaR6mxvFHbDBtYFKg5IsJ", q="gid=1&single=true&output=csv"),
        ],
    },
    "bonoloto": {
        "max": 49,
        "urls": [
            _SHEET.format(key="2PACX-1vQALTRaLDFfhXOAQmeONPqmFKm9yOiQ4W97rhWgR41BZ7czFsjK5YktD6fnETKHGB9YUnyQ4XBSbhZx", q="gid=0&single=true&output=csv"),
            _SHEET.format(key="2PACX-1vQALTRaLDFfhXOAQmeONPqmFKm9yOiQ4W97rhWgR41BZ7czFsjK5YktD6fnETKHGB9YUnyQ4XBSbhZx", q="gid=1&single=true&output=csv"),
        ],
    },
    "eurodreams": {
        "max": 40,
        "urls": [
            _SHEET.format(key="2PACX-1vTZzm-CTUj3li4EdfW1ImthPdc0AGIymq8tbuwPiqjW0OL4F1MWO5G6PfPEtNvLJcY8MpJo4apayTip", q="output=csv"),
        ],
    },
}


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sorteos-ganadores/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def normalizar(textos, maximo):
    """Devuelve [[fecha ISO, [6 números], extra1, extra2], ...] ordenado por fecha.
    extra1 = complementario (Primitiva/Bonoloto) o sueño (EuroDreams); extra2 = reintegro."""
    filas, vistos = [], set()
    for texto in textos:
        for r in list(csv.reader(io.StringIO(texto)))[1:]:
            try:
                d, m, y = r[0].strip().split("/")
                nums = sorted(int(x) for x in r[1:7])
                if len(set(nums)) != 6 or not all(1 <= x <= maximo for x in nums):
                    continue
                extra = lambda i: int(r[i]) if len(r) > i and r[i].strip() else None
                fila = [f"{int(y):04d}-{int(m):02d}-{int(d):02d}", nums, extra(7), extra(8)]
            except (ValueError, IndexError):
                continue
            clave = (fila[0], tuple(nums))
            if clave not in vistos:
                vistos.add(clave)
                filas.append(fila)
    filas.sort(key=lambda f: f[0])
    return filas


def actualizar_datos():
    cambios = False
    for juego, cfg in JUEGOS.items():
        ruta = DATOS / f"{juego}.json"
        previos = json.loads(ruta.read_text()) if ruta.exists() else []
        try:
            nuevos = normalizar([descargar(u) for u in cfg["urls"]], cfg["max"])
        except Exception as e:  # red caída, hoja movida...: se conservan los datos actuales
            print(f"⚠️  {juego}: no se pudo descargar ({e}); se mantienen los datos actuales")
            continue
        # Protección: nunca sustituir por un histórico más corto (hoja vacía o rota)
        if len(nuevos) < len(previos):
            print(f"⚠️  {juego}: la descarga trae {len(nuevos)} sorteos y había {len(previos)}; no se sobrescribe")
            continue
        if nuevos != previos:
            ruta.write_text(json.dumps(nuevos, separators=(",", ":")))
            cambios = True
        print(f"✔ {juego}: {len(nuevos)} sorteos, último {nuevos[-1][0]} (+{len(nuevos) - len(previos)})")
    return cambios


def construir():
    html = PLANTILLA.read_text(encoding="utf-8")
    for juego in JUEGOS:
        marcador = f"/*{juego.upper()}*/"
        if marcador not in html:
            sys.exit(f"Falta el marcador {marcador} en la plantilla")
        html = html.replace(marcador, (DATOS / f"{juego}.json").read_text())
    SALIDA.write_text(html, encoding="utf-8")
    print(f"✔ index.html generado ({SALIDA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    if "--sin-descarga" not in sys.argv:
        actualizar_datos()
    construir()
