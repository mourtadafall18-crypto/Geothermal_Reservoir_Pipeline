import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_performance_synthesis():
    print("🔌 Récupération des données agrégées pour la synthèse...")
    conn = mysql.connector.connect(
        host="localhost", user="root", password="mourtada@123", 
        database="GeoEnergy_Exploration"
    )
    
    # Agrégation des données par puits
    # Net Pay estimé si porosité > 8% et Gamma Ray < cut-off
    query = """
        SELECT well_id, 
               COUNT(*) AS gross_thickness_m,
               SUM(CASE WHEN clean_porosity_pct > 8.0 THEN 1 ELSE 0 END) AS net_pay_m,
               AVG(smoothed_temperature_celsius) AS avg_temp,
               AVG(fracture_density_per_m) AS avg_fracture_density
        FROM Well_Logs_Enriched
        GROUP BY well_id;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Calculs dérivés (Potentiel énergétique)
    # Formule simplifiée : Puissance (MW) ~ Débit * DeltaT * Constante
    df['puissance_thermique_mw'] = (df['net_pay_m'] * df['avg_temp'] * 0.05) 
    df['debit_production_req_m3h'] = df['avg_fracture_density'] * 15 # Estimation dynamique

    # Création de la figure double
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    plt.subplots_adjust(hspace=0.4)

    # FIGURE 1 : Géométrie du réservoir
    df.plot(kind='bar', x='well_id', y=['gross_thickness_m', 'net_pay_m'], ax=ax1, color=['#A52A2A', '#FFD700'])
    ax1.set_title("Figure 1 : Géométrie du Réservoir (Gross vs Net Pay)", fontweight='bold')
    ax1.set_ylabel("Épaisseur (m)")
    ax1.legend(["Gross Thickness", "Net Pay"])

    # FIGURE 2 : Potentiel énergétique
    ax2.bar(df['well_id'].astype(str), df['puissance_thermique_mw'], color='red', alpha=0.7, label='Puissance Thermique (MW)')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(df['well_id'].astype(str), df['debit_production_req_m3h'], color='blue', marker='o', lw=2, label='Débit Requis (m3/h)')
    
    ax2.set_title("Figure 2 : Potentiel Énergétique et Dynamique Hydraulique", fontweight='bold')
    ax2.set_ylabel("Puissance (MW)")
    ax2_twin.set_ylabel("Débit Requis (m3/h)", color='blue')
    
    os.makedirs('outputs/plots', exist_ok=True)
    plt.savefig('outputs/plots/synthese_Performances_Puits.png', dpi=300)
    print("✅ Synthèse générée : outputs/plots/synthese_Performances_Puits.png")
    plt.show()

if __name__ == "__main__":
    generate_performance_synthesis()