#FUNCIONES QUE USAN LOS SCRIPTS PARA LA CARGA DE DATOS GENERALES DE ALUMNOS
#pip install CURPSuite
from validate_email import validate_email
import csv
from curp import *

def normalize(s):
    replacements = (
        ("Á", "A"),
        ("É", "E"),
        ("Í", "I"),
        ("Ó", "O"),
        ("Ú", "U"),
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ñ", "Ñ")
    )
    for a, b in replacements:
        s = s.replace(a, b)
    s = s.strip()
    s = (s.encode('utf8', 'ignore')).decode("utf-8")
    return s


def verificarCorreo(correo):
    is_valid = validate_email(correo)
    return is_valid


def corregirAcentos(s):
    replacements = (
        ("À", "Á"),
        ("È", "É"),
        ("Ì", "Í"),
        ("Ò", "Ó"),
        ("Ù", "Ú"),
        ("à", "á"),
        ("è", "é"),
        ("ì", "í"),
        ("ò", "ó"),
        ("ù", "ú")
    )
    for a, b in replacements:
        s = s.replace(a, b)
    s = s.strip()
    s = (s.encode('utf8', 'ignore')).decode("utf-8")
    return s

def cct(plantel, lista, carrera):
    try:
        result = ""
        plantel = str(plantel).replace("  "," ")
        result = lista.get(plantel)
        if result == "EXT":
            if carrera == "333507006-13":
                return "16ETC0026P"
            if carrera == "352100002-16":
                return "16ETC0032Z"
            if carrera == "3061300001-17":
                return "16ETC0017H"
    except KeyError:
        raise ValueError("Clave de plantel no encontrada")
    return result

def clave_carrera(plan, lista, plantel):
    result = ""
    plan = str(plan).replace("  ", " ")
    plan = plan.capitalize()
    plan = plan.strip()
    plan = normalize(plan)
    if plantel == 'Ixtlán de los Hervores':
        return "EMS_TIC"
    if plan == "Asistencia en direccion y control de pymes":
        return "333502006-13"
    if plan == "Componente de formacion basica":
        return "COMP_BASI"
    if plan == "Diseno grafico digital":
        return "3021500001-17"
    if plan == "Contabilidad*":
        return "333400001-16"
    for l in lista:
        nom_carr = str(l["nombre_carrera"]).replace("  "," ")
        nom_carr = nom_carr.capitalize()
        nom_carr = nom_carr.strip()
        nom_carr = normalize(nom_carr)
        if nom_carr == plan:
            result = l["clave_carrera"]
            break
    if result == "":
        raise ValueError("Clave de carrera no encontrada", nom_carr, plan, plantel)
        #result = "ERROR"
    return result


def nombre_carrera(clave, lista, plantel):
    for l in lista:
        if l["clave_carrera"] == clave:
            if plantel == 'Ixtlán de los Hervores':
                return "Tecnologías de la información y la comunicación"
            else:
                return l["nombre_carrera"]


def matricula(matricula):
    if len(matricula) != 14:
        raise ValueError(" error en matricula")
    return matricula

def validar_curp_raise(curp_str, nombre_str, paterno_str, materno_str):
    try:
        paterno_str = normalize(paterno_str).upper()
        materno_str = normalize(materno_str).upper()
        nombre_str = normalize(nombre_str).upper()
        print(paterno_str + " " + materno_str + " " + nombre_str + " " + curp_str)
        c = CURP(curp_str, primer_apellido=paterno_str, segundo_apellido=materno_str, nombre=nombre_str)
    except CURPLengthError as e:
        raise ValueError("CURP = " + str(e))
    except CURPDateError as e:
        raise ValueError("CURP = " + str(e))
    except CURPNameError as e:
        raise ValueError("CURP = " + str(e))
    except CURPFirstSurnameError as e:
        raise ValueError("CURP = " + str(e))
    except CURPSecondSurnameError as e:
        raise ValueError("CURP = " + str(e))
    except CURPFullNameError as e:
        raise ValueError("CURP = " + str(e))
    except CURPSexError as e:
        raise ValueError("CURP = " + str(e))
    except CURPRegionError as e:
        raise ValueError("CURP = " + str(e))
    except CURPValueError as e:
        raise ValueError("CURP = " + str(e))
    return curp_str

def obtener_genero(gen):
    if gen == "Masculino":
        return "H"
    elif gen == "Femenino":
        return "M"
    else:
        raise ValueError("Error en el género")

def grabar_linea(archivo, linea):
    try:
        arch = archivo + '.csv'
        archivoDestino = open(arch, 'a', encoding="utf8", newline='')
        cols = ["plantel","nombre","paterno","materno","matricula","error"]
        writer = csv.DictWriter(archivoDestino, fieldnames=cols, dialect='excel')
        writer.writerow(linea)
        archivoDestino.close()
    except NameError:
        print(NameError)

def grabar_lista_archivo(archivo, lista):
    try:
        arch = archivo + '.csv'
        archivoDestino = open(arch, 'a', encoding="utf8", newline='')
        writer = csv.DictWriter(archivoDestino, fieldnames=lista[0].keys(), dialect='excel')
        writer.writerows(lista)
    except NameError:
        print(NameError)