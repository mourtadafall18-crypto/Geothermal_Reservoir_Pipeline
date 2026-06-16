-- 1. Création et activation de la base de données
CREATE DATABASE IF NOT EXISTS GeoEnergy_Exploration;
USE GeoEnergy_Exploration;

-- 2. Nettoyage des anciennes tables si elles existent (pour repartir à neuf)
DROP TABLE IF EXISTS Well_Logs;
DROP TABLE IF EXISTS Wells;

-- 3. Table des Forages (Métadonnées spatiales)
CREATE TABLE Wells (
    well_id INT PRIMARY KEY,
    well_name VARCHAR(50) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    total_depth_meters DECIMAL(10, 2) NOT NULL
) ENGINE=InnoDB;

-- 4. Table des Mesures de Diagraphie (Données Haute Résolution)
CREATE TABLE Well_Logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    well_id INT,
    depth_meters DECIMAL(10, 2) NOT NULL,
    gamma_ray_api DECIMAL(6, 2) NULL,          -- NULL autorisé pour simuler les pannes
    porosity_pct DECIMAL(5, 2) NOT NULL,
    temperature_celsius DECIMAL(5, 2) NOT NULL,
    FOREIGN KEY (well_id) REFERENCES Wells(well_id) ON DELETE CASCADE
) ENGINE=InnoDB;
USE GeoEnergy_Exploration;
describe well_analytics;
-- Ajout de la colonne pour stocker la température moyenne du Net Pay
ALter TABLE Well_Analytics 
ADD COLUMN reservoir_temp_celsius DOUBLE AFTER ntg_percentage;well_analytics
describe well_analytics;
-- Ajout des colonnes pour le dimensionnement hydraulique (Étape 3) au cas où elles manquent
ALTER TABLE Well_Analytics 
ADD COLUMN required_flow_rate_m3h DOUBLE AFTER required_flow_rate_lps;

SELECT well_id, net_pay, thermal_power_mwth, reservoir_temp_celsius 
FROM Well_Analytics;
SELECT AVG(temperature_celsius) 
FROM Well_Logs 
WHERE well_id = 1 AND gamma_ray_api <= 65.0 AND porosity_pct >= 8.0;
SELECT gamma_ray_api, porosity_pct 
FROM Well_Logs 
WHERE well_id = 1 
LIMIT 10;

select*from well_analytics;
ALTER TABLE Well_Logs 
ADD COLUMN formation_name VARCHAR(255),
ADD COLUMN fracture_density_per_m INT,
ADD COLUMN is_fault_zone INT,
ADD COLUMN dip_angle FLOAT;
ALTER TABLE Well_Logs 
MODIFY COLUMN porosity_pct FLOAT NULL,
MODIFY COLUMN gamma_ray_api FLOAT NULL,
MODIFY COLUMN dip_angle FLOAT NULL;
-- cleaning DATA
CREATE OR REPLACE VIEW v_well_logs_cleaned AS
SELECT 
    well_id,
    depth_meters,
    COALESCE(gamma_ray_api, 0.0) AS gamma_ray_api,
    COALESCE(porosity_pct, 0.0) AS porosity_pct,
    COALESCE(temperature_celsius, 10.0) AS temperature_celsius, -- 10°C par défaut si rien
    formation_name,
    fracture_density_per_m,
    is_fault_zone,
    dip_angle
FROM Well_Logs;
DROP TABLE IF EXISTS GeoEnergy_Exploration.Well_Logs_Enriched;well_logs_enriched
select* from well_logs_enriched;
USE GeoEnergy_Exploration;
USE GeoEnergy_Exploration;

DROP TABLE IF EXISTS Well_Logs_Enriched;

CREATE TABLE Well_Logs_Enriched (
    well_id INT,
    depth_meters FLOAT,
    gamma_ray_api FLOAT,
    porosity_pct FLOAT,
    temperature_celsius FLOAT,
    formation_name VARCHAR(255),
    fracture_density_per_m FLOAT,
    is_fault_zone INT,
    dip_angle FLOAT,
    lithology VARCHAR(255),
    temp_diff FLOAT,well_logs_enriched
    depth_diff FLOAT,
    geothermal_gradient_c_per_km FLOAT
);
DROP TABLE IF EXISTS Well_Logs_Enriched;

CREATE TABLE Well_Logs_Enriched (
    log_id FLOAT,
    well_name VARCHAR(100),
    well_id INT,
    depth_meters FLOAT,
    clean_porosity_pct FLOAT,
    gamma_ray_api FLOAT,
    raw_temperature FLOAT,
    smoothed_temperature_celsius FLOAT,
    lithology VARCHAR(100),
    temp_diff FLOAT,
    depth_diff FLOAT,
    geothermal_gradient_c_per_km FLOAT
);
select*From well_logs_enriched;

SELECT 
    MIN(smoothed_temperature_celsius) AS temp_min, 
    AVG(smoothed_temperature_celsius) AS temp_moy, 
    MAX(smoothed_temperature_celsius) AS temp_max,
    COUNT(*) AS nombre_mesures
FROM Well_Logs_Enriched 
WHERE well_id = 3 
AND lithology = 'Reservoir (Sandstone)';
SELECT 
    well_id, 
    formation_name, 
    net_pay, 
    reservoir_temp_celsius, 
    heat_in_place_pj, 
    thermal_power_mwth 
FROM Well_Analytics;
-- 1. Ajouter les colonnes manquantes à Well_Logs_Enriched
ALTER TABLE Well_Logs_Enriched 
ADD COLUMN formation_name VARCHAR(255),
ADD COLUMN fracture_density_per_m FLOAT,
ADD COLUMN is_fault_zone BOOLEAN,
ADD COLUMN dip_angle FLOAT;

select*from well_logs_enriched;
SELECT count(*), formation_name 
FROM Well_Logs_Enriched 
GROUP BY formation_name;
SELECT e.well_id, e.depth_meters AS depth_e, o.depth_meters AS depth_o
FROM Well_Logs_Enriched e
LEFT JOIN Well_Logs o ON e.well_id = o.well_id 
-- On compare les entiers pour voir s'il y a des correspondances
WHERE FLOOR(e.depth_meters) = FLOOR(o.depth_meters)
LIMIT 10;
