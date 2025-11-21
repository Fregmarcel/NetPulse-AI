"""
Analyseur de tendances pour identifier les patterns dans les données.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from backend.database.models import MesureKPI
from backend.database.connection import get_db_context


def detect_degradation_trend(link_id: int, metric: str, hours: int = 24) -> Dict:
    """
    Détecte une tendance à la dégradation pour une métrique.
    
    Args:
        link_id (int): ID de la liaison
        metric (str): Métrique à analyser ('rssi_dbm', 'snr_db', etc.)
        hours (int): Période d'analyse en heures
        
    Returns:
        Dict: Résultat de l'analyse
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
        
        if len(measures) < 10:
            return {'trend': 'INSUFFICIENT_DATA', 'slope': 0}
        
        # Extraire les valeurs
        values = [getattr(m, metric) for m in measures]
        timestamps = [(m.timestamp - measures[0].timestamp).total_seconds() for m in measures]
        
        # Calcul de la régression linéaire
        slope, intercept = np.polyfit(timestamps, values, 1)
        
        # Déterminer la tendance
        if metric in ['rssi_dbm', 'snr_db']:
            # Pour RSSI et SNR, une pente négative est mauvaise
            if slope < -0.01:
                trend = 'DEGRADATION'
            elif slope > 0.01:
                trend = 'AMELIORATION'
            else:
                trend = 'STABLE'
        else:
            # Pour BER, latence, etc., une pente positive est mauvaise
            if slope > 0.01:
                trend = 'DEGRADATION'
            elif slope < -0.01:
                trend = 'AMELIORATION'
            else:
                trend = 'STABLE'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'nb_points': len(measures),
            'periode_hours': hours
        }


def analyze_correlation(link_id: int, hours: int = 48) -> Dict:
    """
    Analyse la corrélation entre les métriques et la pluie.
    
    Args:
        link_id (int): ID de la liaison
        hours (int): Période d'analyse
        
    Returns:
        Dict: Corrélations calculées
    """
    with get_db_context() as db:
        date_from = datetime.utcnow() - timedelta(hours=hours)
        
        measures = (
            db.query(MesureKPI)
            .filter(
                MesureKPI.link_id == link_id,
                MesureKPI.timestamp >= date_from
            )
            .all()
        )
        
        if len(measures) < 20:
            return {'status': 'INSUFFICIENT_DATA'}
        
        # Créer DataFrame
        df = pd.DataFrame([{
            'rssi_dbm': m.rssi_dbm,
            'snr_db': m.snr_db,
            'rainfall_mm': m.rainfall_mm
        } for m in measures])
        
        # Calculer corrélations
        corr_rssi_rain = df['rssi_dbm'].corr(df['rainfall_mm'])
        corr_snr_rain = df['snr_db'].corr(df['rainfall_mm'])
        
        return {
            'status': 'OK',
            'rssi_rainfall_corr': float(corr_rssi_rain),
            'snr_rainfall_corr': float(corr_snr_rain),
            'rainfall_impact': 'HIGH' if abs(corr_rssi_rain) > 0.7 else 'MODERATE' if abs(corr_rssi_rain) > 0.4 else 'LOW'
        }


def get_peak_hours(link_id: int, days: int = 7) -> List[int]:
    """
    Identifie les heures de pointe (dégradation maximale).
    
    Args:
        link_id (int): ID de la liaison
        days (int): Nombre de jours à analyser
        
    Returns:
        List[int]: Liste des heures (0-23) de pointe
    """
    with get_db_context() as db:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        measures = (
            db.query(MesureKPI)
            .filter(
                MesureKPI.link_id == link_id,
                MesureKPI.timestamp >= date_from
            )
            .all()
        )
        
        # Grouper par heure
        hourly_rssi = {}
        for m in measures:
            hour = m.timestamp.hour
            if hour not in hourly_rssi:
                hourly_rssi[hour] = []
            hourly_rssi[hour].append(m.rssi_dbm)
        
        # Calculer moyenne par heure
        avg_by_hour = {hour: np.mean(values) for hour, values in hourly_rssi.items()}
        
        # Trouver les 3 pires heures
        worst_hours = sorted(avg_by_hour.items(), key=lambda x: x[1])[:3]
        
        return [hour for hour, _ in worst_hours]
