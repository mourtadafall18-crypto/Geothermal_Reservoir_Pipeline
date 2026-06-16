import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_reservoir_plots():
    print("🔌 Connexion à la base de données (Module Analytics enrichi)...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mourtada@123",
        database="GeoEnergy_Exploration"
    )
    
    output_dir = "outputs/plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Récupération des puits depuis la table enrichie
    query_wells = "SELECT DISTINCT well_id FROM Well_Logs_Enriched;"
    wells = pd.read_sql(query_wells, conn)['well_id'].tolist()
    
    print(f"📈 Génération des profils analytiques pour les {len(wells)} puits...")
    
    for well_id in wells:
        # Extraction des données lissées et propres
        query = f"""
            SELECT depth_meters, gamma_ray_api, clean_porosity_pct, 
                   smoothed_temperature_celsius, fracture_density_per_m 
            FROM Well_Logs_Enriched 
            WHERE well_id = {well_id} 
            ORDER BY depth_meters;
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            continue
            
        fig, axs = plt.subplots(1, 4, figsize=(16, 10), sharey=True)
        fig.suptitle(f"WELL ANALYSIS - GT-0{well_id} (Cleaned Data)", fontsize=14, fontweight='bold', y=0.96)
        
        # Track 1 : Gamma Ray
        axs[0].plot(df['gamma_ray_api'], df['depth_meters'], color='green', lw=1.2)
        axs[0].set_xlabel('Gamma Ray (API)', fontweight='bold')
        axs[0].grid(True, linestyle=':', alpha=0.6)
        
        # Track 2 : Clean Porosity (Données traitées)
        axs[1].plot(df['clean_porosity_pct'], df['depth_meters'], color='blue', lw=1.2)
        axs[1].set_xlabel('Clean Porosity (%)', fontweight='bold')
        axs[1].grid(True, linestyle=':', alpha=0.6)
        
        # Track 3 : Fracture Density
        axs[2].plot(df['fracture_density_per_m'], df['depth_meters'], color='orange', lw=1.2)
        axs[2].set_xlabel('Fracture Density (/m)', fontweight='bold')
        axs[2].grid(True, linestyle=':', alpha=0.6)
            
        # Track 4 : Smoothed Temperature (Gradient lissé)
        axs[3].plot(df['smoothed_temperature_celsius'], df['depth_meters'], color='red', lw=1.5)
        axs[3].set_xlabel('Temp (°C) - Smoothed', fontweight='bold')
        axs[3].grid(True, linestyle=':', alpha=0.6)
        
        # Inversion axe Y pour la norme géologique
        axs[0].set_ylabel('Depth (m)', fontweight='bold')
        axs[0].invert_yaxis()
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.93])
        output_path = f"{output_dir}/Well_GT0{well_id}_Analytics.png"
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"   ↳ Rapport généré : {output_path}")
        
    conn.close()
    print("💾 Rapports analytiques terminés.\n")

if __name__ == "__main__":
    generate_reservoir_plots()