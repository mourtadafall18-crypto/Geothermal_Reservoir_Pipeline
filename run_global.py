# run_global.py à la racine du projet
import sys
import os
import time

# Ajout du dossier src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_step(step_name, func, *args, **kwargs):
    """Exécute une étape du pipeline avec mesure du temps et gestion d'erreurs."""
    print(f"\n▶️ EXÉCUTION : {step_name}...")
    start_time = time.time()
    try:
        func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"✅ {step_name} terminé en {duration:.2f}s")
    except Exception as e:
        print(f"❌ Échec lors de l'étape : {step_name}")
        print(f"   Détail : {e}")
        sys.exit(1)

def main():
    # Importation des modules
    try:
        from generate_data import generate_uk_geothermal_data
        from import_data import import_geothermal_data
        from scientific_analysis import run_scientific_pipeline
        from import_data_cleaned import run_import_cleaned_to_mysql
        from calculate_net_pay import run_multi_well_net_pay_pipeline
        from calculate_heat_in_place import run_geothermal_heat_in_place_pipeline
        from calculate_production_flow import run_hydraulic_production_pipeline
        from export_analytics import export_reservoir_analytics_report
        
        # Modules de visualisation
        from process_and_plot import generate_lithostratigraphic_cross_section
        from plot_well_tracks import plot_professional_well_logs
        from plot_analytics import generate_reservoir_plots
        from plot_synthese_Performance import generate_performance_synthesis
    except ImportError as e:
        print(f"❌ Erreur d'importation : {e}")
        sys.exit(1)

    print("🚀 DÉMARRAGE DU PIPELINE GÉOTHERMIQUE COMPLET")
    print("======================================================")
    
    # 1. Pipeline de Données
    run_step("Génération des données sources", generate_uk_geothermal_data)
    run_step("Ingestion des données brutes", import_geothermal_data)
    run_step("Pipeline scientifique (Nettoyage/Imputation)", run_scientific_pipeline)
    run_step("Importation données enrichies vers MySQL", run_import_cleaned_to_mysql)
    
    # 2. Pipeline Analytique
    run_step("Calculs Net Pay", run_multi_well_net_pay_pipeline)
    run_step("Calculs Heat In Place", run_geothermal_heat_in_place_pipeline)
    run_step("Calculs Dynamique hydraulique", run_hydraulic_production_pipeline)
    run_step("Exportation des rapports analytiques", export_reservoir_analytics_report)
    
    # 3. Pipeline de Visualisation
    print("\n--- GÉNÉRATION DES VISUALISATIONS ---")
    run_step("Coupe lithostratigraphique 2D", generate_lithostratigraphic_cross_section)
    for w in [1, 2, 3]:
        run_step(f"Log détaillé du puits GT-0{w}", plot_professional_well_logs, well_id=w)
    run_step("Profils analytiques complets", generate_reservoir_plots)
    run_step("Synthèse des performances puits", generate_performance_synthesis)
    
    print("\n======================================================")
    print("✅ Pipeline terminé avec succès. Tous les résultats sont dans /outputs")

if __name__ == "__main__":
    main()