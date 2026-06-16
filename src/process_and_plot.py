import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def generate_lithostratigraphic_cross_section():
    print("🔌 Récupération des données ENRICHIES depuis MySQL...")
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mourtada@123",
        database="GeoEnergy_Exploration"
    )
    
    # Utilisation de Well_Logs_Enriched au lieu de Well_Logs
    query = """
        SELECT well_id, depth_meters, gamma_ray_api, clean_porosity_pct, 
               smoothed_temperature_celsius, formation_name, fracture_density_per_m, 
               is_fault_zone 
        FROM Well_Logs_Enriched
        ORDER BY well_id, depth_meters;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    print("🎨 Génération de la coupe lithostratigraphique 2D (Données Propres)...")
    fig, ax = plt.subplots(figsize=(14, 8))
    
    formation_colors = {
        "Mercia Mudstone Group": "#A52A2A",
        "Sherwood Sandstone Group": "#FFD700",
        "Aylesbeare Mudstone": "#8B4513",
        "Millstone Grit": "#DEB887",
        "Carboniferous Fault Damage Zone": "#FF4500",
        "Carboniferous Limestone Complex": "#708090",
        "Triassic Onlap Sequence": "#E9967A",
        "Variscan Basement (Folded Mudrocks)": "#4B0082"
    }
    
    well_positions = {1: 2.0, 2: 5.0, 3: 8.0}
    well_names = {1: "Well-GT01", 2: "Well-GT02", 3: "Well-GT03"}
    well_width = 0.4
    
    for w_id in [1, 2, 3]:
        df_w = df[df['well_id'] == w_id]
        x_pos = well_positions[w_id]
        
        for _, row in df_w.iterrows():
            depth = row['depth_meters']
            form = row['formation_name']
            color = formation_colors.get(form, "#FFFFFF")
            
            rect = mpatches.Rectangle(
                (x_pos - well_width/2, depth), 
                well_width, 1, 
                linewidth=0, color=color
            )
            ax.add_patch(rect)
            
            if row['is_fault_zone']:
                ax.plot([x_pos - well_width, x_pos + well_width], [depth, depth], color="black", lw=1, ls="--")
        
        ax.text(x_pos, -30, well_names[w_id], ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.plot([x_pos, x_pos], [0, df_w['depth_meters'].max()], color='black', lw=1, zorder=3)

    # Habillage et structure
    ax.set_title("COUPE LITHOLOGIQUE ENRICHIE (Données nettoyées)", fontsize=14, fontweight='bold', pad=30)
    ax.set_ylabel("Profondeur (Mètres)")
    ax.set_ylim(1050, -100)
    ax.set_xlim(0, 10)
    ax.set_xticks([2.0, 5.0, 8.0])
    ax.set_xticklabels(["Puits 1", "Puits 2", "Puits 3"])
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Légende
    legend_patches = [mpatches.Patch(color=color, label=name) for name, color in formation_colors.items()]
    ax.legend(handles=legend_patches, loc='lower left', fontsize=8)
    
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/coupe_litho_enrichie.png', dpi=300)
    print("✅ Coupe mise à jour avec succès : output/coupe_litho_enrichie.png")
    plt.show()

if __name__ == "__main__":
    generate_lithostratigraphic_cross_section()