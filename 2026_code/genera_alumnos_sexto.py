"""
Genera la plantilla de alumnos de sexto semestre para carga en SISEC.
Periodo : FEBRERO – JULIO 2026  |  Grado: 6
Fuente  : API Saeko (auth JWT-Bearer)
Destino : 2026_code/resultado/carga YYYY-MM-DD HH-MM-SS.csv
"""

from __future__ import annotations

import csv
import json
import logging
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── agregar raíz al path para importar auth.py ────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import re
from datetime import date

import requests  # noqa: E402 (después de modificar sys.path)
from tqdm import tqdm
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+$")

from auth import SERVICE_ACCOUNT, USER_EMAIL, get_access_token
from curp import CURP as CURPSuite, CURPValueError

# ── validador de CURP (sin dependencia externa) ───────────────────────────────
_ESTADOS = (
    "AS", "BC", "BS", "CC", "CL", "CM", "CS", "CH", "DF", "DG",
    "GT", "GR", "HG", "JC", "MC", "MN", "MS", "NT", "NL", "OC",
    "PL", "QT", "QR", "SP", "SL", "SR", "TC", "TS", "TL", "VZ",
    "YN", "ZS", "NE",
)
_CURP_RE = re.compile(
    r"^[A-Z]{4}"
    r"(?P<yy>\d{2})(?P<mm>0[1-9]|1[0-2])(?P<dd>0[1-9]|[12]\d|3[01])"
    r"(?P<sex>[HM])"
    r"(?P<edo>" + "|".join(_ESTADOS) + r")"
    r"[B-DF-HJ-NP-TV-Z]{3}"
    r"[A-Z0-9]\d$"
)
# Nombres compuestos que Saeko a veces registra como primer nombre
_NOMBRES_COMPUESTOS = {"JOSE", "MARIA", "MA", "MA.", "J", "J."}

# Prefijos que el RENAPO ignora al calcular las iniciales de la CURP
_PREFIJOS_APELLIDO = {"DE", "LA", "EL", "DEL", "LOS", "LAS", "DE LA", "DE LOS", "DE LAS", "J"}
_PREFIJOS_NOMBRE   = _NOMBRES_COMPUESTOS | {"DEL", "DE", "LA", "LOS", "LAS",
                                             "DE LA", "DE LOS", "DE LAS",
                                             "MA DE LOS", "MA DE LA", "MA DEL"}

# ── constantes ────────────────────────────────────────────────────────────────
COLEGIO = "Michoacán"
VERSION_CARRERA = "V23"
TERM_KEYWORDS = ("febrero", "2026")   # ambas deben estar en el nombre del término
GRADE_LEVEL = 6
API_LIMIT = 500

RESULTADO_DIR = Path(__file__).parent / "resultado"
CARRERAS_CRUCE_CSV = Path(__file__).parent / "carreras_cruce.csv"
CHECKPOINT_FILE = RESULTADO_DIR / "checkpoint.json"

DESTINO_FIELDNAMES = [
    "COLEGIO", "CCT", "NOMBRE_DE_PLANTEL", "TURNO", "VERSION_CARRERA",
    "CLAVE_CARRERA", "NOMBRE_CARRERA", "MATRICULA", "NOMBRE",
    "PRIMER_APELLIDO", "SEGUNDO_APELLIDO", "CURP", "GENERO",
    "CORREO_ELECTRONICO", "GRUPO",
]
ERROR_FIELDNAMES = ["plantel", "nombre", "paterno", "materno", "matricula", "curp", "error"]
WARNING_FIELDNAMES = ["plantel", "nombre", "paterno", "materno", "matricula", "curp", "warning"]

