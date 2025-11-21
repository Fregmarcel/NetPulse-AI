"""
Module pour expliquer les prédictions et anomalies de l'IA.
"""
from typing import Dict, List


def explain_anomaly(metric: str, value: float, z_score: float) -> str:
    """
    Génère une explication textuelle pour une anomalie.
    
    Args:
        metric (str): Métrique concernée
        value (float): Valeur anormale
        z_score (float): Z-score de l'anomalie
        
    Returns:
        str: Explication textuelle
    """
    severity = "extrême" if abs(z_score) > 4 else "significative" if abs(z_score) > 3 else "modérée"
    
    metric_names = {
        'rssi_dbm': 'RSSI',
        'snr_db': 'SNR',
        'ber': 'BER',
        'latency_ms': 'latence',
        'packet_loss': 'perte de paquets'
    }
    
    name = metric_names.get(metric, metric)
    
    if metric in ['rssi_dbm', 'snr_db']:
        direction = "anormalement faible" if z_score < 0 else "anormalement élevée"
    else:
        direction = "anormalement élevée" if z_score > 0 else "anormalement faible"
    
    explanation = f"Une valeur {severity} de {name} a été détectée ({value:.2f}), "
    explanation += f"qui est {direction} par rapport à la normale (Z-score: {z_score:.2f}). "
    
    if abs(z_score) > 4:
        explanation += "Ceci nécessite une attention immédiate."
    elif abs(z_score) > 3:
        explanation += "Une investigation est recommandée."
    else:
        explanation += "À surveiller."
    
    return explanation


def get_recommendation(metric: str, current_value: float, predicted_value: float) -> List[str]:
    """
    Génère des recommandations basées sur les prédictions.
    
    Args:
        metric (str): Métrique analysée
        current_value (float): Valeur actuelle
        predicted_value (float): Valeur prédite
        
    Returns:
        List[str]: Liste de recommandations
    """
    recommendations = []
    
    if metric == 'rssi_dbm':
        if predicted_value < -70:
            recommendations.append("⚠️ Vérifier l'alignement des antennes")
            recommendations.append("🔍 Inspecter les câbles et connecteurs")
            recommendations.append("📡 Vérifier les conditions météorologiques")
        elif predicted_value < -65:
            recommendations.append("👁️ Surveillance accrue recommandée")
            recommendations.append("📊 Planifier une maintenance préventive")
    
    elif metric == 'snr_db':
        if predicted_value < 15:
            recommendations.append("📶 Réduire les sources d'interférence")
            recommendations.append("🔧 Vérifier la configuration des filtres")
            recommendations.append("⚡ Vérifier l'alimentation électrique")
    
    if not recommendations:
        recommendations.append("✅ Aucune action immédiate requise")
        recommendations.append("📈 Continuer la surveillance normale")
    
    return recommendations


def explain_prediction(prediction_result: Dict) -> str:
    """
    Explique un résultat de prédiction.
    
    Args:
        prediction_result (Dict): Résultat de la prédiction
        
    Returns:
        str: Explication textuelle
    """
    if prediction_result['status'] != 'OK':
        return "Données insuffisantes pour effectuer une prédiction fiable."
    
    metric = prediction_result['metric']
    current = prediction_result['current_value']
    predicted = prediction_result['predictions'][-1]
    confidence = prediction_result['confidence']
    
    explanation = f"**Analyse prédictive pour {metric}:**\n\n"
    explanation += f"• Valeur actuelle : {current:.2f}\n"
    explanation += f"• Valeur prédite : {predicted:.2f}\n"
    explanation += f"• Confiance du modèle : {confidence*100:.1f}%\n\n"
    
    if confidence < 0.5:
        explanation += "⚠️ La confiance du modèle est faible. Les données présentent une forte variabilité.\n\n"
    
    trend = prediction_result.get('trend', 'UNKNOWN')
    if trend == 'DEGRADING':
        explanation += "📉 **Tendance :** Dégradation attendue\n\n"
    elif trend == 'STABLE':
        explanation += "📊 **Tendance :** Stable\n\n"
    
    recommendations = get_recommendation(metric, current, predicted)
    explanation += "**Recommandations :**\n"
    for rec in recommendations:
        explanation += f"- {rec}\n"
    
    return explanation
