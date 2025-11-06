
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS crimenes_db_clean;
USE crimenes_db_clean;

-- Tabla de fechas (dimensión)
CREATE TABLE dim_fecha (
    id_fecha INT AUTO_INCREMENT PRIMARY KEY,
    year INT,
    month INT,
    day INT
);

-- Tabla de horas (dimensión)
CREATE TABLE dim_hora (
    id_hora INT AUTO_INCREMENT PRIMARY KEY,
    time TIME
);

-- Tabla de ubicación (dimensión)
CREATE TABLE dim_ubicacion (
    id_ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    district INT,
    community_area INT, 
    location_description VARCHAR(255)
);

-- Tabla de tipo de crimen (dimensión)
CREATE TABLE dim_tipo (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    iucr VARCHAR(10),
    description VARCHAR(255),
);

-- Tabla de arresto (dimensión)
CREATE TABLE dim_arresto (
    id_arresto INT AUTO_INCREMENT PRIMARY KEY,
    arrest BOOLEAN
);

-- Tabla de hechos (fact table)
CREATE TABLE hecho_crimenes (
    case_number VARCHAR(50) PRIMARY KEY,
    updated_date DATETIME,
    id_fecha INT,
    id_hora INT,
    id_ubicacion INT,
    id_tipo INT,
    id_arresto INT,
    FOREIGN KEY (id_fecha) REFERENCES dim_fecha(id_fecha),
    FOREIGN KEY (id_hora) REFERENCES dim_hora(id_hora),
    FOREIGN KEY (id_ubicacion) REFERENCES dim_ubicacion(id_ubicacion),
    FOREIGN KEY (id_tipo) REFERENCES dim_tipo(id_tipo),
    FOREIGN KEY (id_arresto) REFERENCES dim_arresto(id_arresto)
);
