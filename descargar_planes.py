#!/usr/bin/env python3
"""
Descargador de Planes de Estudio - COSAC SEMS
Parsea la página y descarga todos los archivos organizados por carpetas según año/categoría.
"""

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup

BASE_URL = "https://cosac.sems.gob.mx"
PAGE_URL = "https://cosac.sems.gob.mx/pa_formaciontecnica.php"
DESTINO = "planes_de_estudio"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

# Permit toggling SSL verification via environment variable.
# Set VERIFY_SSL=0 (Windows) or VERIFY_SSL=0 (Unix) to disable cert checks.
VERIFY_SSL = os.environ.get("VERIFY_SSL", "1").lower() not in ("0", "false", "no", "n")
if not VERIFY_SSL:
    # Suppress warnings from urllib3 about insecure requests.
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def limpiar_nombre(nombre):
    return re.sub(r'[<>:"/\\|?*]', '_', nombre).strip()

def obtener_pagina():
    print("Descargando página principal...")
    r = requests.get(PAGE_URL, headers=HEADERS, timeout=30, verify=VERIFY_SSL)
    r.raise_for_status()
    return r.text

def extraer_enlaces(html):
    soup = BeautifulSoup(html, "html.parser")
    resultados = []

    todos_los_links = soup.find_all("a", href=True)

    for link in todos_los_links:
        href = link["href"]
        if not (href.endswith(".pdf") or href.endswith(".zip") or 
                ".pdf" in href or ".zip" in href):
            continue
        if not href.startswith("http"):
            href = urljoin(BASE_URL, href)

        nombre_archivo = unquote(href.split("/")[-1])

        partes_ruta = []
        li_actual = link.find_parent("li")
        nivel = 0
        while li_actual and nivel < 10:
            ul_padre = li_actual.find_parent("ul")
            if ul_padre:
                li_padre = ul_padre.find_parent("li")
                if li_padre:
                    textos = []
                    for child in li_padre.children:
                        if hasattr(child, 'get_text'):
                            t = child.get_text(strip=True)
                            if t and "expandir" not in t.lower() and len(t) > 1:
                                textos.append(t)
                    if textos:
                        partes_ruta.insert(0, limpiar_nombre(textos[0]))
                li_actual = li_padre
                nivel += 1
            else:
                break

        if len(partes_ruta) > 4:
            partes_ruta = partes_ruta[-4:]

        ruta_carpeta = os.path.join(DESTINO, *partes_ruta) if partes_ruta else DESTINO
        resultados.append((ruta_carpeta, nombre_archivo, href))

    return resultados

def descargar_archivo(url, ruta_carpeta, nombre_archivo):
    Path(ruta_carpeta).mkdir(parents=True, exist_ok=True)
    destino = os.path.join(ruta_carpeta, nombre_archivo)

    if os.path.exists(destino):
        print(f"  [EXISTE] {destino}")
        return True

    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True, verify=VERIFY_SSL)
        r.raise_for_status()
        with open(destino, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  [OK] {destino}")
        return True
    except Exception as e:
        print(f"  [ERROR] {url} -> {e}")
        return False

def main():
    html = obtener_pagina()
    
    print("Extrayendo enlaces...")
    enlaces = extraer_enlaces(html)
    
    vistos = set()
    enlaces_unicos = []
    for ruta, nombre, url in enlaces:
        if url not in vistos:
            vistos.add(url)
            enlaces_unicos.append((ruta, nombre, url))

    print(f"\nTotal de archivos únicos encontrados: {len(enlaces_unicos)}")
    print(f"Descargando en: {os.path.abspath(DESTINO)}\n")

    ok = 0
    errores = 0
    for i, (ruta, nombre, url) in enumerate(enlaces_unicos, 1):
        print(f"[{i}/{len(enlaces_unicos)}] {nombre}")
        if descargar_archivo(url, ruta, nombre):
            ok += 1
        else:
            errores += 1
        time.sleep(0.3)

    print(f"\n{'='*50}")
    print(f"Completado: {ok} descargados, {errores} errores")
    print(f"Carpeta: {os.path.abspath(DESTINO)}")

if __name__ == "__main__":
    main()
