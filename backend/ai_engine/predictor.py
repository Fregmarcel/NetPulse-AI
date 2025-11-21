"""
Module de prédiction pour anticiper les dégradations.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from sklearn.linear_model import LinearRegression
from backend.database.models import MesureKPI
from backend.database.connection import get_db_context
import config


def predict_next_values(link_id: int, metric: str, hours_ahead: int = None) -> Dict:
    """
    Prédit les valeurs futures d'une métrique.
    
    Args:
        link_id (int): ID de la liaison
        metric (str): Métrique à prédire
        hours_ahead (int): Horizon de prédiction
        
    Returns:
        Dict: Prédictions et statistiques
    """
    if hours_ahead is None:
        hours_ahead = config.IA_CONFIG['prediction_horizon']
    
    with get_db_context() as db:
        # Récupérer les mesures des dernières 48h
        date_from = datetime.utcnow() - timedelta(hours=48)
        
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
            return {'status': 'INSUFFICIENT_DATA'}
        
        # Préparer les données
        timestamps = [(m.timestamp - measures[0].timestamp).total_seconds() / 3600 for m in measures]
        values = [getattr(m, metric) for m in measures]
        
        X = np.array(timestamps).reshape(-1, 1)
        y = np.array(values)
        
        # Entraîner le modèle
        model = LinearRegression()
        model.fit(X, y)
        
        # Prédire
        last_timestamp = timestamps[-1]
        future_timestamps = [last_timestamp + i for i in range(1, hours_ahead + 1)]
        X_future = np.array(future_timestamps).reshape(-1, 1)
        predictions = model.predict(X_future)
        
        # Calculer la confiance
        score = model.score(X, y)
        
        return {
            'status': 'OK',
            'metric': metric,
            'current_value': values[-1],
            'predictions': [float(p) for p in predictions],
            'timestamps': [measures[0].timestamp + timedelta(hours=t) for t in future_timestamps],
            'confidence': float(score),
            'trend': 'DEGRADING' if predictions[-1] < values[-1] - 2 else 'STABLE'
        }


def predict_degradation_risk(link_id: int) -> Dict:
    """
    Évalue le risque de dégradation dans les prochaines heures.
    
    Args:
        link_id (int): ID de la liaison
        
    Returns:
        Dict: Évaluation du risque
    """
    # Prédire RSSI
    rssi_pred = predict_next_values(link_id, 'rssi_dbm', hours_ahead=2)
    if rssi_pred['status'] != 'OK':
        return {'risk_level': 'UNKNOWN', 'reason': 'Données insuffisantes'}
    
    # Vérifier si le RSSI prédit descend sous le seuil critique
    rssi_threshold = config.SEUILS_RSSI['DEGRADED']
    future_rssi = rssi_pred['predictions'][-1]
    
    if future_rssi < rssi_threshold:
        return {
            'risk_level': 'HIGH',
            'reason': f"RSSI prédit ({future_rssi:.1f} dBm) sous le seuil de dégradation",
            'estimated_time': rssi_pred['timestamps'][-1],
            'confidence': rssi_pred['confidence']
        }
    elif future_rssi < rssi_threshold + 5:
        return {
            'risk_level': 'MODERATE',
            'reason': f"RSSI prédit ({future_rssi:.1f} dBm) proche du seuil",
            'estimated_time': rssi_pred['timestamps'][-1],
            'confidence': rssi_pred['confidence']
        }
    else:
        return {
            'risk_level': 'LOW',
            'reason': f"RSSI prédit stable ({future_rssi:.1f} dBm)",
            'confidence': rssi_pred['confidence']
        }
