"""
Détecteur d'anomalies basé sur l'analyse statistique.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from backend.database.models import MesureKPI
from backend.database.connection import get_db_context
import config


def detect_anomalies_zscore(link_id: int, metric: str, hours: int = 48, threshold: float = None) -> List[Dict]:
    """
    Détecte les anomalies en utilisant le Z-score.
    
    Args:
        link_id (int): ID de la liaison
        metric (str): Métrique à analyser
        hours (int): Période d'analyse
        threshold (float): Seuil de détection (écarts-types)
        
    Returns:
        List[Dict]: Liste des anomalies détectées
    """
    if threshold is None:
        threshold = config.IA_CONFIG['anomaly_threshold']
    
    with get_db_context() as db:
        date_from = datetime.utcnow() - timedelta(hours=hours)
        
        measures = (
            db.query(MesureKPI)
            .filter(
                MesureKPI.link_id == link_id,
                MesureKPI.timestamp >= date_from
            )
            .order_by(MesureKPI.timestamp)
            .all()
        )
        
        if len(measures) < config.IA_CONFIG['min_data_points']:
            return []
        
        # Extraire les valeurs
        values = [getattr(m, metric) for m in measures]
        timestamps = [m.timestamp for m in measures]
        
        # Calculer moyenne et écart-type
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return []
        
        # Calculer Z-scores
        z_scores = [(v - mean_val) / std_val for v in values]
        
        # Détecter anomalies
        anomalies = []
        for i, z in enumerate(z_scores):
            if abs(z) > threshold:
                anomalies.append({
                    'timestamp': timestamps[i],
                    'value': values[i],
                    'z_score': float(z),
                    'severity': 'HIGH' if abs(z) > threshold + 1 else 'MODERATE'
                })
        
        return anomalies


def detect_sudden_drops(link_id: int, metric: str, hours: int = 24, drop_threshold: float = 10) -> List[Dict]:
    """
    Détecte les chutes brutales de signal.
    
    Args:
        link_id (int): ID de la liaison
        metric (str): Métrique (rssi_dbm, snr_db)
        hours (int): Période d'analyse
        drop_threshold (float): Seuil de chute (unité de la métrique)
        
    Returns:
        List[Dict]: Liste des chutes détectées
    """
    with get_db_context() as db:
        date_from = datetime.utcnow() - timedelta(hours=hours)
        
        measures = (
            db.query(MesureKPI)
            .filter(
                MesureKPI.link_id == link_id,
                MesureKPI.timestamp >= date_from
            )
            .order_by(MesureKPI.timestamp)
            .all()
        )
        
        if len(measures) < 2:
            return []
        
        drops = []
        for i in range(1, len(measures)):
            prev_val = getattr(measures[i-1], metric)
            curr_val = getattr(measures[i], metric)
            drop = prev_val - curr_val
            
            if drop > drop_threshold:
                drops.append({
                    'timestamp': measures[i].timestamp,
                    'previous_value': prev_val,
                    'current_value': curr_val,
                    'drop': float(drop),
                    'severity': 'CRITICAL' if drop > drop_threshold * 2 else 'HIGH'
                })
        
        return drops


def is_anomalous(link_id: int) -> Tuple[bool, str]:
    """
    Détermine si la liaison présente actuellement des anomalies.
    
    Args:
        link_id (int): ID de la liaison
        
    Returns:
        Tuple[bool, str]: (Anomalie détectée, Description)
    """
    # Vérifier RSSI
    rssi_anomalies = detect_anomalies_zscore(link_id, 'rssi_dbm', hours=12)
    if rssi_anomalies:
        return True, f"Anomalie RSSI détectée : {len(rssi_anomalies)} événement(s)"
    
    # Vérifier SNR
    snr_anomalies = detect_anomalies_zscore(link_id, 'snr_db', hours=12)
    if snr_anomalies:
        return True, f"Anomalie SNR détectée : {len(snr_anomalies)} événement(s)"
    
    # Vérifier chutes brutales
    rssi_drops = detect_sudden_drops(link_id, 'rssi_dbm', hours=6, drop_threshold=8)
    if rssi_drops:
        return True, f"Chute brutale de signal détectée"
    
    return False, "Aucune anomalie détectée"
