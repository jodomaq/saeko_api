"""
Descarga todos los programas (carreras) con su nombre y clave interna.
Exporta a CSV y muestra en terminal.
"""

import csv
import requests
from auth import SERVICE_ACCOUNT, USER_EMAIL, get_access_token

BASE_URL = "https://app.saeko.io/api/v1"
OUTPUT_FILE = "programs.csv"


def api_get(endpoint: str, token: str, params: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    print("Autenticando...")
    token = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)["access_token"]
    print("OK\n")

    print("Descargando programas...")
    data = api_get("/core/programs", token, {"include_fields": "internal_code", "limit": 500})
    programs = data.get("programs", [])
    programs.sort(key=lambda p: (p.get("internal_code") or "", p.get("name", "")))
    print(f"Total: {len(programs)} programas\n")

    col_id = 6
    col_clave = 15
    col_nombre = 60
    sep = "-" * (col_id + col_clave + col_nombre + 8)
    header = f"{'ID':>{col_id}} | {'CLAVE':<{col_clave}} | {'NOMBRE':<{col_nombre}}"

    print(sep)
    print(header)
    print(sep)
    for p in programs:
        clave = p.get("internal_code") or ""
        nombre = p.get("name") or ""
        pid = p.get("id", "")
        print(f"{pid:>{col_id}} | {clave:<{col_clave}} | {nombre:<{col_nombre}}")
    print(sep)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "clave", "nombre"])
        writer.writeheader()
        for p in programs:
            writer.writerow({
                "id": p.get("id", ""),
                "clave": p.get("internal_code") or "",
                "nombre": p.get("name") or "",
            })

    print(f"\nArchivo guardado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
