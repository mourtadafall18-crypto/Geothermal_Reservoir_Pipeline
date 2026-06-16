import pandas as pd
import numpy as np # Import nécessaire pour gérer inf
import mysql.connector
import os
from dotenv import load_dotenv

def run_import_cleaned_to_mysql():
    print("📥 Ingestion du dataset enrichi avec métadonnées géologiques...")
    load_dotenv()
    
    df_engineered = pd.read_csv('data/engineered_geothermal_data.csv')
    
    # --- AJOUT DU NETTOYAGE ---
    # Remplace les infinis par NaN, puis convertit tout en None (NULL pour MySQL)
    df_engineered = df_engineered.replace([np.inf, -np.inf], np.nan)
    # ---------------------------

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    
    df_geo = pd.read_sql("SELECT well_id, depth_meters, formation_name, fracture_density_per_m, is_fault_zone, dip_angle FROM Well_Logs", conn)
    conn.close()
    
    # Merge
    df_final = pd.merge(df_engineered, df_geo, on=['well_id', 'depth_meters'], how='left')
    
    # Nettoyage final pour MySQL
    df_final = df_final.replace({pd.NA: None, np.nan: None})
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE Well_Logs_Enriched")
        
        # Préparation des données pour mysql-connector (convertir en tuples)
        # On s'assure qu'aucune valeur n'est numpy type, mais du python natif
        data_to_insert = [tuple(None if pd.isna(x) else x for x in row) for row in df_final.to_numpy()]
        
        cols = ",".join(df_final.columns)
        placeholders = ",".join(["%s"] * len(df_final.columns))
        sql = f"INSERT INTO Well_Logs_Enriched ({cols}) VALUES ({placeholders})"
        
        cursor.executemany(sql, data_to_insert)
        conn.commit()
        
        print(f"🚀 Succès : {len(df_final)} lignes insérées.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur lors de l'ingestion : {e}")

if __name__ == "__main__":
    run_import_cleaned_to_mysql()