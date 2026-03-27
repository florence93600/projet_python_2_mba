import pandas as pd
import pathlib
import json
import os
from tqdm import tqdm
from fastapi import HTTPException

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
CACHE_FILE = DATA_DIR / "full_dataset_turbo.parquet"

_df: pd.DataFrame | None = None

def get_df() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = connexion_dataset()
    return _df

def reset_df() -> None:
   
    global _df
    _df = None

def connexion_dataset() -> pd.DataFrame:

    if CACHE_FILE.exists():
        print("Chargement des données depuis le cache…")
        try:
            return pd.read_parquet(CACHE_FILE)
        except Exception:
            print("Cache corrompu, reconstruction…")

    print("Fusion des fichiers sources…")
    try:
        path_tx     = DATA_DIR / "transactions_data.csv"
        path_users  = DATA_DIR / "users_data.csv"
        path_cards  = DATA_DIR / "cards_data.csv"
        path_mcc    = DATA_DIR / "mcc_codes.json"
        path_labels = DATA_DIR / "train_fraud_labels.json"

        with tqdm(total=5, desc="Lecture des sources") as pbar:

            df_trans = pd.read_csv(path_tx, low_memory=False)
            pbar.update(1)

            df_users = pd.read_csv(path_users)
            pbar.update(1)

            df_cards = pd.read_csv(path_cards)
            pbar.update(1)

            with open(path_mcc, "r", encoding="utf-8") as f:
                mcc_dict = json.load(f)
            pbar.update(1)

           
            fraud_json = _load_json_safe(path_labels)
            pbar.update(1)

        print("Nettoyage et jointures…")

        df_trans.columns = df_trans.columns.str.strip()
        df_trans["amount"] = (
            df_trans["amount"]
            .astype(str)
            .str.replace(r"[^\d.-]", "", regex=True)
            .astype(float)
        )

        fraud_df = pd.DataFrame.from_dict(
            fraud_json["target"], orient="index", columns=["is_fraud_str"]
        )
        fraud_df.index = fraud_df.index.astype(int)
        fraud_df["is_fraud"] = (fraud_df["is_fraud_str"] == "Yes").astype(int)

        df_merged = df_trans.merge(
            fraud_df[["is_fraud"]], left_on="id", right_index=True, how="left"
        )
        df_merged["is_fraud"] = df_merged["is_fraud"].fillna(0).astype(int)

        df_users.columns = df_users.columns.str.strip()
        df_merged = df_merged.merge(
            df_users,
            left_on="client_id",
            right_on="id",
            how="left",
            suffixes=("", "_user"),
        )

        df_cards.columns = df_cards.columns.str.strip()
        df_merged = df_merged.merge(
            df_cards,
            left_on=["client_id", "card_id"],
            right_on=["client_id", "id"],
            how="left",
            suffixes=("", "_card"),
        )

        df_merged["mcc_description"] = df_merged["mcc"].astype(str).map(mcc_dict)

        cols_to_drop = ["id_user", "id_card", "id_y"]
        df_merged = df_merged.drop(
            columns=[c for c in cols_to_drop if c in df_merged.columns]
        )

        print(f"Sauvegarde du cache : {CACHE_FILE.name}")
        df_merged.to_parquet(CACHE_FILE, index=False)

        print(f"Terminé : {len(df_merged)} transactions prêtes.")
        return df_merged

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur : {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _load_json_safe(path: pathlib.Path) -> dict:

    raw = path.read_text(encoding="utf-8")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(raw.lstrip())
        print(
            f"[config] Avertissement : '{path.name}' contient des données "
            "supplémentaires après le premier objet JSON — seul le premier "
            "objet a été chargé."
        )
        return obj
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Impossible de lire {path.name} : {e}",
        )
        
def get_sample_df(n: int = 100) -> pd.DataFrame:
    
    df = connexion_dataset()
    return df.head(n)        
