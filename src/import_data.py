import os
import pandas as pd
import mysql.connector

def import_geothermal_data():
    print("🔌 Connexion à la base de données GeoEnergy_Exploration...")
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mourtada@123",
        database="GeoEnergy_Exploration"
    )
    cursor = conn.cursor()
    
    # 1. Lecture des fichiers CSV
    df_wells = pd.read_csv('data/synthetic_wells.csv')
    df_logs = pd.read_csv('data/synthetic_logs.csv')
    
    # 2. Nettoyage des données pour éviter les erreurs SQL (NULLs et NaN)
    # Remplacement des valeurs manquantes par 0.0 pour respecter les contraintes de la table
    df_logs['porosity_pct'] = df_logs['porosity_pct'].fillna(0.0)
    df_logs['gamma_ray_api'] = df_logs['gamma_ray_api'].fillna(0.0)
    df_logs['dip_angle'] = df_logs['dip_angle'].fillna(0.0)
    
    # Conversion des types pour garantir l'insertion
    df_logs = df_logs.astype(object) 
    
    try:
        # 3. Ingestion Wells
        print("📥 Insertion des métadonnées des puits...")
        sql_wells = """
            INSERT IGNORE INTO Wells (well_id, well_name, latitude, longitude, total_depth_meters)
            VALUES (%s, %s, %s, %s, %s)
        """
        wells_tuples = [tuple(x) for x in df_wells.values]
        cursor.executemany(sql_wells, wells_tuples)
        
        # 4. Ingestion Well_Logs
        print("📥 Insertion des logs continus v2.0...")
        sql_logs = """
            INSERT INTO Well_Logs (
                well_id, depth_meters, gamma_ray_api, porosity_pct, 
                temperature_celsius, formation_name, fracture_density_per_m, 
                is_fault_zone, dip_angle
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        logs_tuples = [tuple(x) for x in df_logs.values]
        cursor.executemany(sql_logs, logs_tuples)
        
        conn.commit()
        print("✅ Ingestion réussie avec succès dans MySQL !")
        
    except mysql.connector.Error as err:
        print(f"❌ Erreur lors de l'insertion : {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import_geothermal_data()