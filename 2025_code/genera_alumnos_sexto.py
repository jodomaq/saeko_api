"""Este código genera la plantilla para subir a los alumnos de sexto próximos a egresar,
a partir del listado de alumnos que se genera en saeko v2
Se selecciona en el listado genero, correo, escuela, plan estudios, grado, grupo, turno, promedio, estado, curp"""

from funciones import *
from datos import *
import datetime as dt
lin = 1
current_date_and_time = dt.datetime.now()
for fuente in alu_fuente_lista:
    try:
        _clave_carrera = clave_carrera(fuente["PLAN_DE_ESTUDIOS"], carreras_lista, fuente['ESCUELA'])
        #print(fuente)
        alu_destino["COLEGIO"] = "Michoacán" # 1
        lin = lin +1
        alu_destino["CCT"] = cct(fuente["ESCUELA"], clave_plantel_rev, _clave_carrera) # 2
        lin = lin +1
        alu_destino["NOMBRE_DE_PLANTEL"] = clave_plantel[alu_destino["CCT"]]
        #alu_destino["NOMBRE_DE_PLANTEL"] = fuente["ESCUELA"] # 3
        lin = lin +1
        alu_destino["TURNO"] = fuente["TURNO"] # 4
        lin = lin +1
        alu_destino["VERSION_CARRERA"] = "V23" # 5
        lin = lin +1
        alu_destino["CLAVE_CARRERA"] = _clave_carrera # 6
        lin = lin +1
        alu_destino["NOMBRE_CARRERA"] = nombre_carrera(alu_destino["CLAVE_CARRERA"], carreras_lista, fuente['ESCUELA']) # 7
        lin = lin +1
        alu_destino["MATRICULA"] = matricula(fuente["MATRICULA"]) # 8
        lin = lin +1
        alu_destino["NOMBRE"] = fuente["NOMBRE"] # 9
        lin = lin +1
        alu_destino["PRIMER_APELLIDO"] = fuente["PRIMER_APELLIDO"] # 10
        lin = lin +1
        alu_destino["SEGUNDO_APELLIDO"] = fuente["SEGUNDO_APELLIDO"] # 11
        lin = lin +1
        alu_destino["CURP"] = validar_curp_raise(fuente["CURP"], fuente["NOMBRE"], fuente["PRIMER_APELLIDO"], fuente["SEGUNDO_APELLIDO"]) # 12
        lin = lin +1
        alu_destino["GENERO"] = obtener_genero(fuente["GENERO"]) # 13
        lin = lin +1
        alu_destino["CORREO_ELECTRONICO"] = fuente["CORREO_INSTITUCIONAL"] # 14
        lin = lin +1
        alu_destino["GRUPO"] = fuente["GRUPO"] # 15
        lin = lin +1
        alu_destino_lista.append(alu_destino.copy())
        lin = 1
    except Exception as e:
        print(fuente['ESCUELA'] + " " + fuente['NOMBRE'] + " " + fuente['PRIMER_APELLIDO'] + " " + fuente['SEGUNDO_APELLIDO'] + " " + fuente['CURP'] + " Error: " + str(e))
        grabar_linea("./resultado/errores "+current_date_and_time.strftime("%Y-%m-%d %H-%M-%S"), {"plantel": fuente["ESCUELA"],
                                 "nombre": fuente["NOMBRE"],
                                 "paterno": fuente["PRIMER_APELLIDO"],
                                 "materno": fuente["SEGUNDO_APELLIDO"],
                                 "matricula": fuente["CURP"],
                                 "error": str(e) + " " + str(lin)
                                 })
        lin = 1


print(current_date_and_time.strftime("%Y-%m-%d %H-%M-%S"))
grabar_lista_archivo("./resultado/carga "+current_date_and_time.strftime("%Y-%m-%d %H-%M-%S"), alu_destino_lista)