# ── CCT → nombre oficial de plantel ───────────────────────────────────────────
CLAVE_PLANTEL: dict[str, str] = {
    "16ETC0001G": "Cecyte 01 Penjamillo",
    "16ETC0003E": "Cecyte 02 Peribán de Ramos",
    "16ETC0004D": "Cecyte 03 Tancítaro",
    "16ETC0006B": "Cecyte 04 Puruándiro",
    "16ETC0005C": "Cecyte 05 Guacamayas",
    "16ETC0010O": "Cecyte 06 Churumuco",
    "16ETC0007A": "Cecyte 07 Epitacio Huerta",
    "16ETC0008Z": "Cecyte 08 San Lucas",
    "16ETC0009Z": "Cecyte 09 Apatzingán",
    "16ETC0011N": "Cecyte 10 Panindícuaro",
    "16ETC0012M": "Cecyte 11 Senguio",
    "16ETC0013L": "Cecyte 12 Morelia",
    "16ETC0014K": "Cecyte 13 Purépero",
    "16ETC0015J": "Cecyte 14 Carácuaro de Morelos",
    "16ETC0019F": "Cecyte 15 Álvaro Obregón",
    "16ETC0016I": "Cecyte 16 Huandacareo",
    "16ETC0017H": "Cecyte 17 Ciudad Hidalgo",
    "16ETC0018G": "Cecyte 18 Nahuatzen",
    "16ETC0021U": "Cecyte 19 Tzintzuntzan",
    "16ETC0020V": "Cecyte 20 Uruapan",
    "16ETC0022T": "Cecyte 21 Vicente Riva Palacio",
    "16ETC0023S": "Cecyte 22 Tangancícuaro",
    "16ETC0024R": "Cecyte 23 Tocumbo",
    "16ETC0025Q": "Cecyte 24 Lagunillas",
    "16ETC0028N": "Cecyte 25 Opopeo",
    "16ETC0026P": "Cecyte 26 Colola",
    "16ETC0027O": "Cecyte 27 San Pedro Jacuaro",
    "16ETC0029M": "Cecyte 28 Maravatío",
    "16ETC0031A": "Cecyte 29 Cahulote de Santa Ana",
    "16ETC0030B": "Cecyte 30 Crescencio Morales",
    "16ETC0032Z": "Cecyte 31 Arteaga",
    "16ETC0033Z": "Cecyte 32 Huecorio",
    "16ETC0034Y": "Cecyte 33 Capula",
    "16ETC0035X": "Cecyte 34 Irapeo",
    "16ETC0002F": "Cecyte 35 Tacámbaro",
    "EXT": "Cecyte 36 Ixtlán de los Hervores",
    "16EMS0001Y": "EMSAD 01 Caleta de Campos",
    "16EMS0002X": "EMSAD 02 Manga de Cuimbo",
    "16EMS0003W": "EMSAD 03 Zárate",
    "16EMS0004V": "EMSAD 04 Agostitlán",
    "16EMS0005U": "EMSAD 05 San Antonio Villalongín",
    "16EMS0006T": "CEMSAD 06 Susupuato",
    "16EMS0008R": "EMSAD 08 Las Cruces",
    "16EMS0009Q": "EMSAD 09 San Jerónimo",
    "16EMS0010F": "EMSAD 10 Cuitzián Grande",
    "16EMS0014B": "CEMSAD 11 Tzintzingareo",
    "16EMS0013C": "CEMSAD 12 Cuto de la Esperanza",
    "16EMS0012D": "CEMSAD 13 Teremendo",
    "16EMS0015A": "CEMSAD 15 Poturo",
    "16EMS0016Z": "CEMSAD 16 Villa Victoria",
    "16EMS0017Z": "CEMSAD 17 Tzitzio",
    "16EMS0018Y": "CEMSAD 18 Santiago Acahuato",
    "16EMS0019X": "CEMSAD 19 Janitzio",
    "16EMS0020M": "CEMSAD 20 Serrano",
    "16EMS0021L": "CEMSAD 21 Ixtaro",
    "16EMS0023J": "CEMSAD 23 Cupuán del Río",
    "16EMS0024I": "CEMSAD 24 Zirahúen",
    "16EMS0026G": "CEMSAD 26 Uripitio",
    "16EMS0027F": "EMSAD 27 Ceibas de Trujillo",
    "16EMS0028E": "CEMSAD 28 Paso de Tierra (Melchor Ocampo)",
    "16EMS0030T": "CEMSAD 30 Limón de Papatzindán",
    "16EMS0031S": "CEMSAD 31 Felipe Carrillo Puerto",
    "16EMS0033Q": "CEMSAD 33 San Cristóbal de los Guajes",
    "16EMS0036N": "CEMSAD 34 Aporo",
    "16EMS0034P": "CEMSAD 35 Cañas",
    "16EMS0035O": "CEMSAD No. 36 Huajúmbaro",
    "16EMS0037M": "CEMSAD No. 37 Santiago Undameo",
    "16EMS0039K": "CEMSAD No. 39 Dr. Miguel Silva",
    "16EMS0040Z": "CEMSAD 40 Chucutitán, el Bejuco",
    "16EMS0041Z": "CEMSAD 41 Santa Cruz de Morelos",
    "16EMS0042Y": "CEMSAD 42 Zináparo",
    "16EMS0044W": "CEMSAD 43 Buenavista",
    "16EMS0045V": "CEMSAD 44 Galeana",
    "16EMS0046U": "CEMSAD 45 Paso de Morelos (La Parotita)",
    "16EMS0047T": "CEMSAD 46 Ostula",
    "16EMS0058Z": "EMSAD 47 Faro de Bucerías",
    "16EMS0048S": "EMSAD 48 El Chaparro",
    "16EMS0049R": "EMSAD 49 Copándaro del Cuatro",
    "16EMS0050G": "EMSAD 50 Unión Juárez Agua Gorda",
    "16EMS0051F": "EMSAD 51 El Puerto de Jungapeo",
    "16EMS0052E": "EMSAD 52 Atécuaro",
    "16EMS0053D": "EMSAD 53 Curimeo",
    "16EMS0054C": "EMSAD 54 La Luz",
    "16EMS0055B": "CEMSAD 55 Las Yeguas",
    "16EMS0056A": "EMSAD 56 San Lorenzo",
    "16EMS0057Z": "EMSAD 57 Gallitos",
    "16EMS0059Y": "EMSAD 58 Las Pitahayas",
    "16EMS0060N": "EMSAD 59 San Nicolás Obispo",
    "16EMS0061M": "EMSAD 60 Tziritzicuaro",
    "16EMS0062L": "EMSAD 61 Tacámbaro",
    "16EMS0063K": "EMSAD 62 San Rafael Tecario",
    "16EMS0064J": "EMSAD 63 Turundeo",
    "16EMS0065I": "EMSAD 64 Aquiles Serdán",
    "16EMS0066H": "EMSAD 65 Atecucario",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── utilidades de texto ───────────────────────────────────────────────────────

def normalizar(s: str) -> str:
    tabla = str.maketrans("ÁÉÍÓÚáéíóú", "AEIOUaeiou")
    return s.translate(tabla).replace("ñ", "Ñ").strip()


def corregir_acentos(s: str) -> str:
    tabla = str.maketrans("ÀÈÌÒÙàèìòù", "ÁÉÍÓÚáéíóú")
    return s.translate(tabla).strip()


def _inicial_real(texto: str, prefijos: set[str]) -> str:
    """Devuelve la primera letra significativa ignorando prefijos (DE, LA, DEL …).

    Soporta prefijos multi-palabra como "MA. DE LOS": intenta consumir la
    secuencia más larga de palabras que formen un prefijo conocido antes de
    tomar la primera letra del resto.
    """
    # Separar prefijos pegados con punto: "J.Lucas" → "J." + "Lucas"
    texto_prep = re.sub(r'\.(?=[A-Za-zÁÉÍÓÚáéíóúÑñ])', '. ', texto)
    palabras = normalizar(texto_prep).upper().split()
    i = 0
    while i < len(palabras):
        # intentar prefijo de 3, 2 y 1 palabra(s)
        matched = False
        for n in (3, 2, 1):
            if i + n <= len(palabras):
                candidato = " ".join(p.rstrip(".") for p in palabras[i:i + n])
                if candidato in prefijos:
                    i += n
                    matched = True
                    break
        if not matched:
            return palabras[i][0]
    return palabras[0][0] if palabras else ""


# ── validaciones ──────────────────────────────────────────────────────────────

_GENERO_MAP: dict[str, str] = {
    "h": "H", "masculino": "H", "male": "H", "hombre": "H", "1": "H",
    "m": "M", "femenino": "M", "female": "M", "mujer": "M", "2": "M",
}


def obtener_genero(gen) -> str:
    result = _GENERO_MAP.get(str(gen).lower().strip())
    if result is None:
        raise ValueError(f"Género no reconocido: '{gen}' (tipo: {type(gen).__name__})")
    return result


def validar_curp(curp: str, nombre: str, paterno: str, materno: str) -> str:
    curp = curp.strip().upper()
    if len(curp) != 18:
        raise ValueError(f"CURP debe tener 18 caracteres, tiene {len(curp)} | curp='{curp}'")
    m = _CURP_RE.match(curp)
    if not m:
        raise ValueError(f"Formato de CURP inválido | curp='{curp}'")
    # Validar que la fecha sea real
    try:
        yy, mm, dd = int(m["yy"]), int(m["mm"]), int(m["dd"])
        yyyy = 1900 + yy if yy >= 25 else 2000 + yy
        date(yyyy, mm, dd)
    except ValueError:
        raise ValueError(f"Fecha inválida en CURP: {curp[4:10]} | curp='{curp}'")
    # Validar inicial del primer apellido (ignorando prefijos: De la, Del …)
    ini_pat = _inicial_real(paterno, _PREFIJOS_APELLIDO)
    if ini_pat and curp[0] != ini_pat:
        raise ValueError(f"Inicial CURP ({curp[0]}) no coincide con apellido paterno ({ini_pat}) | curp='{curp}'")
    # Para nacidos en el extranjero (NE) puede haber un solo apellido — omitir validación de materno
    nacido_extranjero = m["edo"] == "NE"
    ini_mat = _inicial_real(materno, _PREFIJOS_APELLIDO)
    if ini_mat and not nacido_extranjero and curp[2] != "X" and curp[2] != ini_mat:
        raise ValueError(f"Inicial CURP ({curp[2]}) no coincide con apellido materno ({ini_mat}) | curp='{curp}'")
    # Validar inicial del primer nombre (ignorando Ma., José, etc.)
    ini_nom = _inicial_real(nombre, _PREFIJOS_NOMBRE)
    if ini_nom and curp[3] != ini_nom:
        raise ValueError(f"Inicial CURP ({curp[3]}) no coincide con nombre ({ini_nom}) | curp='{curp}'")
    return curp


def validar_curp_estructura(curp: str) -> tuple[bool, str]:
    """Valida estructura de CURP con CURPSuite (formato, fecha, dígito verificador, estado)."""
    try:
        CURPSuite(curp.strip().upper())
        return True, ""
    except CURPValueError as exc:
        return False, str(exc)


def validar_matricula(mat: str) -> str:
    if len(mat) != 14:
        raise ValueError(f"Matrícula debe tener 14 chars, tiene {len(mat)}: '{mat}'")
    return mat


# ── tabla de cruce de carreras ────────────────────────────────────────────────

def cargar_cruce_carreras(
    path: Path,
) -> tuple[dict[tuple[str, str], dict], dict[str, dict]]:
    """
    cruce_por_cct : (CCT_upper, PLAN_upper) → {nombre, clave}   búsqueda primaria
    cruce_por_plan: PLAN_upper             → {nombre, clave}   fallback
    """
    cruce_por_cct: dict[tuple[str, str], dict] = {}
    cruce_por_plan: dict[str, dict] = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            cct = row["CCT"].strip().upper()
            plan = row["PLAN DE ESTUDIOS"].strip().upper()
            info = {
                "nombre": row["SISEC_ESPECIALIDAD"].strip(),
                "clave": row["SISEC_CLAVE"].strip(),
            }
            cruce_por_cct[(cct, plan)] = info
            if plan not in cruce_por_plan:
                cruce_por_plan[plan] = info
    return cruce_por_cct, cruce_por_plan


def buscar_carrera(
    cct: str,
    program_name: str,
    cruce_por_cct: dict,
    cruce_por_plan: dict,
) -> dict:
    plan = program_name.strip().upper()
    info = cruce_por_cct.get((cct.upper(), plan)) or cruce_por_plan.get(plan)
    if info is None:
        raise ValueError(f"Carrera no encontrada: CCT={cct!r}, plan={program_name!r}")
    return info


# ── I/O CSV ───────────────────────────────────────────────────────────────────

def write_csv_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=fieldnames, dialect="excel").writerows(rows)


