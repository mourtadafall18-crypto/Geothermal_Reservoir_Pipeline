import os
import mysql.connector
import pandas as pd
import numpy as np
from dotenv import load_dotenv

def run_scientific_pipeline():
    print("🔌 Connexion à MySQL pour extraction de la Vue Nettoyée...")
    load_dotenv()
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        
        # 1. Extraction des données de la VUE via Pandas
        query = "SELECT * FROM v_clean_well_logs ORDER BY well_id, depth_meters;"
        df = pd.read_sql(query, conn)
        print(f"✅ Données extraites avec succès : {df.shape[0]} lignes chargées.")
        
        # 2. IMPUTATION DES MANQUES (Gamma Ray)
        # On interpole puits par puits pour ne pas mélanger les géologies
        print("🧪 Imputation par interpolation linéaire des pannes du Gamma Ray...")
        df['gamma_ray_api'] = df.groupby('well_id')['gamma_ray_api'].transform(lambda x: x.interpolate(method='linear'))
        
        # 3. FEATURE ENGINEERING : Classification de la Lithologie
        # Seuil géologique standard : < 65 API = Réservoir (Sable/Grès), >= 65 = Couverture (Argile/Shale)
        print("🪨 Classification automatisée de la lithologie (Seuil: 65 API)...")
        df['lithology'] = np.where(df['gamma_ray_api'] < 65, 'Reservoir (Sandstone)', 'Caprock (Clay/Shale)')
        
        # 4. FEATURE ENGINEERING : Calcul du Gradient Géothermique Local (°C/km)
        # Calcul de la différence de température par rapport au pas précédent (1 mètre)
        print("🔥 Calcul du gradient géothermique localisé...")
        df['temp_diff'] = df.groupby('well_id')['smoothed_temperature_celsius'].diff()
        df['depth_diff'] = df.groupby('well_id')['depth_meters'].diff()
        
        # Gradient en °C/km = (dT / dz) * 1000
        df['geothermal_gradient_c_per_km'] = (df['temp_diff'] / df['depth_diff']) * 1000
        
        # Remplacement de la première ligne de chaque puits (qui devient NaN après le diff) par la moyenne
        df['geothermal_gradient_c_per_km'] = df['geothermal_gradient_c_per_km'].bfill()
        
        # 5. SYNTHÈSE POUR LE RAPPORT GÉOLOGIQUE
        print("\n=======================================================")
        print("📊 RAPPORT SYNTHÉTIQUE D'EXPLORATION GÉOTHERMIQUE")
        print("=======================================================")
        
        summary = df.groupby('well_name').agg(
            Profondeur_Max=('depth_meters', 'max'),
            Temp_Max=('smoothed_temperature_celsius', 'max'),
            Porosite_Moyenne=('clean_porosity_pct', 'mean'),
            Epaisseur_Reservoir_Metres=('lithology', lambda x: (x == 'Reservoir (Sandstone)').sum()),
            Gradient_Moyen_C_km=('geothermal_gradient_c_per_km', 'mean')
        ).reset_index()
        
        print(summary.to_string(index=False))
        print("=======================================================")
        
        # Sauvegarde du dataset enrichi pour la phase de dataviz
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/engineered_geothermal_data.csv', index=False)
        print("\n💾 Dataset enrichi sauvegardé dans 'data/engineered_geothermal_data.csv'.")

    except mysql.connector.Error as err:
        print(f"❌ Erreur : {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("🔒 Connexion MySQL refermée.")

if __name__ == "__main__":
    run_scientific_pipeline()