DROP DATABASE IF EXISTS parque;

CREATE DATABASE parque;

USE parque;

CREATE TABLE dispositivos (
    id_dispositivo INTEGER NOT NULL COMMENT "ID del Dispositivo",
    temperatura_dis INTEGER NOT NULL COMMENT "Temperatura del Dispositivo",
    humedad_dis INTEGER NOT NULL COMMENT "Humedad del Dispositivo",
    lluvia_dis INTEGER NOT NULL COMMENT "Lluvia del Dispositivo",
    humedad_suelo_dis INTEGER NOT NULL COMMENT "Humedad del Suelo del Dispositivo",
    monoxido_carbon_dis INTEGER NOT NULL COMMENT "Monóxido de Carbón del Dispositivo",
    pulso_emergencia_dis INTEGER NOT NULL COMMENT "Pulso de Emergencia del Dispositivo",
    PRIMARY KEY(id_dispositivo)
) COMMENT "Tabla de Dispositivos";

CREATE TABLE usuarios (
    cedula_usu INTEGER NOT NULL COMMENT "ID del Usuario",
    nombre_usu VARCHAR(15) NOT NULL COMMENT "Nombre del Usuario",
    apellido_usu VARCHAR(15) NOT NULL COMMENT "Apellido del Usuario",
    celular_usu INTEGER(10) NOT NULL COMMENT "Celular del Usuario",
    fecha_usu DATE NOT NULL COMMENT "Fecha de registro",
    id_dispositivo INTEGER COMMENT "ID del Dispositivo",
    PRIMARY KEY(cedula_usu),
    FOREIGN KEY(id_dispositivo) REFERENCES dispositivos(id_dispositivo)
) COMMENT "Tabla de Usuarios";

CREATE TABLE gps (
    id_gps INTEGER NOT NULL COMMENT "ID del GPS",
    latitud_gps TEXT NOT NULL COMMENT "Latitud del GPS",
    longitud_gps TEXT NOT NULL COMMENT "Longitud del GPS",
    altura_gps TEXT NOT NULL COMMENT "Altura del GPS",
    id_dispositivo INTEGER NOT NULL COMMENT "ID del Dispositivo",
    PRIMARY KEY(id_gps),
    FOREIGN KEY(id_dispositivo) REFERENCES dispositivos(id_dispositivo)
) COMMENT "Tabla de GPS";

CREATE TABLE ruta (
    id_ruta INTEGER NOT NULL AUTO_INCREMENT COMMENT "ID de la ruta",
    latitud_rut TEXT NOT NULL COMMENT "Latitud de la Ruta",
    longitud_rut TEXT NOT NULL COMMENT "Longitud de la Ruta",
    altura_rut TEXT NOT NULL COMMENT "Altura de la Ruta",
    id_gps INTEGER NOT NULL COMMENT "ID del GPS",
    PRIMARY KEY(id_ruta),
    FOREIGN KEY(id_gps) REFERENCES gps(id_gps)
) COMMENT "Tabla de la ruta";

CREATE TABLE auditoria (
    id_auditoria INTEGER NOT NULL AUTO_INCREMENT COMMENT "ID de la Auditoría",
    cedula_usu INTEGER NOT NULL COMMENT "ID del Usuario",
    id_dispositivo INTEGER NOT NULL COMMENT "ID del Dispositivo",
    fecha_aud DATE NOT NULL COMMENT "Fecha de la Auditoría",
    PRIMARY KEY(id_auditoria),
    FOREIGN KEY(cedula_usu) REFERENCES usuarios(cedula_usu),
    FOREIGN KEY(id_dispositivo) REFERENCES dispositivos(id_dispositivo)
) COMMENT "Tabla de Auditoría";

CREATE TABLE ruta_auditoria (
    id_rutaud INTEGER NOT NULL AUTO_INCREMENT COMMENT "ID de la auditoría de la ruta",
    id_auditoria INTEGER NOT NULL COMMENT "ID de la Auditoría",
    latitud_rutaud TEXT NOT NULL COMMENT "Latitud de la Ruta",
    longitud_rutaud TEXT NOT NULL COMMENT "Longitud de la Ruta",
    altura_rutaud TEXT NOT NULL COMMENT "Altura de la Ruta",
    temperatura_rutaud INTEGER NOT NULL,
    PRIMARY KEY (id_rutaud),
    FOREIGN KEY (id_auditoria) REFERENCES auditoria (id_auditoria)
) COMMENT "Tabla de Auditoría sobre la ruta";

INSERT INTO dispositivos (id_dispositivo, temperatura_dis, humedad_dis, lluvia_dis, humedad_suelo_dis, monoxido_carbon_dis, pulso_emergencia_dis) VALUES (0, 0, 0, 0, 0, 0, 0);