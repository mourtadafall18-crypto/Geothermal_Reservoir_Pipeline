import mysql.connector
import pandas as pd
from config import WELL_CONFIGS

def run_hydraulic_production_pipeline():
    print("🔌 Connexion à GeoEnergy (Module Hydraulique sur données nettoyées)...")
    conn = mysql.connector.connect(
        host="localhost", user="root", password="mourtada@123", database="GeoEnergy_Exploration"
    )
    cursor = conn.cursor()

    # Lecture des données analytiques (données propres)
    query = "SELECT well_id, thermal_power_mwth, reservoir_temp_celsius FROM Well_Analytics;"
    df = pd.read_sql(query, conn)

    # Paramètres physiques
    RHO_F, C_F = 950.0, 4180.0
    # On ajuste T_REJET à 10°C pour correspondre à vos tests précédents
    T_REJET = 10.0 

    for _, row in df.iterrows():
        well_id = int(row['well_id'])
        p_th_mw = float(row['thermal_power_mwth'])
        t_res = float(row['reservoir_temp_celsius'])

        # Mise à jour des conditions de sécurité
        # On évite la division par zéro si t_res est trop proche de T_REJET
        if well_id not in WELL_CONFIGS or p_th_mw <= 0 or t_res <= (T_REJET + 0.1):
            print(f"   ↳ Puits {well_id} : Potentiel insuffisant pour ce seuil (T_rejet={T_REJET}°C).")
            cursor.execute("UPDATE Well_Analytics SET required_flow_rate_lps = 0, required_flow_rate_m3h = 0 WHERE well_id = %s;", (well_id,))
            continue

        # Calcul du débit basé sur la conservation de l'énergie
        delta_t = t_res - T_REJET
        flow_m3_per_s = (p_th_mw * 1e6) / (RHO_F * C_F * delta_t)
        
        flow_lps = float(flow_m3_per_s * 1000.0)
        flow_m3h = float(flow_m3_per_s * 3600.0)

        print(f"   ↳ Puits {WELL_CONFIGS[well_id]['name']} : Débit requis = {flow_lps:.1f} L/s ({flow_m3h:.1f} m³/h)")

        cursor.execute("""
            UPDATE Well_Analytics 
            SET required_flow_rate_lps = %s, required_flow_rate_m3h = %s
            WHERE well_id = %s;
        """, (flow_lps, flow_m3h, well_id))

    conn.commit()
    cursor.close()
    conn.close()
    print("💾 Modélisation hydraulique sauvegardée.")

if __name__ == "__main__":
    run_hydraulic_production_pipeline()