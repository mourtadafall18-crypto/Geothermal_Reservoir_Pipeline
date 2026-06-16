import os
import numpy as np
import pandas as pd

def generate_uk_geothermal_data():
    print("⏳ Génération du dataset géologique v2.0 (Scénario UK)...")
    np.random.seed(42)  # Pour la reproductibilité
    
    # 1. Création des métadonnées des puits (Wells)
    wells_data = {
        'well_id': [1, 2, 3],
        'well_name': ['Well-GT01', 'Well-GT02', 'Well-GT03'],
        'latitude': [50.909, 54.450, 53.210],   # Coordonnées réalistes UK
        'longitude': [-1.404, -1.900, -2.500],
        'total_depth_meters': [700.0, 1000.0, 500.0]
    }
    df_wells = pd.DataFrame(wells_data)
    
    # 2. Génération des logs continus (Well_Logs)
    logs_list = []
    
    for _, well in df_wells.iterrows():
        w_id = well['well_id']
        w_name = well['well_name']
        max_depth = int(well['total_depth_meters'])
        
        # Température de surface standard au Royaume-Uni (~10°C)
        base_temp = 10.0 
        
        for depth in range(1, max_depth + 1):
            # Valeurs par défaut communes
            fault_zone = False
            fracture_density = np.random.randint(0, 3) # Bruit de fond
            
            # --- CONFIGURATION INDIVIDUELLE DES PUITS (LOIS GÉOLOGIQUES UK) ---
            
            if w_id == 1:
                # SCÉNARIO 1 : Bassin sédimentaire type Wessex (Sherwood Sandstone)
                gradient_base = 0.030 # 30°C/km (Standard)
                current_temp = base_temp + (depth * gradient_base) + np.random.normal(0, 0.2)
                
                if depth < 250:
                    form_name = "Mercia Mudstone Group" # Couverture argileuse
                    gr = np.random.normal(105, 8)
                    poro = np.random.uniform(2, 6)
                    dip = np.random.uniform(2, 5) # Couches quasi horizontales
                elif 250 <= depth <= 550:
                    form_name = "Sherwood Sandstone Group" # Le réservoir cible
                    gr = np.random.normal(45, 6) # Faible radioactivité = sable
                    poro = np.random.uniform(18, 25) # Excellente porosité matrix
                    dip = np.random.uniform(3, 6)
                    # Petit bug de capteur simulé (pannes intermittentes)
                    if np.random.rand() < 0.02: 
                        gr = np.nan
                else:
                    form_name = "Aylesbeare Mudstone" # Base étanche
                    gr = np.random.normal(95, 10)
                    poro = np.random.uniform(4, 8)
                    dip = np.random.uniform(5, 8)

            elif w_id == 2:
                # SCÉNARIO 2 : Zone de Faille Majeure (High-Enthalpy)
                # Gradient constant de 45°C/km pour simuler le flux thermique régional
                gradient_base = 0.045 
                
                # Physique thermique corrigée : monotone et croissante
                # Température = Surface (10°C) + Gradient(depth/1000) + anomalie locale
                temp_lineaire = 10.0 + (depth * gradient_base)
                anomalie = 15.0 if depth >= 600 else 0.0
                current_temp = temp_lineaire + anomalie + np.random.normal(0, 0.2)
                
                # Zone de faille intersectée entre 600m et 680m
                if 600 <= depth <= 680:
                    fault_zone = True
                    form_name = "Carboniferous Fault Damage Zone"
                    gr = np.random.normal(55, 12)
                    poro = np.random.uniform(12, 18)
                    fracture_density = np.random.randint(15, 35)
                    dip = np.random.uniform(45, 75)
                else:
                    # Reste du puits
                    form_name = "Carboniferous Limestone Complex" if depth > 400 else "Millstone Grit"
                    gr = np.random.normal(75, 15)
                    poro = np.random.uniform(6, 12)
                    fracture_density = np.random.randint(1, 6)
                    dip = np.random.uniform(15, 25)
                # Simulation des valeurs aberrantes de porosité (-999.0) dues à des parois rugueuses
                if np.random.rand() < 0.015:
                    poro = -999.0

            elif w_id == 3:
                # SCÉNARIO 3 : Discordance / Onlap Varisque
                gradient_base = 0.028 
                current_temp = base_temp + (depth * gradient_base) + np.random.normal(0, 0.1)
                
                if depth < 320:
                    form_name = "Triassic Onlap Sequence" # Biseautage sédimentaire
                    gr = np.random.normal(58, 7)
                    poro = np.random.uniform(14, 20)
                    dip = np.random.uniform(12, 18) # Inclinaison de dépôt sur la pente
                else:
                    # Passage brutal de la discordance (Unconformity) -> Socle ancien plissé
                    form_name = "Variscan Basement (Folded Mudrocks)"
                    gr = np.random.normal(120, 10) # Très argileux/métamorphique
                    poro = np.random.uniform(1, 4)   # Porosité matrice détruite
                    dip = np.random.uniform(60, 85)  # Séries quasi verticales (plissement intense)
                    fracture_density = np.random.randint(2, 8)

            logs_list.append({
                'well_id': w_id,
                'depth_meters': float(depth),
                'gamma_ray_api': gr,
                'porosity_pct': poro,
                'temperature_celsius': current_temp,
                'formation_name': form_name,
                'fracture_density_per_m': fracture_density,
                'is_fault_zone': int(fault_zone),
                'dip_angle': dip
            })

    df_logs = pd.DataFrame(logs_list)
    
    # Exportation des fichiers CSV
    os.makedirs('data', exist_ok=True)
    df_wells.to_csv('data/synthetic_wells.csv', index=False)
    df_logs.to_csv('data/synthetic_logs.csv', index=False)
    print("✅ Fichiers v2.0 'synthetic_wells.csv' et 'synthetic_logs.csv' générés avec succès dans /data !")

if __name__ == "__main__":
    generate_uk_geothermal_data()