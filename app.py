from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
import math

app = Flask(__name__)
CORS(app)

base_datos = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="parque"
)

cursor = base_datos.cursor()

if os.path.exists('manejador.txt'):
    os.remove('manejador.txt')

nuevo_archivo = open('manejador.txt', 'a')
nuevo_archivo.write('0')
nuevo_archivo.close()

# USUARIOS
@app.route('/usuarios/auditlogs/<idcard>/<page>', methods=['POST'])
def auditLogs(idcard, page):
    data = request.json
    skip = (10 * int(page)) - 10

    if data:
        cursor.execute('SELECT * FROM auditoria WHERE id_dispositivo = %s OR fecha_aud LIKE %s ORDER BY fecha_aud DESC LIMIT 10 OFFSET %s', (data['dataSearch'], "%"+data['dataSearch']+"%", skip, ))
    else:
        cursor.execute('SELECT * FROM auditoria WHERE cedula_usu = %s ORDER BY id_auditoria DESC', (idcard, ))

    auditLogs = cursor.fetchall()

    if auditLogs == []:
        return jsonify (
            msg = 'No se han encontrado resultados los datos ' + data['dataSearch'],
            error = True
        )
    else:
        return jsonify (
            msg = auditLogs,
            max = math.ceil(len(auditLogs) / 10),
            error = False
        )

@app.route('/usuarios/<page>', methods=['POST'])
def usuarios(page):
    data = request.json
    skip = (10 * int(page)) - 10

    if data:
        cursor.execute('SELECT * FROM usuarios WHERE cedula_usu = %s OR nombre_usu = %s OR apellido_usu = %s OR celular_usu = %s ORDER BY fecha_usu DESC LIMIT 10 OFFSET %s', (data['dataSearch'], data['dataSearch'], data['dataSearch'], data['dataSearch'], skip, ))
    else:
        cursor.execute('SELECT * FROM usuarios ORDER BY fecha_usu DESC LIMIT 10 OFFSET %s', (skip, ))

    usersList = cursor.fetchall()

    return jsonify (
        usuarios = usersList,
        maximo = math.ceil(len(usersList) / 10),
        error = False
    )

@app.route('/usuario/<cedula>')
def Datos_Usuario(cedula):
    cursor.execute('SELECT * FROM usuarios WHERE cedula_usu = %s', (cedula, ))
    datosUsuario = cursor.fetchone()

    return jsonify (
        usuario = datosUsuario,
        error = False
    )

@app.route("/usuario/actualizar", methods=['POST'])
def Actualizar_Usuario():
    datos = request.json

    cursor.execute('UPDATE usuarios SET nombre_usu = %s, apellido_usu = %s, celular_usu = %s', (datos['nombre'], datos['apellido'], datos['celular']))
    base_datos.commit()

    return jsonify (
        mensaje = 'Usuario editado correctamente',
        error = False
    )

@app.route('/usuario/eliminar', methods=['POST'])
def Eliminar_Usuario():
    cedula = request.json

    cursor.execute('DELETE FROM usuarios WHERE cedula_usu = %s', (cedula, ))
    base_datos.commit()

    return jsonify (
        mensaje = "Usuario eliminado correctamente",
        error = False
    )

@app.route('/usuarios/asignados')
def Index():
    cursor.execute('SELECT * FROM usuarios WHERE NOT id_dispositivo = "null" AND NOT id_dispositivo = 0')
    consulta = cursor.fetchall()
    if consulta == []:
        return jsonify(
            asignados = False,
            usuarios = 'No hay usuarios asignados'
        )
    else:
        usuarios = []
        for fila in consulta:
            usuarios.append({
                'cedula_usu': fila[0],
                'nombre_usu': fila[1],
                'apellido_usu': fila[2],
                'celular_usu': fila[3],
                'fecha_usu': fila[4],
                'id_dispositivo': fila[5]
            })
        return jsonify(
            asignados = True,
            usuarios = usuarios
        )

@app.route('/usuarios/validar', methods=['POST'])
def validar_usuario():
    datos = request.json
    cursor.execute('SELECT * FROM usuarios WHERE cedula_usu = %s', (datos['cedula'], ))
    usuario = cursor.fetchall()

    if usuario == []:
        return jsonify(
            existe = False,
            mensaje = 'Cédula no registrada'
        )
    else:
        return jsonify(
            existe = True,
            mensaje = 'Cédula ya reigstrada'
        )

@app.route('/usuarios/registrar', methods=['POST'])
def registrar_usuario():
    datos = request.json
    cursor.execute('INSERT INTO usuarios (cedula_usu, nombre_usu, apellido_usu, celular_usu, fecha_usu) VALUES (%s, %s, %s, %s, %s)', (datos['cedula'], datos['nombre'], datos['apellido'], datos['celular'], datos['fecha']))
    base_datos.commit()

    return jsonify(
        registro = True,
        mensaje = 'Usuario registrado con éxito'
    )

