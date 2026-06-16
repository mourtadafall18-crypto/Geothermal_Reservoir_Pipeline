import mysql.connector
import pandas as pd
from config import WELL_CONFIGS

def run_geothermal_heat_in_place_pipeline():
    print("🔌 Connexion à GeoEnergy (Module Heat In Place sur données nettoyées)...")
    conn = mysql.connector.connect(
        host="localhost", user="root", password="mourtada@123", database="GeoEnergy_Exploration"
    )
    cursor = conn.cursor()

    # Récupération des données Net Pay déjà calculées
    query = "SELECT well_id, net_pay FROM Well_Analytics;"
    df_analytics = pd.read_sql(query, conn)

    for _, row in df_analytics.iterrows():
        well_id = int(row['well_id'])
        net_pay = float(row['net_pay'])
        
        if well_id not in WELL_CONFIGS or net_pay <= 0:
            continue
            
        cfg = WELL_CONFIGS[well_id]

        # 1. Calcul de la température moyenne du réservoir (DIRECTEMENT sur la table nettoyée)
        # On utilise lithology et clean_porosity_pct au lieu des seuils bruts
        t_query = f"""
            SELECT AVG(smoothed_temperature_celsius) 
            FROM Well_Logs_Enriched 
            WHERE well_id = {well_id} 
            AND lithology = 'Reservoir (Sandstone)'
            AND clean_porosity_pct >= {cfg.get('poro_cut', 0.0)};
        """
        cursor.execute(t_query)
        result = cursor.fetchone()[0]
        t_r = float(result) if result else 25.0

        # 2. Paramètres physiques
        rho_r, c_r = cfg.get('rho_r', 2650), cfg.get('c_r', 880)
        phi = cfg.get('phi', 0.10)
        
        # Constantes
        rho_f, c_f, t_0 = 950.0, 4180.0, 10.0
        area = 1000000.0 # 1 km²
        r_f = 0.15 
        duration_seconds = 30 * 365 * 24 * 3600

        # 3. Équation Volumetric Heat In Place
        matrix_cap = (1.0 - phi) * rho_r * c_r
        fluid_cap = phi * rho_f * c_f
        
        q_joules = area * net_pay * (matrix_cap + fluid_cap) * max(0, t_r - t_0)
        q_pj = float(q_joules / 1e15)
        p_th_mw = float((q_joules * r_f) / (duration_seconds * 1e6))

        # 4. Mise à jour SQL
        cursor.execute("""
            UPDATE Well_Analytics 
            SET heat_in_place_pj = %s, thermal_power_mwth = %s, reservoir_temp_celsius = %s
            WHERE well_id = %s;
        """, (q_pj, p_th_mw, t_r, well_id))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Calculs 'Heat In Place' mis à jour avec précision sur données nettoyées.")

if __name__ == "__main__":
    run_geothermal_heat_in_place_pipeline()