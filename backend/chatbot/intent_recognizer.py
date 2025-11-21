"""
Reconnaissance d'intention pour le chatbot.
"""
import re
from typing import Dict, List


def recognize_intent(user_message: str) -> Dict:
    """
    Reconnaît l'intention de l'utilisateur à partir de son message.
    
    Args:
        user_message (str): Message de l'utilisateur
        
    Returns:
        Dict: {intent: str, confidence: float, entities: dict}
    """
    message_lower = user_message.lower().strip()
    
    # Patterns d'intentions
    intents_patterns = {
        'greeting': [
            r'^(bonjour|hello|salut|hey|hi|bonsoir)',
            r'^(coucou|yo)'
        ],
        'get_status': [
            r'(quel|quoi|comment).*(état|status|statut)',
            r'état.*(liaison|link)',
            r'comment.*(va|aller|marche)',
            r'status'
        ],
        'get_alerts': [
            r'(alerte|alert)',
            r'(problème|incident|erreur)',
            r'quoi.*(ne va pas|problème)'
        ],
        'get_metrics': [
            r'(rssi|snr|ber|latence|signal)',
            r'(métrique|indicateur|kpi)',
            r'valeur.*(rssi|snr)',
            r'(performance|mesure)'
        ],
        'get_recommendations': [
            r'(recommandation|conseil|que faire)',
            r'(action|mesure).*(prendre|faire)',
            r'(corriger|réparer|fix)'
        ],
        'get_history': [
            r'(historique|histoire|passé)',
            r'(hier|avant|précédent)',
            r'(évolution|tendance)'
        ],
        'get_prediction': [
            r'(prédiction|prévoir|futur)',
            r'(va|sera).*(demain|prochain)',
            r'(anticip|estim)'
        ],
        'help': [
            r'^(aide|help|\?)',
            r'(peux|peut).*(faire|aider)',
            r'(comment|quoi).*(utilise|fonctionne)',
            r'qu.?est.?ce.?que.*sais.*faire'
        ]
    }
    
    # Vérifier chaque intention
    for intent, patterns in intents_patterns.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return {
                    'intent': intent,
                    'confidence': 0.85,
                    'entities': extract_entities(message_lower)
                }
    
    # Intention par défaut
    return {
        'intent': 'unknown',
        'confidence': 0.3,
        'entities': {}
    }


def extract_entities(message: str) -> Dict:
    """
    Extrait les entités du message (liaisons, métriques, etc.).
    
    Args:
        message (str): Message à analyser
        
    Returns:
        Dict: Entités extraites
    """
    entities = {}
    
    # Détecter les métriques mentionnées
    metrics = []
    if re.search(r'rssi', message):
        metrics.append('rssi_dbm')
    if re.search(r'snr', message):
        metrics.append('snr_db')
    if re.search(r'ber', message):
        metrics.append('ber')
    if re.search(r'latence', message):
        metrics.append('latency_ms')
    
    if metrics:
        entities['metrics'] = metrics
    
    # Détecter la période temporelle
    if re.search(r'(aujourd\'hui|maintenant|actuellement)', message):
        entities['time_period'] = 'now'
    elif re.search(r'(hier|yesterday)', message):
        entities['time_period'] = 'yesterday'
    elif re.search(r'(semaine|week)', message):
        entities['time_period'] = 'week'
    
    return entities


def get_intent_description(intent: str) -> str:
    """
    Retourne une description de l'intention.
    
    Args:
        intent (str): Code de l'intention
        
    Returns:
        str: Description
    """
    descriptions = {
        'get_status': 'Consulter l\'état de la liaison',
        'get_alerts': 'Consulter les alertes actives',
        'get_metrics': 'Consulter les métriques techniques',
        'get_recommendations': 'Obtenir des recommandations',
        'get_history': 'Consulter l\'historique',
        'get_prediction': 'Obtenir des prédictions',
        'help': 'Obtenir de l\'aide',
        'unknown': 'Intention non reconnue'
    }
    return descriptions.get(intent, 'Inconnu')