# DISPOSITIVOS
@app.route('/dispositivo/asignar', methods=['POST'])
def asignar_dispositivo():
    datos = request.json
    cursor.execute('SELECT * FROM usuarios WHERE cedula_usu = %s', (datos['cedula'], ))
    usuario = cursor.fetchone()
    cursor.execute('SELECT * FROM usuarios WHERE id_dispositivo = %s', (datos['dispositivo'], ))
    dispositivo = cursor.fetchall()
    id_gps = int(datos['dispositivo']) + 1

    if usuario[5] != None and usuario[5] != 0:
        return jsonify(
            asignado = True,
            mensaje = 'Ya se le ha asignado un dispositivo a este usuario'
        )
    elif dispositivo != []:
        return jsonify(
            asignado = True,
            mensaje = 'El dispositivo ya fue asignado a otro usuario'
        )
    else:
        cursor.execute('SELECT * FROM dispositivos WHERE id_dispositivo = %s', (datos['dispositivo'], ))
        eldispositivo = cursor.fetchone()

        if eldispositivo == None:
            cursor.execute('INSERT INTO dispositivos (id_dispositivo, temperatura_dis, humedad_dis, lluvia_dis, humedad_suelo_dis, monoxido_carbon_dis, pulso_emergencia_dis) VALUES (%s, %s, %s, %s, %s, %s, %s)', (datos['dispositivo'], 0, 0, 0, 0, 0, 0))
            base_datos.commit()
            cursor.execute('INSERT INTO gps (id_gps, latitud_gps, longitud_gps, altura_gps, id_dispositivo) VALUES (%s, %s, %s, %s, %s)', (id_gps, 0, 0, 0, datos['dispositivo']))
            base_datos.commit()
            cursor.execute('INSERT INTO ruta (latitud_rut, longitud_rut, altura_rut, id_gps) VALUES (%s, %s, %s, %s)', (0, 0, 0, id_gps))
            base_datos.commit()
            cursor.execute('UPDATE usuarios SET id_dispositivo = %s WHERE cedula_usu = %s', (datos['dispositivo'], datos['cedula']))
            base_datos.commit()
            cursor.execute('UPDATE gps SET latitud_gps = %s, longitud_gps = %s, altura_gps = %s WHERE id_dispositivo = %s', (datos['latitud'], datos['longitud'], datos['altura'], datos['dispositivo']))
            base_datos.commit()
            cursor.execute('UPDATE ruta SET latitud_rut = %s, longitud_rut = %s, altura_rut = %s WHERE id_gps = %s', (datos['latitud'], datos['longitud'], datos['altura'], id_gps))
            base_datos.commit()
            cursor.execute('INSERT INTO auditoria (cedula_usu, id_dispositivo, fecha_aud) VALUES (%s, %s, %s)', (datos['cedula'], datos['dispositivo'], datos['fecha']))
            base_datos.commit()

            return jsonify (
                asignado = False,
                mensaje = 'Dispositivo asignado correctamente'
            )
        else:
            cursor.execute('UPDATE usuarios SET id_dispositivo = %s WHERE cedula_usu = %s', (datos['dispositivo'], datos['cedula']))
            base_datos.commit()
            cursor.execute('UPDATE gps SET latitud_gps = %s, longitud_gps = %s, altura_gps = %s WHERE id_dispositivo = %s', (datos['latitud'], datos['longitud'], datos['altura'], datos['dispositivo']))
            base_datos.commit()
            cursor.execute('UPDATE ruta SET latitud_rut = %s, longitud_rut = %s, altura_rut = %s WHERE id_gps = %s', (datos['latitud'], datos['longitud'], datos['altura'], id_gps))
            base_datos.commit()
            cursor.execute('INSERT INTO auditoria (cedula_usu, id_dispositivo, fecha_aud) VALUES (%s, %s, %s)', (datos['cedula'], datos['dispositivo'], datos['fecha']))
            base_datos.commit()

            return jsonify (
                asignado = False,
                mensaje = 'Dispositivo asignado correctamente'
            )

@app.route('/dispositivo/informacion/<id_dispositivo>')
def informacion_dispositivo(id_dispositivo):
    cursor.execute('SELECT * FROM dispositivos WHERE id_dispositivo = %s', (id_dispositivo, ))
    informacion = cursor.fetchone()

    if informacion == None:
        return jsonify (
            error = True,
            mensaje = 'El dispositivo no está en la Base de Datos'
        )
    else:
        return jsonify (
            error = False,
            mensaje = informacion
        )

