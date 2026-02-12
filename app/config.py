from pathlib import Path
import pandas as pd

# Chemin racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Chemin vers le dataset
DATASET_PATH = BASE_DIR / "data" / "transaction_data.csv"

def connexion_dataset():
    """
    Charge le dataset CSV et retourne un DataFrame pandas.
    """
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Le fichier {DATASET_PATH} est introuvable. "
            "Vérifie que le dossier 'data' et le fichier CSV existent."
        )

    df = pd.read_csv(DATASET_PATH)
    return df


