import mysql.connector
import pandas as pd
import os
from datetime import datetime
from config import WELL_CONFIGS

def export_reservoir_analytics_report():
    print("🔌 Connexion à la base de données GeoEnergy (Module Export)...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mourtada@123",
        database="GeoEnergy_Exploration"
    )
    
    # Extraction complète
    query = "SELECT * FROM Well_Analytics ORDER BY well_id;"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # 1. Validation automatique
    df['Statut_Analytique'] = df.apply(lambda row: "Validé" if row['well_id'] in WELL_CONFIGS else "À vérifier", axis=1)

    # 2. Mapping complet incluant les nouveaux calculs thermodynamiques et hydrauliques
    rename_mapping = {
        'well_id': 'Puits ID',
        'formation_name': 'Formation Cible',
        'net_pay': 'Net Pay (m)',
        'ntg_percentage': 'NTG (%)',
        'reservoir_temp_celsius': 'Temp. Réservoir (°C)',
        'heat_in_place_pj': 'Heat In Place (PJ)',
        'thermal_power_mwth': 'Puissance (MWth)',
        'required_flow_rate_lps': 'Débit Requis (L/s)',
        'required_flow_rate_m3h': 'Débit Requis (m³/h)',
        'Statut_Analytique': 'Statut Qualité'
    }
    
    # On ne garde que les colonnes utiles
    cols_to_keep = list(rename_mapping.keys())
    df_clean = df[cols_to_keep].rename(columns=rename_mapping)
    
    # Formatage cosmétique
    df_clean['Puits ID'] = df_clean['Puits ID'].apply(lambda x: f"GT-0{x}")

    # 3. Export sécurisé
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)
    
    csv_path = os.path.join(output_folder, f"Rapport_Final_{timestamp}.csv")
    excel_path = os.path.join(output_folder, f"Rapport_Final_{timestamp}.xlsx")

    df_clean.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"✅ Rapport CSV exporté : {csv_path}")

    try:
        df_clean.to_excel(excel_path, index=False, sheet_name="Synthese_Reservoir")
        print(f"✅ Rapport Excel exporté : {excel_path}")
    except ImportError:
        print("⚠️ Module 'openpyxl' manquant pour Excel. (pip install openpyxl)")

    print("\n🎉 Synthèse prête pour la direction technique.")

if __name__ == "__main__":
    export_reservoir_analytics_report()