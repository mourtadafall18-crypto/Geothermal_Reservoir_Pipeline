import mysql.connector
import pandas as pd
from config import WELL_CONFIGS

def run_multi_well_net_pay_pipeline():
    print("🔌 Connexion à GeoEnergy (Module Net Pay sur données enrichies)...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mourtada@123",
        database="GeoEnergy_Exploration"
    )
    cursor = conn.cursor()

    for well_id, cfg in WELL_CONFIGS.items():
        # ON LIS MAINTENANT 'Well_Logs_Enriched'
        # On n'a plus besoin de filtrer le gamma_ray ou la porosité ici,
        # le SQL et la table enrichie font le travail pour nous.
        query = f"SELECT * FROM Well_Logs_Enriched WHERE well_id = {well_id} ORDER BY depth_meters;"
        df_well = pd.read_sql(query, conn)
        
        if df_well.empty:
            continue

        # 1. Épaisseur brute
        gross_thickness = float(df_well['depth_meters'].max() - df_well['depth_meters'].min())

        # 2. Application des filtres simplifiés
        # La lithologie est déjà classifiée, le calcul est donc immédiat
        condition = (df_well['lithology'] == 'Reservoir (Sandstone)') & \
                    (df_well['clean_porosity_pct'] >= cfg.get('poro_cut', 0.0))

        df_net_pay = df_well[condition]
        net_pay = float(len(df_net_pay))
        
        if net_pay > gross_thickness:
            net_pay = gross_thickness

        ntg = float((net_pay / gross_thickness) * 100.0) if gross_thickness > 0 else 0.0
        
        print(f"   ↳ Puits {cfg['name']} : Net Pay={net_pay:.1f}m | NTG={ntg:.1f}%")

        # 3. Upsert en base (inchangé)
        upsert_query = """
            INSERT INTO Well_Analytics (well_id, formation_name, gross_thickness, net_pay, ntg_percentage, calculated_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                net_pay = VALUES(net_pay),
                ntg_percentage = VALUES(ntg_percentage),
                calculated_at = NOW();
        """
        cursor.execute(upsert_query, (well_id, cfg['form'], gross_thickness, net_pay, ntg))

    conn.commit()
    cursor.close()
    conn.close()
    print("💾 Analyses Net Pay injectées avec succès.\n")
    
if __name__ == "__main__":  
    run_multi_well_net_pay_pipeline()