# ── llamadas a la API ─────────────────────────────────────────────────────────

def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


def _get(url: str, token: str, params: Optional[dict] = None) -> dict:
    resp = requests.get(url, headers=_headers(token), params=params, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"GET {url} → {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def get_schools(token: str, api_url: str) -> list[dict]:
    url = f"{api_url}/api/v1/core/schools"
    data = _get(url, token, {"include_fields": "cct", "limit": API_LIMIT})
    return data.get("schools", [])


def find_febrero_term(school_id: int, token: str, api_url: str) -> Optional[dict]:
    url = f"{api_url}/api/v1/core/schools/{school_id}/terms"
    offset = 0
    while True:
        data = _get(url, token, {"limit": 200, "offset": offset})
        terms = data.get("terms", [])
        for t in terms:
            name = t.get("name", "").lower()
            if all(kw in name for kw in TERM_KEYWORDS):
                return t
        if len(terms) < 200:
            break
        offset += 200
    return None


def get_enrollments_grade6(
    term_id: int, school_id: int, token: str, api_url: str, school_name: str = ""
) -> list[dict]:
    url = f"{api_url}/api/v1/core/terms/{term_id}/enrollments"
    params_base = {
        "include_fields": "student,program_name,group_name,school_name,group_shift",
        "filters": f"grade_level={GRADE_LEVEL};school_id={school_id}",
        "limit": API_LIMIT,
    }
    enrollments: list[dict] = []
    offset = 0
    total_reported = None
    page = 1
    while True:
        data = _get(url, token, {**params_base, "offset": offset})
        batch = data.get("enrollments", [])
        enrollments.extend(batch)

        if total_reported is None:
            total_reported = data.get("meta", {}).get("total")

        if page > 1 or (total_reported and total_reported > API_LIMIT):
            label = school_name[:35] if school_name else f"term {term_id}"
            tqdm.write(
                f"  [PAGINANDO] {label} | pág {page} | offset={offset} | "
                f"esta pág={len(batch)} | total acumulado={len(enrollments)} / {total_reported}"
            )

        if not batch:
            break
        offset += len(batch)
        page += 1
        if total_reported is not None and len(enrollments) >= total_reported:
            break

    return enrollments


def get_student_curp(student_id: int, token: str, api_url: str) -> str:
    """Obtiene la CURP del alumno (no viene en el embedding de enrollment)."""
    url = f"{api_url}/api/v1/core/students/{student_id}"
    data = _get(url, token, {"include_fields": "curp"})
    student = data.get("student") or data
    return (student.get("curp") or "").strip()


# ── transformación enrollment → registro destino ─────────────────────────────

def procesar_enrollment(
    enr: dict,
    school_cct: str,
    cruce_por_cct: dict,
    cruce_por_plan: dict,
    raw_curp: str,
    skip_curp_validation: bool = False,
) -> dict:
    student = enr.get("student") or {}

    nombre = corregir_acentos(student.get("first_name") or "")
    surnames = student.get("surnames") or []
    paterno = corregir_acentos(surnames[0] if len(surnames) > 0 else student.get("surname", ""))
    materno = corregir_acentos(surnames[1] if len(surnames) > 1 else "")

    matricula = validar_matricula((student.get("student_id") or "").strip())
    curp = raw_curp.strip().upper() if skip_curp_validation else validar_curp(raw_curp, nombre, paterno, materno)
    genero = obtener_genero(student.get("gender") or "")

    raw_email = (student.get("email") or "").strip()
    if _EMAIL_RE.match(raw_email) and len(raw_email) <= 64:
        email = raw_email
    elif len(raw_email) > 64:
        email = "michoacan@cecytem.edu.mx"
    else:
        email = f"{matricula}@cecytem.edu.mx"

    carrera = buscar_carrera(school_cct, enr.get("program_name") or "", cruce_por_cct, cruce_por_plan)
    cct = school_cct.upper()

    return {
        "COLEGIO": COLEGIO,
        "CCT": cct,
        "NOMBRE_DE_PLANTEL": CLAVE_PLANTEL.get(cct, enr.get("school_name", cct)),
        "TURNO": enr.get("group_shift") or "",
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


# ── checkpoint ────────────────────────────────────────────────────────────────

def _guardar_checkpoint(timestamp: str, processed_ids: set, carga_path: Path, errores_path: Path) -> None:
    RESULTADO_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "processed_ids": list(processed_ids),
            "carga_path": str(carga_path),
            "errores_path": str(errores_path),
        }, f, ensure_ascii=False, indent=2)


