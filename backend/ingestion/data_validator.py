"""
Validateur de données pour les mesures FH.
Vérifie la conformité des données importées.
"""
import pandas as pd
from typing import Tuple, List, Dict
import config


def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """
    Valide que le DataFrame contient les colonnes requises.
    
    Args:
        df (pd.DataFrame): DataFrame à valider
        
    Returns:
        Tuple[bool, List[str], List[str]]: (Validité, Colonnes manquantes, Colonnes présentes)
    """
    required_columns = config.DATA_VALIDATION['required_columns']
    
    # Normaliser les noms de colonnes pour la comparaison
    df_columns_lower = [col.lower().strip() for col in df.columns]
    required_columns_lower = [col.lower().strip() for col in required_columns]
    
    # Trouver les colonnes manquantes
    missing_columns = [col for col in required_columns_lower if col not in df_columns_lower]
    
    is_valid = len(missing_columns) == 0
    
    return is_valid, missing_columns, df_columns_lower


def validate_data_ranges(df: pd.DataFrame) -> Tuple[bool, Dict[str, List]]:
    """
    Valide que les valeurs sont dans les plages acceptables.
    
    Args:
        df (pd.DataFrame): DataFrame à valider
        
    Returns:
        Tuple[bool, Dict[str, List]]: (Validité globale, Dictionnaire des erreurs par colonne)
    """
    errors = {}
    validation_config = config.DATA_VALIDATION
    
    # Valider RSSI
    if 'rssi_dbm' in df.columns:
        rssi_min, rssi_max = validation_config['rssi_range']
        invalid_rssi = df[(df['rssi_dbm'] < rssi_min) | (df['rssi_dbm'] > rssi_max)]
        if not invalid_rssi.empty:
            errors['rssi_dbm'] = [
                f"{len(invalid_rssi)} valeur(s) hors plage [{rssi_min}, {rssi_max}] dBm"
            ]
    
    # Valider SNR
    if 'snr_db' in df.columns:
        snr_min, snr_max = validation_config['snr_range']
        invalid_snr = df[(df['snr_db'] < snr_min) | (df['snr_db'] > snr_max)]
        if not invalid_snr.empty:
            errors['snr_db'] = [
                f"{len(invalid_snr)} valeur(s) hors plage [{snr_min}, {snr_max}] dB"
            ]
    
    # Valider BER
    if 'ber' in df.columns:
        ber_min, ber_max = validation_config['ber_range']
        invalid_ber = df[(df['ber'] < ber_min) | (df['ber'] > ber_max)]
        if not invalid_ber.empty:
            errors['ber'] = [
                f"{len(invalid_ber)} valeur(s) hors plage [{ber_min}, {ber_max}]"
            ]
    
    # Valider latence
    if 'latency_ms' in df.columns:
        lat_min, lat_max = validation_config['latency_range']
        invalid_latency = df[(df['latency_ms'] < lat_min) | (df['latency_ms'] > lat_max)]
        if not invalid_latency.empty:
            errors['latency_ms'] = [
                f"{len(invalid_latency)} valeur(s) hors plage [{lat_min}, {lat_max}] ms"
            ]
    
    # Valider packet loss
    if 'packet_loss' in df.columns:
        pl_min, pl_max = validation_config['packet_loss_range']
        invalid_pl = df[(df['packet_loss'] < pl_min) | (df['packet_loss'] > pl_max)]
        if not invalid_pl.empty:
            errors['packet_loss'] = [
                f"{len(invalid_pl)} valeur(s) hors plage [{pl_min}, {pl_max}] %"
            ]
    
    # Valider pluie
    if 'rainfall_mm' in df.columns:
        rain_min, rain_max = validation_config['rainfall_range']
        invalid_rain = df[(df['rainfall_mm'] < rain_min) | (df['rainfall_mm'] > rain_max)]
        if not invalid_rain.empty:
            errors['rainfall_mm'] = [
                f"{len(invalid_rain)} valeur(s) hors plage [{rain_min}, {rain_max}] mm"
            ]
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_acm_modulation(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Valide que les modulations ACM sont valides.
    
    Args:
        df (pd.DataFrame): DataFrame à valider
        
    Returns:
        Tuple[bool, List[str]]: (Validité, Liste des modulations invalides)
    """
    if 'acm_modulation' not in df.columns:
        return True, []
    
    valid_modulations = config.ACM_MODULATIONS
    invalid_modulations = df[~df['acm_modulation'].isin(valid_modulations)]['acm_modulation'].unique()
    
    is_valid = len(invalid_modulations) == 0
    return is_valid, invalid_modulations.tolist()


def validate_timestamps(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Valide que les timestamps sont cohérents.
    
    Args:
        df (pd.DataFrame): DataFrame à valider
        
    Returns:
        Tuple[bool, str]: (Validité, Message d'erreur)
    """
    if 'timestamp' not in df.columns:
        return False, "Colonne 'timestamp' manquante"
    
    # Vérifier les valeurs nulles
    null_timestamps = df['timestamp'].isnull().sum()
    if null_timestamps > 0:
        return False, f"{null_timestamps} timestamp(s) manquant(s)"
    
    # Convertir en datetime si nécessaire
    try:
        timestamps = pd.to_datetime(df['timestamp'])
    except Exception as e:
        return False, f"Erreur de conversion des timestamps : {str(e)}"
    
    # Vérifier l'ordre chronologique
    if not timestamps.is_monotonic_increasing:
        return False, "Les timestamps ne sont pas dans l'ordre chronologique"
    
    return True, "Timestamps valides"


def check_missing_values(df: pd.DataFrame) -> Dict[str, int]:
    """
    Compte les valeurs manquantes par colonne.
    
    Args:
        df (pd.DataFrame): DataFrame à analyser
        
    Returns:
        Dict[str, int]: Dictionnaire {colonne: nombre de valeurs manquantes}
    """
    missing = df.isnull().sum()
    return {col: count for col, count in missing.items() if count > 0}


def validate_complete(df: pd.DataFrame) -> Tuple[bool, Dict[str, any]]:
    """
    Effectue une validation complète du DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame à valider
        
    Returns:
        Tuple[bool, Dict]: (Validité globale, Rapport de validation détaillé)
    """
    report = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    # 1. Validation du schéma
    schema_valid, missing_cols, present_cols = validate_schema(df)
    if not schema_valid:
        report['valid'] = False
        report['errors'].append(f"Colonnes manquantes : {', '.join(missing_cols)}")
    
    # 2. Validation des plages de valeurs
    ranges_valid, range_errors = validate_data_ranges(df)
    if not ranges_valid:
        report['warnings'].extend([f"{col}: {msg[0]}" for col, msg in range_errors.items()])
    
    # 3. Validation des modulations ACM
    acm_valid, invalid_mods = validate_acm_modulation(df)
    if not acm_valid:
        report['warnings'].append(f"Modulations invalides : {', '.join(invalid_mods)}")
    
    # 4. Validation des timestamps
    ts_valid, ts_message = validate_timestamps(df)
    if not ts_valid:
        report['errors'].append(ts_message)
        report['valid'] = False
    
    # 5. Vérification des valeurs manquantes
    missing_values = check_missing_values(df)
    if missing_values:
        report['warnings'].append(f"Valeurs manquantes détectées : {missing_values}")
    
    # Informations générales
    report['info'] = {
        'nb_lignes': len(df),
        'nb_colonnes': len(df.columns),
        'colonnes': list(df.columns),
        'periode': {
            'debut': str(df['timestamp'].min()) if 'timestamp' in df.columns else None,
            'fin': str(df['timestamp'].max()) if 'timestamp' in df.columns else None
        }
    }
    
    return report['valid'], report


def get_data_quality_score(df: pd.DataFrame) -> float:
    """
    Calcule un score de qualité des données (0-100).
    
    Args:
        df (pd.DataFrame): DataFrame à évaluer
        
    Returns:
        float: Score de qualité (0-100)
    """
    score = 100.0
    
    # Pénalité pour valeurs manquantes
    missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
    score -= missing_ratio * 30
    
    # Pénalité pour valeurs hors plage
    _, range_errors = validate_data_ranges(df)
    if range_errors:
        score -= len(range_errors) * 5
    
    # Pénalité pour modulations invalides
    acm_valid, invalid_mods = validate_acm_modulation(df)
    if not acm_valid:
        score -= len(invalid_mods) * 3
    
    return max(0, min(100, score))
