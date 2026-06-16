# src/config.py
# Centralisation des seuils pour garantir l'unicité des résultats
WELL_CONFIGS = {
    1: {
        "name": "GT-01", "form": "Sherwood Sandstone",
        "gamma_cut": 65.0, "poro_cut": 8.0, "fract_cut": 0.0,
        "rho_r": 2600.0, "c_r": 850.0, "phi": 0.12  # Propriétés Grès
    },
    2: {
        "name": "GT-02", "form": "Carboniferous Fault",
        "gamma_cut": 70.0, "poro_cut": 0.0, "fract_cut": 12.0,
        "rho_r": 2700.0, "c_r": 900.0, "phi": 0.084 # Propriétés Calcaire
    },
    3: {
        "name": "GT-03", "form": "Onlap Trias / Socle",
        "gamma_cut": 65.0, "poro_cut": 5.0, "fract_cut": 5.0,
        "rho_r": 2650.0, "c_r": 880.0, "phi": 0.05  # Propriétés Socle
    }
}
# Constantes physiques
T_REF_USINE = 40.0 # Température de base pour le calcul de puissance