def _cargar_checkpoint() -> Optional[dict]:
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return None


def _eliminar_checkpoint() -> None:
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


# ── CSV → Excel particionado ──────────────────────────────────────────────────

def csv_a_excel_particionado(csv_path: Path, n_partes: int = 10) -> Path:
    """Lee el CSV de carga y lo divide en *n_partes* archivos .xlsx con encabezados."""
    import openpyxl

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, fieldnames=DESTINO_FIELDNAMES)
        rows = list(reader)

    if not rows:
        log.warning("CSV de carga vacío, no se generan archivos Excel.")
        return csv_path.parent

    carpeta = csv_path.parent / csv_path.stem
    carpeta.mkdir(parents=True, exist_ok=True)

    chunk_size = math.ceil(len(rows) / n_partes)

    for i in range(n_partes):
        chunk = rows[i * chunk_size : (i + 1) * chunk_size]
        if not chunk:
            break
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "myFile"
        ws.append(DESTINO_FIELDNAMES)
        for row in chunk:
            ws.append([row[col] for col in DESTINO_FIELDNAMES])
        nombre_archivo = carpeta / f"{csv_path.stem} parte {i + 1}.xlsx"
        wb.save(nombre_archivo)
        log.info("  Excel %d/%d: %s (%d filas)", i + 1, n_partes, nombre_archivo.name, len(chunk))

    log.info("Archivos Excel guardados en: %s", carpeta)
    return carpeta


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    log.info("Cargando tabla de cruce de carreras…")
    cruce_por_cct, cruce_por_plan = cargar_cruce_carreras(CARRERAS_CRUCE_CSV)
    log.info("Cruce cargado: %d entradas (CCT+plan), %d por plan", len(cruce_por_cct), len(cruce_por_plan))

    # ── checkpoint / resume ───────────────────────────────────────────────────
    checkpoint = _cargar_checkpoint()
    if checkpoint:
        print(f"\nAvance guardado encontrado del {checkpoint['timestamp']} "
              f"({len(checkpoint['processed_ids'])} planteles ya procesados).")
        resp = input("¿Continuar donde se quedó? [s/n]: ").strip().lower()
        if resp in ("s", "si", "sí", "y", "yes"):
            timestamp = checkpoint["timestamp"]
            processed_ids: set[int] = set(checkpoint["processed_ids"])
            carga_path = Path(checkpoint["carga_path"])
            errores_path = Path(checkpoint["errores_path"])
            warnings_path = RESULTADO_DIR / f"warnings {timestamp}.csv"
            log.info("Reanudando desde %d planteles ya procesados.", len(processed_ids))
        else:
            _eliminar_checkpoint()
            timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            processed_ids = set()
            carga_path = RESULTADO_DIR / f"carga {timestamp}.csv"
            errores_path = RESULTADO_DIR / f"errores {timestamp}.csv"
            warnings_path = RESULTADO_DIR / f"warnings {timestamp}.csv"
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        processed_ids = set()
        carga_path = RESULTADO_DIR / f"carga {timestamp}.csv"
        errores_path = RESULTADO_DIR / f"errores {timestamp}.csv"
        warnings_path = RESULTADO_DIR / f"warnings {timestamp}.csv"

    log.info("Autenticando con Saeko…")
    token = get_access_token(SERVICE_ACCOUNT, USER_EMAIL)["access_token"]
    api_url = SERVICE_ACCOUNT["api_url"].rstrip("/")

    log.info("Obteniendo lista de planteles…")
    schools = get_schools(token, api_url)
    pending = [s for s in schools if s["id"] not in processed_ids]
    log.info("%d planteles totales, %d pendientes", len(schools), len(pending))
    print()

    total_ok = 0
    total_err = 0
    total_warn = 0

    bar_schools = tqdm(pending, desc="Planteles", unit="plantel", colour="cyan")
    for school in bar_schools:
        school_id = school["id"]
        school_name = school.get("name", str(school_id))
        school_cct = (school.get("cct") or "").strip()

        bar_schools.set_postfix_str(school_name[:45])

        term = find_febrero_term(school_id, token, api_url)
        if term is None:
            tqdm.write(f"[SKIP] Sin término FEB-JUL 2026: {school_name}")
            processed_ids.add(school_id)
            _guardar_checkpoint(timestamp, processed_ids, carga_path, errores_path)
            continue

        enrollments = get_enrollments_grade6(term["id"], school_id, token, api_url, school_name)
        tqdm.write(f"\n── {school_name} | {term['name']} | {len(enrollments)} alumnos 6° ──")

        resultados_plantel: list[dict] = []
        errores_plantel: list[dict] = []
        warnings_plantel: list[dict] = []

        bar_alumnos = tqdm(
            enrollments,
            desc=f"  {school_name[:35]}",
            unit="alumno",
            leave=False,
            colour="green",
        )
        for enr in bar_alumnos:
            student = enr.get("student") or {}
            surnames = student.get("surnames") or []
            nombre = student.get("first_name", "")
            bar_alumnos.set_postfix_str(f"{surnames[0] if surnames else ''} {nombre}"[:30])

            # Obtener CURP (no viene embebida en enrollment)
            raw_curp = (student.get("curp") or "").strip()
            if not raw_curp:
                sid = student.get("id") or enr.get("student_id")
                if sid:
                    try:
                        raw_curp = get_student_curp(sid, token, api_url)
                    except Exception:
                        raw_curp = ""

            # ── Validación dual: CURPSuite (estructura) + validar_curp (nombres) ──
            suite_ok, suite_err = validar_curp_estructura(raw_curp)

            if suite_ok:
                # CURPSuite aprueba estructura → intento normal (con validación de nombres)
                try:
                    resultados_plantel.append(
                        procesar_enrollment(enr, school_cct, cruce_por_cct, cruce_por_plan, raw_curp)
                    )
                except Exception as exc:
                    # Falló validar_curp u otro → reintentar sin validar CURP
                    try:
                        resultados_plantel.append(
                            procesar_enrollment(
                                enr, school_cct, cruce_por_cct, cruce_por_plan, raw_curp,
                                skip_curp_validation=True,
                            )
                        )
                        # Caso 1: CURPSuite ok, validar_curp falló → carga + warning
                        warnings_plantel.append({
                            "plantel": school_name,
                            "nombre": nombre,
                            "paterno": surnames[0] if len(surnames) > 0 else "",
                            "materno": surnames[1] if len(surnames) > 1 else "",
                            "matricula": (student.get("student_id") or "").strip(),
                            "curp": raw_curp,
                            "warning": str(exc),
                        })
                        tqdm.write(f"[WARN] {surnames[0] if surnames else ''} {nombre}: {exc}")
                    except Exception as exc2:
                        # Error no relacionado con CURP (matrícula, género, carrera)
                        errores_plantel.append({
                            "plantel": school_name,
                            "nombre": nombre,
                            "paterno": surnames[0] if len(surnames) > 0 else "",
                            "materno": surnames[1] if len(surnames) > 1 else "",
                            "matricula": (student.get("student_id") or "").strip(),
                            "curp": raw_curp,
                            "error": str(exc2),
                        })
                        tqdm.write(f"[ERROR] {surnames[0] if surnames else ''} {nombre}: {exc2}")
            else:
                # Casos 2 y 3: CURPSuite falla → error
                errores_plantel.append({
                    "plantel": school_name,
                    "nombre": nombre,
                    "paterno": surnames[0] if len(surnames) > 0 else "",
                    "materno": surnames[1] if len(surnames) > 1 else "",
                    "matricula": (student.get("student_id") or "").strip(),
                    "curp": raw_curp,
                    "error": f"[CURPSuite] {suite_err}",
                })
                tqdm.write(f"[ERROR] {surnames[0] if surnames else ''} {nombre}: [CURPSuite] {suite_err}")

        # Guardar resultados del plantel y actualizar checkpoint
        write_csv_rows(carga_path, resultados_plantel, DESTINO_FIELDNAMES)
        write_csv_rows(errores_path, errores_plantel, ERROR_FIELDNAMES)
        write_csv_rows(warnings_path, warnings_plantel, WARNING_FIELDNAMES)
        processed_ids.add(school_id)
        _guardar_checkpoint(timestamp, processed_ids, carga_path, errores_path)

        obtenidos = len(enrollments)
        ok_plantel = len(resultados_plantel)
        err_plantel = len(errores_plantel)
        warn_plantel = len(warnings_plantel)
        total_ok += ok_plantel
        total_err += err_plantel
        total_warn += warn_plantel
        tqdm.write(
            f"  ✓ {school_name}: {obtenidos} obtenidos | "
            f"{ok_plantel} ok, {err_plantel} errores, {warn_plantel} warnings  "
            f"(acumulado: {total_ok} ok / {total_err} errores / {total_warn} warnings)"
        )

    _eliminar_checkpoint()
    print(f"\nFinalizado {timestamp}")
    print(f"  Procesados : {total_ok}")
    print(f"  Warnings   : {total_warn}")
    print(f"  Errores    : {total_err}")
    if total_ok:
        print(f"  Carga CSV  : {carga_path}")
        carpeta_excel = csv_a_excel_particionado(carga_path)
        print(f"  Carga Excel: {carpeta_excel}")
    if total_warn:
        print(f"  Warnings   : {warnings_path}")
    if total_err:
        print(f"  Errores    : {errores_path}")


if __name__ == "__main__":
    main()
