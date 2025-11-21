"""
Configuration globale de l'application NetPulse-AI.
Contient les seuils, paramètres et constantes utilisés dans toute l'application.
"""
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///netpulse.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'netpulse_secret_key_change_in_production_2024')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))

# Configuration de l'application
APP_NAME = "NetPulse-AI"
APP_VERSION = "1.0.0"
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Seuils ITU/ETSI pour les liaisons micro-ondes FH
SEUILS_RSSI = {
    'EXCELLENT': -50,  # dBm
    'BON': -60,
    'ACCEPTABLE': -70,
    'DEGRADED': -75,
    'CRITIQUE': -80
}

SEUILS_SNR = {
    'EXCELLENT': 30,  # dB
    'BON': 20,
    'ACCEPTABLE': 15,
    'DEGRADED': 10,
    'CRITIQUE': 5
}

SEUILS_BER = {
    'EXCELLENT': 1e-9,
    'BON': 1e-7,
    'ACCEPTABLE': 1e-6,
    'DEGRADED': 1e-5,
    'CRITIQUE': 1e-4
}

SEUILS_DISPONIBILITE = {
    'EXCELLENT': 99.999,  # %
    'BON': 99.99,
    'ACCEPTABLE': 99.9,
    'DEGRADED': 99.0,
    'CRITIQUE': 95.0
}

# Configuration de l'IA
IA_CONFIG = {
    'prediction_horizon': 2,  # heures
    'anomaly_threshold': 2.5,  # écarts-types
    'min_data_points': 50,
    'retrain_interval': 24,  # heures
    'confidence_threshold': 0.7
}

# Sévérités des alertes avec couleurs
ALERT_SEVERITIES = {
    'CRITIQUE': {
        'level': 5,
        'color': '#DC143C',  # Rouge crimson
        'icon': '🔴',
        'description': 'Perte de service imminente'
    },
    'MAJEURE': {
        'level': 4,
        'color': '#FF4500',  # Orange rouge
        'icon': '🟠',
        'description': 'Dégradation sévère des performances'
    },
    'MINEURE': {
        'level': 3,
        'color': '#FFA500',  # Orange
        'icon': '🟡',
        'description': 'Dégradation modérée'
    },
    'WARNING': {
        'level': 2,
        'color': '#FFD700',  # Jaune or
        'icon': '⚠️',
        'description': 'Attention requise'
    },
    'INFO': {
        'level': 1,
        'color': '#1E90FF',  # Bleu dodger
        'icon': 'ℹ️',
        'description': 'Information'
    },
    'PREDICTIVE': {
        'level': 3,
        'color': '#9370DB',  # Violet
        'icon': '🔮',
        'description': 'Anomalie prédite par IA'
    },
    'SECURITY': {
        'level': 4,
        'color': '#8B0000',  # Rouge sombre
        'icon': '🔒',
        'description': 'Incident de sécurité'
    }
}

# Types d'alertes
ALERT_TYPES = {
    'RSSI_LOW': 'RSSI faible',
    'SNR_LOW': 'SNR faible',
    'BER_HIGH': 'BER élevé',
    'LINK_DOWN': 'Liaison interrompue',
    'RAINFALL_IMPACT': 'Impact pluie',
    'LATENCY_HIGH': 'Latence élevée',
    'PACKET_LOSS': 'Perte de paquets',
    'ANOMALY_DETECTED': 'Anomalie détectée',
    'PREDICTION_WARNING': 'Alerte prédictive',
    'LOGIN_FAILED': 'Échec authentification',
    'UNAUTHORIZED_ACCESS': 'Accès non autorisé'
}

# Rôles utilisateurs
USER_ROLES = {
    'ADMIN': {
        'level': 3,
        'permissions': ['all']
    },
    'TECH': {
        'level': 2,
        'permissions': ['view', 'resolve_alerts', 'export']
    },
    'GUEST': {
        'level': 1,
        'permissions': ['view']
    }
}

# Configuration des graphiques
CHART_CONFIG = {
    'height': 400,
    'template': 'plotly_white',
    'line_width': 2,
    'marker_size': 6,
    'font_size': 12
}

# Modulations ACM (Adaptive Coding and Modulation)
ACM_MODULATIONS = [
    'QPSK',
    '8PSK',
    '16QAM',
    '32QAM',
    '64QAM',
    '128QAM',
    '256QAM',
    '512QAM',
    '1024QAM'
]

# Configuration du chatbot
CHATBOT_CONFIG = {
    'max_history': 50,
    'response_delay': 0.5,  # secondes
    'suggestions': [
        "Quel est l'état de la liaison ?",
        "Affiche les alertes actives",
        "Donne les métriques actuelles",
        "Quelles sont les recommandations ?",
        "Historique des performances"
    ]
}

# Configuration de l'export
EXPORT_CONFIG = {
    'max_rows': 10000,
    'formats': ['CSV', 'Excel', 'JSON'],
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Configuration de la validation des données
DATA_VALIDATION = {
    'required_columns': [
        'timestamp',
        'link_name',
        'rssi_dbm',
        'snr_db',
        'ber',
        'acm_modulation',
        'latency_ms',
        'packet_loss',
        'rainfall_mm'
    ],
    'rssi_range': (-90, -30),
    'snr_range': (0, 50),
    'ber_range': (1e-12, 1e-3),
    'latency_range': (0, 1000),
    'packet_loss_range': (0, 100),
    'rainfall_range': (0, 200)
}

# Messages système
MESSAGES = {
    'login_success': "✅ Connexion réussie !",
    'login_failed': "❌ Identifiants incorrects",
    'logout': "👋 Déconnexion réussie",
    'access_denied': "🚫 Accès refusé - Permissions insuffisantes",
    'data_saved': "💾 Données sauvegardées avec succès",
    'data_error': "⚠️ Erreur lors du traitement des données",
    'alert_resolved': "✅ Alerte résolue",
    'alert_created': "🚨 Nouvelle alerte créée",
    'import_success': "✅ Import réussi",
    'import_error': "❌ Erreur lors de l'import"
}