@app.route('/dispositivo/eliminar', methods=['POST'])
def eliminar_dispositivo():
    data = request.json
    cursor.execute('UPDATE usuarios SET id_dispositivo = %s WHERE cedula_usu = %s', (0, data['cedula_usuario']))
    base_datos.commit()
    cursor.execute('UPDATE dispositivos SET temperatura_dis = %s, humedad_dis = %s, lluvia_dis = %s, humedad_suelo_dis = %s, monoxido_carbon_dis = %s, pulso_emergencia_dis = %s WHERE id_dispositivo = %s', (0, 0, 0, 0, 0, 0, data['id_dispositivo']))
    base_datos.commit()
    cursor.execute('UPDATE gps SET latitud_gps = %s, longitud_gps = %s, altura_gps = %s WHERE id_dispositivo = %s', (0, 0, 0, data['id_dispositivo']))
    base_datos.commit()

    el_gps = data['id_dispositivo'] + 1
    cursor.execute('DELETE FROM ruta WHERE id_gps = %s', (el_gps, ))

    return jsonify (
        error = False,
        mensaje = 'Dispositivo desasignado, la página se recargará para mostrar los cambios'
    )

# UBICACIÓN
@app.route('/ruta', methods=['POST'])
def rutas():
    # Recibir datos del frontend
    datos = request.json

    # Leer archivo de sensores
    archivo = open('datos.txt', 'r')
    dispositivo = archivo.readlines()
    cantidadLineas = len(dispositivo) - 1
    archivo.close()

    # Leer archivo manejador
    archivo_manejador = open('manejador.txt', 'r')
    numero_manejador = int(archivo_manejador.read())
    archivo_manejador.close()

    # Sobre escribir archivo manejador
    archivo_manejador = open('manejador.txt', 'w')
    cantidadLineas = str(cantidadLineas)
    archivo_manejador.write(cantidadLineas)
    archivo_manejador.close()

    cantidadLineas = int(cantidadLineas)

    # Recopilar los datos del archivo de cada usuario
    for usuarios in datos:
        i = numero_manejador
        gps = int(usuarios['id_dispositivo']) + 1
        gps_cantidad = 0
        info_dis = 0
        temperature = []

        # Recolectar Información sobre cuanta ID GPS y ID dispositivos hay del usuario
        while i <= cantidadLineas:
            informacion = dispositivo[i].split()

            if informacion != [] and informacion[0] != 'CRC':
                comparar = int(informacion[0])

                if comparar == usuarios['id_dispositivo']:
                    info_dis += 1

                if comparar == gps:
                    gps_cantidad += 1
            i += 1

        # Guardar/Actualizar en la Base de Datos
        i = numero_manejador
        update_dis = 0
        update_gps = 0

        while i <= cantidadLineas:
            informacion = dispositivo[i].split()

            if informacion != [] and informacion[0] != 'CRC':
                comparar = int(informacion[0])

                if comparar == usuarios['id_dispositivo']:

                    update_dis += 1
                    temperature.append(int(informacion[1]))

                    if update_dis == info_dis:
                        cursor.execute('UPDATE dispositivos SET temperatura_dis = %s, humedad_dis = %s, lluvia_dis = %s, humedad_suelo_dis = %s, monoxido_carbon_dis = %s, pulso_emergencia_dis = %s WHERE id_dispositivo = %s', (informacion[1], informacion[2], informacion[3], informacion[4], informacion[5], informacion[6], usuarios['id_dispositivo']))
                        base_datos.commit()

                if comparar == gps:
                    update_gps += 1
                    if update_gps == gps_cantidad:
                        cursor.execute('UPDATE gps SET latitud_gps = %s, longitud_gps = %s, altura_gps = %s WHERE id_gps = %s', (informacion[1], informacion[2], informacion[3], gps))
                        base_datos.commit()
                    else:
                        cursor.execute('INSERT INTO ruta (latitud_rut, longitud_rut, altura_rut, id_gps) VALUES (%s, %s, %s, %s)', (informacion[1], informacion[2], informacion[3], gps))
                        base_datos.commit()

                        cursor.execute('SELECT * FROM auditoria WHERE cedula_usu = %s ORDER BY id_auditoria DESC', (usuarios['cedula_usu'], ))
                        audit = cursor.fetchall()

                        audit_id = audit[0][0]
                        numtemp = len(temperature) - 1

                        cursor.execute('INSERT INTO ruta_auditoria (id_auditoria, latitud_rutaud, longitud_rutaud, altura_rutaud, temperatura_rutaud) VALUES (%s, %s, %s, %s, %s)', (audit_id, informacion[1], informacion[2], informacion[3], temperature[numtemp]))
                        base_datos.commit()
            i += 1

    cursor.execute('SELECT * FROM gps WHERE NOT latitud_gps = 0 AND NOT longitud_gps = 0')
    ubicacion = cursor.fetchall()
    cursor.execute('SELECT * FROM ruta')
    ruta = cursor.fetchall()

    return jsonify (
        ubicacion = ubicacion,
        rutas = ruta
    )

@app.route('/ruta/auditoria/<auditid>')
def auditPath(auditid):
    cursor.execute('SELECT * FROM ruta_auditoria WHERE id_auditoria = %s', (auditid, ))
    paths = cursor.fetchall()

    if paths == []:
        return jsonify (
            error = True,
            msg = 'No hay registros de una ruta'
        )
    else:
        return jsonify (
            error = False,
            msg = paths
        )

    return jsonify (
        paths = paths,
        error = False
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)