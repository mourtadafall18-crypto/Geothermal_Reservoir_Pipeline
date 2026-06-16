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

USE GeoEnergy_Exploration;

-- Évolution de la table pour accueillir le scénario UK v2.0
ALTER TABLE Well_Logs 
ADD COLUMN formation_name VARCHAR(150) AFTER temperature_celsius,
ADD COLUMN fracture_density_per_m INT AFTER formation_name,
ADD COLUMN is_fault_zone BOOLEAN DEFAULT FALSE AFTER fracture_density_per_m,
ADD COLUMN dip_angle FLOAT AFTER is_fault_zone;
--  Modifier les colonnes pour accepter les valeurs NULL
ALTER TABLE Well_Logs MODIFY COLUMN porosity_pct FLOAT NULL;
ALTER TABLE Well_Logs MODIFY COLUMN gamma_ray_api FLOAT NULL;
-- Optionnel : Vider les anciennes données pour repartir sur du propre
SET SQL_SAFE_UPDATES = 0;
DELETE FROM Well_Logs;
DELETE FROM Wells;
SET SQL_SAFE_UPDATES = 1;

-- Vérification de la nouvelle structure
DESCRIBE Well_Logs;
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

-- 1. Calcul des intervalles réels entre chaque mesure de diagraphie
WITH LogIntervals AS (
    SELECT 
        well_id,
        depth_meters,
        clean_porosity_pct,
        gamma_ray_api,
        smoothed_temperature_celsius,
        -- LEAD récupère la profondeur de la ligne suivante pour calculer l'épaisseur du banc
        LEAD(depth_meters) OVER(PARTITION BY well_id ORDER BY depth_meters) - depth_meters AS sample_thickness
    FROM v_clean_well_logs
),

-- 2. Isolement des caractéristiques uniques au réservoir (Gamma Ray < 65 API)
ReservoirSegments AS (
    SELECT 
        well_id,
        -- Si le segment répond aux critères, on retient son épaisseur réelle, sinon 0
        CASE WHEN gamma_ray_api < 65 THEN COALESCE(sample_thickness, 1.0) ELSE 0 END AS net_reservoir_thickness,
        CASE WHEN gamma_ray_api < 65 THEN clean_porosity_pct ELSE NULL END AS reservoir_porosity,
        smoothed_temperature_celsius
    FROM LogIntervals
)

-- 3. Agrégation finale par forage avec calcul d'un indice de qualité (Net Pay Zone)
SELECT 
    w.well_name,
    ROUND(SUM(r.net_reservoir_thickness), 1) AS reservoir_thickness_cumulee_m,
    ROUND(AVG(r.reservoir_porosity), 2) AS mean_porosity__reservoir_pct,
    ROUND(MAX(r.smoothed_temperature_celsius), 1) AS temp_max_detectee_c,
    -- Indice de Qualité du Réservoir (Épaisseur utile x Porosité moyenne)
    ROUND(SUM(r.net_reservoir_thickness) * AVG(r.reservoir_porosity), 0) AS score_potentiel_geothermique
FROM ReservoirSegments r
JOIN Wells w ON r.well_id = w.well_id
GROUP BY w.well_id, w.well_name
ORDER BY score_potentiel_geothermique DESC;