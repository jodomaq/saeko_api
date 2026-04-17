"""
Consulta de matrícula del plantel Colola - Especialidad Ecoturismo
Últimos 10 periodos.
"""

import requests
from auth import SERVICE_ACCOUNT, USER_EMAIL, get_access_token

BASE_URL = "https://app.saeko.io/api/v1"


def api_get(endpoint: str, token: str, params: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def get_schools(token: str) -> list:
    data = api_get("/core/schools", token, {"include_fields": "cct"})
    return data.get("schools", [])


def get_terms_by_school(token: str, school_id: int) -> list:
    all_terms = []
    params = {"limit": 200, "offset": 0}
    while True:
        data = api_get(f"/core/schools/{school_id}/terms", token, params)
        terms = data.get("terms", [])
        all_terms.extend(terms)
        if not data.get("meta", {}).get("next_page"):
            break
        params["offset"] += len(terms)
    return all_terms


def get_programs_by_school(token: str, school_id: int) -> list:
    data = api_get(f"/core/schools/{school_id}/programs", token,
                   {"include_fields": "internal_code,school_ids"})
    return data.get("programs", [])


def get_enrollment_count(token: str, term_id: int, program_id: int) -> int:
    """Cuenta todos los enrollments de un programa en un term (suma todos los grupos)."""
    params = {"limit": 1, "offset": 0, "filters": f"program_id={program_id}"}
    data = api_get(f"/core/terms/{term_id}/enrollments", token, params)
    return data.get("meta", {}).get("total", len(data.get("enrollments", [])))


def main():
    print("Autenticando...")
    token_data = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)
    token = token_data["access_token"]
    print("OK\n")

    # 1. Buscar plantel Colola
    print("Buscando plantel Colola...")
    schools = get_schools(token)
    colola = next(
        (s for s in schools if "colola" in s.get("name", "").lower()),
        None
    )
    if not colola:
        print("ERROR: No se encontró ningún plantel con 'Colola' en el nombre.")
        print("Planteles disponibles:")
        for s in schools:
            print(f"  {s['id']} | {s.get('name', '')}")
        return

    school_id = colola["id"]
    print(f"Plantel encontrado: [{school_id}] {colola.get('name', '')} (CCT: {colola.get('cct', '')})\n")

    # 2. Buscar especialidad Ecoturismo
    print("Buscando especialidad Ecoturismo...")
    programs = get_programs_by_school(token, school_id)
    ecoturismo = next(
        (p for p in programs if "ecoturismo" in p.get("name", "").lower()),
        None
    )
    if not ecoturismo:
        print("ERROR: No se encontró la especialidad Ecoturismo en ese plantel.")
        print("Especialidades disponibles:")
        for p in programs:
            print(f"  {p['id']} | {p.get('internal_code', '')} | {p.get('name', '')}")
        return

    program_id = ecoturismo["id"]
    print(f"Especialidad encontrada: [{program_id}] {ecoturismo.get('name', '')} "
          f"(Clave: {ecoturismo.get('internal_code', '')})\n")


    # 3. Obtener últimos 10 periodos
    print("Cargando periodos...")
    all_terms = get_terms_by_school(token, school_id)
    sorted_terms = sorted(all_terms, key=lambda t: t.get("begins_at", ""), reverse=True)
    last_10 = sorted_terms[:10]
    print(f"Total de periodos en el plantel: {len(all_terms)}\n")

    # 4. Consultar matrícula por periodo
    print("Consultando matrícula por periodo...\n")

    col_periodo = 35
    col_inicio = 12
    col_fin = 12
    col_matricula = 10

    sep = "-" * (col_periodo + col_inicio + col_fin + col_matricula + 13)
    header = (f"{'PERIODO':<{col_periodo}} | {'INICIO':<{col_inicio}} | "
              f"{'FIN':<{col_fin}} | {'MATRICULA':>{col_matricula}}")

    print(sep)
    print(header)
    print(sep)

    total_general = 0
    for term in last_10:
        term_id = term["id"]
        name = term.get("name", f"Term {term_id}")
        begins = term.get("begins_at", "")[:10]
        ends = term.get("ends_at", "")[:10]
        current_marker = " [ACTUAL]" if term.get("is_current") else ""

        count = get_enrollment_count(token, term_id, program_id)
        total_general += count

        row = (f"{name + current_marker:<{col_periodo}} | {begins:<{col_inicio}} | "
               f"{ends:<{col_fin}} | {count:>{col_matricula}}")
        print(row)

    print(sep)
    total_row = (f"{'TOTAL':<{col_periodo}} | {'':<{col_inicio}} | "
                 f"{'':<{col_fin}} | {total_general:>{col_matricula}}")
    print(total_row)
    print(sep)
    print("\n[ACTUAL] = Periodo activo actualmente")


if __name__ == "__main__":
    main()
