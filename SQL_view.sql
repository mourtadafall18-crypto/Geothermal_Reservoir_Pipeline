USE GeoEnergy_Exploration;

-- Création de la vue analytique nettoyée
CREATE OR REPLACE VIEW v_clean_well_logs AS
SELECT 
    wl.log_id,
    w.well_name,
    wl.well_id,
    wl.depth_meters,
    
    -- 1. Nettoyage de la porosité : les -999.0 deviennent des NULL propres
    CASE 
        WHEN wl.porosity_pct < 0 THEN NULL 
        ELSE wl.porosity_pct 
    END AS clean_porosity_pct,
    
    -- 2. Récupération du Gamma Ray (on garde les NULL pour la Phase 3)
    wl.gamma_ray_api,
    
    -- 3. Température brute pour comparaison
    wl.temperature_celsius AS raw_temperature,
    
    -- 4. WINDOW FUNCTION : Lissage de la température (Moyenne mobile centrée sur 5 lignes)
    AVG(wl.temperature_celsius) OVER(
        PARTITION BY wl.well_id 
        ORDER BY wl.depth_meters 
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ) AS smoothed_temperature_celsius

FROM Well_Logs wl
JOIN Wells w ON wl.well_id = w.well_id;
SELECT * FROM v_clean_well_logs WHERE well_id = 1 LIMIT 20;