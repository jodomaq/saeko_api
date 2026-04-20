"""
Reprocesa el archivo de errores con CURPs corregidas manualmente.

Flujo por cada fila del CSV de errores:
  1. Si la fila comienza con "mal" → permanece como error pendiente.
  2. Si la fila comienza con "bien":
     a. Busca al alumno en la API por matrícula (enrollment de 6° grado).
     b. Hace PUT /core/students/:id para actualizar la CURP en Saeko.
     c. Procesa el enrollment y lo agrega al CSV de carga.
  3. Sobrescribe el CSV de errores con solo las filas "mal".

Uso:
    python reprocesar_errores.py
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import requests
from tqdm import tqdm
from validate_email import validate_email

from auth import SERVICE_ACCOUNT, USER_EMAIL, get_access_token
from genera_alumnos_sexto import (
    API_LIMIT,
    CARRERAS_CRUCE_CSV,
    CLAVE_PLANTEL,
    COLEGIO,
    DESTINO_FIELDNAMES,
    GRADE_LEVEL,
    RESULTADO_DIR,
    TERM_KEYWORDS,
    VERSION_CARRERA,
    _get,
    _headers,
    buscar_carrera,
    cargar_cruce_carreras,
    corregir_acentos,
    find_febrero_term,
    get_enrollments_grade6,
    get_schools,
    normalizar,
    obtener_genero,
    validar_curp,
    validar_matricula,
    write_csv_rows,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── archivos de entrada / salida ──────────────────────────────────────────────
ERRORES_CSV = RESULTADO_DIR / "errores 2026-04-17 20-44-36.csv"
CARGA_CSV   = RESULTADO_DIR / "carga 2026-04-17 20-44-36.csv"

# Campos del CSV editado: status,plantel,nombre,paterno,materno,matricula,curp_corregida,error
EDITED_FIELDS = ["status", "plantel", "nombre", "paterno", "materno",
                 "matricula", "curp", "error"]

# Campos originales sin la columna "status" (para reescribir los "mal")
ERROR_FIELDNAMES = ["plantel", "nombre", "paterno", "materno",
                    "matricula", "curp", "error"]


# ── API: actualizar CURP del estudiante ───────────────────────────────────────

def update_student_curp(student_id: int, curp: str, token: str, api_url: str) -> dict:
    """PUT /core/students/:id  →  actualiza la CURP en Saeko."""
    url = f"{api_url}/api/v1/core/students/{student_id}"
    payload = {"student": {"curp": curp}}
    resp = requests.put(url, headers=_headers(token), json=payload, timeout=30)
    if resp.status_code not in (200, 204):
        raise RuntimeError(
            f"PUT {url} → {resp.status_code}: {resp.text[:300]}"
        )
    return resp.json() if resp.text else {}


# ── helpers ───────────────────────────────────────────────────────────────────

def leer_errores_editados(path: Path) -> list[dict]:
    """Lee el CSV editado (status,plantel,nombre,…)."""
    rows: list[dict] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, fieldnames=EDITED_FIELDS)
        for row in reader:
            rows.append(row)
    return rows


def _norm(nombre: str) -> str:
    return normalizar(nombre).upper().strip()


def buscar_school(plantel: str, schools: list[dict]) -> dict | None:
    norm = _norm(plantel)
    for s in schools:
        if _norm(s.get("name", "")) == norm:
            return s
    for s in schools:
        s_norm = _norm(s.get("name", ""))
        if norm in s_norm or s_norm in norm:
            return s
    return None


def procesar_enrollment_con_curp(
    enr: dict,
    school_cct: str,
    cruce_por_cct: dict,
    cruce_por_plan: dict,
    curp_corregida: str,
) -> dict:
    """Igual que procesar_enrollment pero usa la CURP corregida en vez de la de la API."""
    student = enr.get("student") or {}

    nombre = corregir_acentos(student.get("first_name") or "")
    surnames = student.get("surnames") or []
    paterno = corregir_acentos(
        surnames[0] if len(surnames) > 0 else student.get("surname", "")
    )
    materno = corregir_acentos(surnames[1] if len(surnames) > 1 else "")

    matricula = validar_matricula((student.get("student_id") or "").strip())
    curp = validar_curp(curp_corregida, nombre, paterno, materno)
    genero = obtener_genero(student.get("gender") or "")

    raw_email = (student.get("email") or "").strip()
    email = raw_email if validate_email(raw_email) else f"{matricula}@cecytem.edu.mx"

    carrera = buscar_carrera(
        school_cct, enr.get("program_name") or "", cruce_por_cct, cruce_por_plan,
    )
    cct = school_cct.upper()

    return {
        "COLEGIO": COLEGIO,
        "CCT": cct,
        "NOMBRE_DE_PLANTEL": CLAVE_PLANTEL.get(cct, enr.get("school_name", cct)),
        "TURNO": {"1": "MATUTINO", "2": "VESPERTINO", "3": "NOCTURNO"}.get(str(enr.get("group_shift") or ""), "MATUTINO"),

        "VERSION_CARRERA": VERSION_CARRERA,
        "CLAVE_CARRERA": carrera["clave"],
        "NOMBRE_CARRERA": carrera["nombre"],
        "MATRICULA": matricula,
        "NOMBRE": nombre,
        "PRIMER_APELLIDO": paterno,
        "SEGUNDO_APELLIDO": materno,
        "CURP": curp,
        "GENERO": genero,
        "CORREO_ELECTRONICO": email,
        "GRUPO": enr.get("group_name") or "",
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── leer y clasificar ─────────────────────────────────────────────────────
    log.info("Leyendo errores editados: %s", ERRORES_CSV)
    filas = leer_errores_editados(ERRORES_CSV)
    log.info("Total filas: %d", len(filas))

    bien: list[dict] = []
    mal: list[dict] = []
    for row in filas:
        if row["status"].strip().lower() == "bien":
            bien.append(row)
        else:
            mal.append(row)

    log.info("Marcadas 'bien': %d  |  Marcadas 'mal': %d", len(bien), len(mal))

    if not bien:
        log.info("No hay filas marcadas como 'bien'. Nada que reprocesar.")
        return

    # ── preparar API y carreras ───────────────────────────────────────────────
    log.info("Cargando tabla de cruce de carreras…")
    cruce_por_cct, cruce_por_plan = cargar_cruce_carreras(CARRERAS_CRUCE_CSV)

    log.info("Autenticando con Saeko…")
    token = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)["access_token"]
    api_url = SERVICE_ACCOUNT["api_url"].rstrip("/")

    log.info("Obteniendo lista de planteles…")
    schools = get_schools(token, api_url)

    # ── agrupar "bien" por plantel ────────────────────────────────────────────
    por_plantel: dict[str, list[dict]] = {}
    for row in bien:
        por_plantel.setdefault(row["plantel"].strip(), []).append(row)

    resultados: list[dict] = []
    sin_resolver: list[dict] = []
    curps_actualizadas = 0

    bar = tqdm(por_plantel.items(), desc="Planteles", unit="plantel", colour="cyan")
    for plantel_name, rows in bar:
        bar.set_postfix_str(plantel_name[:45])

        school = buscar_school(plantel_name, schools)
        if school is None:
            tqdm.write(f"[WARN] Plantel no encontrado en API: '{plantel_name}'")
            sin_resolver.extend(rows)
            continue

        school_id = school["id"]
        school_cct = (school.get("cct") or "").strip()

        term = find_febrero_term(school_id, token, api_url)
        if term is None:
            tqdm.write(f"[WARN] Sin término FEB-JUL 2026: {plantel_name}")
            sin_resolver.extend(rows)
            continue

        # Descargar enrollments de grado 6 para este plantel/término
        enrollments = get_enrollments_grade6(
            term["id"], school_id, token, api_url, plantel_name,
        )

        # Indexar por matrícula
        enr_por_mat: dict[str, dict] = {}
        for enr in enrollments:
            st = enr.get("student") or {}
            mat = (st.get("student_id") or "").strip()
            if mat:
                enr_por_mat[mat] = enr

        for row in rows:
            mat = row["matricula"].strip()
            curp_corregida = row["curp"].strip().upper()
            nombre_display = f"{row['paterno'].strip()} {row['nombre'].strip()}"

            enr = enr_por_mat.get(mat)
            if enr is None:
                tqdm.write(f"  [WARN] Matrícula {mat} no encontrada en enrollments")
                sin_resolver.append(row)
                continue

            student = enr.get("student") or {}
            student_id = student.get("id") or enr.get("student_id")

            # ── 1. Actualizar CURP en Saeko vía PUT ──────────────────────────
            if student_id and curp_corregida:
                try:
                    update_student_curp(student_id, curp_corregida, token, api_url)
                    curps_actualizadas += 1
                    tqdm.write(f"  ↑ API actualizada: {nombre_display} → {curp_corregida}")
                except Exception as exc:
                    tqdm.write(f"  [API-ERR] {nombre_display}: {exc}")

            # ── 2. Procesar enrollment con la CURP corregida ─────────────────
            try:
                resultado = procesar_enrollment_con_curp(
                    enr, school_cct, cruce_por_cct, cruce_por_plan, curp_corregida,
                )
                resultados.append(resultado)
                tqdm.write(f"  ✓ {nombre_display}: OK → carga")
            except Exception as exc:
                tqdm.write(f"  [ERROR] {nombre_display}: {exc}")
                sin_resolver.append(row)

    # ── guardar resultados ────────────────────────────────────────────────────
    if resultados:
        write_csv_rows(CARGA_CSV, resultados, DESTINO_FIELDNAMES)
        log.info("Agregados %d registros a: %s", len(resultados), CARGA_CSV)

    # Sobrescribir errores con solo los "mal" + sin resolver
    todos_errores: list[dict] = []
    for row in mal + sin_resolver:
        todos_errores.append({k: row[k] for k in ERROR_FIELDNAMES})

    with open(ERRORES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ERROR_FIELDNAMES, dialect="excel")
        writer.writerows(todos_errores)
    log.info("Errores restantes: %d → %s", len(todos_errores), ERRORES_CSV)

    # ── resumen ───────────────────────────────────────────────────────────────
    print(f"\n{'═' * 55}")
    print(f"  Agregados a carga  : {len(resultados)}")
    print(f"  CURPs actualizadas : {curps_actualizadas} (API Saeko)")
    print(f"  Sin resolver       : {len(sin_resolver)}")
    print(f"  Errores pendientes : {len(mal)}")
    print(f"  Total restantes    : {len(todos_errores)}")
    print(f"{'═' * 55}")


if __name__ == "__main__":
    main()
