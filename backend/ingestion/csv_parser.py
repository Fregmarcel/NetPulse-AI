"""
Parser CSV/Excel pour l'import de données de mesures FH.
"""
import pandas as pd
from typing import Tuple, Optional
from pathlib import Path
import config


def parse_csv(file_path: str) -> Tuple[Optional[pd.DataFrame], bool, str]:
    """
    Parse un fichier CSV et retourne un DataFrame.
    
    Args:
        file_path (str): Chemin vers le fichier CSV
        
    Returns:
        Tuple[Optional[pd.DataFrame], bool, str]: (DataFrame, Succès, Message)
    """
    try:
        # Lire le CSV
        df = pd.read_csv(file_path)
        
        # Vérifier que le fichier n'est pas vide
        if df.empty:
            return None, False, "Le fichier CSV est vide"
        
        return df, True, f"CSV parsé avec succès : {len(df)} lignes"
        
    except FileNotFoundError:
        return None, False, f"Fichier non trouvé : {file_path}"
    except pd.errors.EmptyDataError:
        return None, False, "Le fichier CSV est vide"
    except pd.errors.ParserError as e:
        return None, False, f"Erreur de parsing CSV : {str(e)}"
    except Exception as e:
        return None, False, f"Erreur lors de la lecture du CSV : {str(e)}"


def parse_excel(file_path: str, sheet_name: str = 0) -> Tuple[Optional[pd.DataFrame], bool, str]:
    """
    Parse un fichier Excel et retourne un DataFrame.
    
    Args:
        file_path (str): Chemin vers le fichier Excel
        sheet_name (str|int): Nom ou index de la feuille à lire
        
    Returns:
        Tuple[Optional[pd.DataFrame], bool, str]: (DataFrame, Succès, Message)
    """
    try:
        # Lire l'Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        
        # Vérifier que le fichier n'est pas vide
        if df.empty:
            return None, False, "Le fichier Excel est vide"
        
        return df, True, f"Excel parsé avec succès : {len(df)} lignes"
        
    except FileNotFoundError:
        return None, False, f"Fichier non trouvé : {file_path}"
    except ValueError as e:
        return None, False, f"Feuille non trouvée : {str(e)}"
    except Exception as e:
        return None, False, f"Erreur lors de la lecture de l'Excel : {str(e)}"


def parse_uploaded_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], bool, str]:
    """
    Parse un fichier uploadé via Streamlit.
    
    Args:
        uploaded_file: Objet UploadedFile de Streamlit
        
    Returns:
        Tuple[Optional[pd.DataFrame], bool, str]: (DataFrame, Succès, Message)
    """
    try:
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            return None, False, f"Format de fichier non supporté : {file_extension}"
        
        if df.empty:
            return None, False, "Le fichier est vide"
        
        return df, True, f"Fichier '{uploaded_file.name}' parsé avec succès : {len(df)} lignes"
        
    except Exception as e:
        return None, False, f"Erreur lors du parsing du fichier : {str(e)}"


def get_file_info(df: pd.DataFrame) -> dict:
    """
    Retourne des informations sur un DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame à analyser
        
    Returns:
        dict: Dictionnaire contenant les informations
    """
    return {
        'nb_lignes': len(df),
        'nb_colonnes': len(df.columns),
        'colonnes': list(df.columns),
        'types': df.dtypes.to_dict(),
        'memoire_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'nb_valeurs_manquantes': df.isnull().sum().to_dict(),
        'preview': df.head(5).to_dict('records')
    }


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les noms de colonnes (minuscules, sans espaces).
    
    Args:
        df (pd.DataFrame): DataFrame à normaliser
        
    Returns:
        pd.DataFrame: DataFrame avec colonnes normalisées
    """
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    return df


def convert_timestamp_column(df: pd.DataFrame, column_name: str = 'timestamp') -> Tuple[pd.DataFrame, bool, str]:
    """
    Convertit une colonne en datetime.
    
    Args:
        df (pd.DataFrame): DataFrame
        column_name (str): Nom de la colonne timestamp
        
    Returns:
        Tuple[pd.DataFrame, bool, str]: (DataFrame modifié, Succès, Message)
    """
    try:
        if column_name not in df.columns:
            return df, False, f"Colonne '{column_name}' non trouvée"
        
        # Essayer plusieurs formats de date
        df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
        
        # Vérifier les valeurs invalides
        nb_invalid = df[column_name].isnull().sum()
        if nb_invalid > 0:
            return df, False, f"{nb_invalid} timestamp(s) invalide(s) détecté(s)"
        
        return df, True, f"Colonne '{column_name}' convertie en datetime"
        
    except Exception as e:
        return df, False, f"Erreur lors de la conversion : {str(e)}"


def remove_duplicates(df: pd.DataFrame, subset: list = None) -> Tuple[pd.DataFrame, int]:
    """
    Supprime les doublons d'un DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame
        subset (list, optional): Colonnes à considérer pour les doublons
        
    Returns:
        Tuple[pd.DataFrame, int]: (DataFrame sans doublons, Nombre de doublons supprimés)
    """
    initial_count = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep='first')
    nb_duplicates = initial_count - len(df_clean)
    
    return df_clean, nb_duplicates
