import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

def plot_professional_well_logs(well_id=2):
    print(f"🔌 Extraction des données ENRICHIES du Puits GT-0{well_id}...")
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mourtada@123",
        database="GeoEnergy_Exploration"
    )
    
    # Lecture depuis Well_Logs_Enriched avec colonnes nettoyées
    query = f"""
        SELECT depth_meters, gamma_ray_api, clean_porosity_pct, 
               smoothed_temperature_celsius, formation_name, fracture_density_per_m, 
               is_fault_zone
        FROM Well_Logs_Enriched
        WHERE well_id = {well_id}
        ORDER BY depth_meters;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Note : Pas besoin d'interpolation, les données sont déjà traitées par scientific_analysis
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 10), sharey=True)
    fig.subplots_adjust(top=0.90, wspace=0.22, bottom=0.20) 
    
    # Palette couleurs
    formation_colors = {
        "Mercia Mudstone Group": "#A52A2A",
        "Sherwood Sandstone Group": "#FFD700",
        "Aylesbeare Mudstone": "#8B4513",
        "Millstone Grit": "#DEB887",
        "Carboniferous Fault Damage Zone": "#FF4500",
        "Carboniferous Limestone Complex": "#708090"
    }
    
    def color_formation_background(ax):
        for form, sub_df in df.groupby('formation_name'):
            top, base = sub_df['depth_meters'].min(), sub_df['depth_meters'].max()
            ax.axhspan(top, base, color=formation_colors.get(form, "#CCCCCC"), alpha=0.3, zorder=0)

    # --- TRACK 1 : GAMMA RAY ---
    color_formation_background(ax1)
    ax1.plot(df['gamma_ray_api'], df['depth_meters'], color='green', lw=1.5)
    ax1.set_xlabel('Gamma Ray (API)', color='green', fontweight='bold')
    ax1.set_xlim(0, 150)
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # --- TRACK 2 : POROSITÉ & FRACTURES ---
    color_formation_background(ax2)
    ax2.plot(df['clean_porosity_pct'], df['depth_meters'], color='blue', lw=1.5) # Utilisation de clean_porosity
    ax2.set_xlabel('Clean Porosity (%)', color='blue', fontweight='bold')
    ax2.set_xlim(0, 30)
    
    ax2_twin = ax2.twiny()
    ax2_twin.plot(df['fracture_density_per_m'], df['depth_meters'], color='purple', lw=1.2, ls='--')
    ax2_twin.set_xlabel('Fracture Density (/m)', color='purple', fontweight='bold')
    ax2_twin.set_xlim(0, 40)
    ax2_twin.spines['bottom'].set_position(('outward', 40))

    # --- TRACK 3 : TEMPÉRATURE ---
    color_formation_background(ax3)
    ax3.plot(df['smoothed_temperature_celsius'], df['depth_meters'], color='red', lw=2) # Utilisation de smoothed_temp
    ax3.set_xlabel('Temp (°C)', color='red', fontweight='bold')
    ax3.set_xlim(10, 150)
    
    # Gestion zones faillées
    fault_df = df[df['is_fault_zone'] == 1]
    if not fault_df.empty:
        f_top, f_base = fault_df['depth_meters'].min(), fault_df['depth_meters'].max()
        ax3.axhspan(f_top, f_base, color='red', alpha=0.2, hatch='//')

    ax1.set_ylabel('Profondeur (Mètres MD)', fontsize=12, fontweight='bold')
    ax1.set_ylim(df['depth_meters'].max(), df['depth_meters'].min()) 
    
    plt.suptitle(f"WELL LOG ANALYSIS - Well: GT-0{well_id} (Enriched Data)", fontsize=12, fontweight='bold')
    
    os.makedirs('output', exist_ok=True)
    plt.savefig(f'output/well_log_GT0{well_id}_enriched.png', dpi=300, bbox_inches='tight')
    print(f"✅ Log enrichi généré : output/well_log_GT0{well_id}_enriched.png")
    plt.show()

if __name__ == "__main__":
    plot_professional_well_logs()