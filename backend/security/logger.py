"""
Module de logging pour enregistrer les événements système.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


# Configuration du logger
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"netpulse_{datetime.now().strftime('%Y%m%d')}.log"

# Configuration du format de log
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Créer le logger
logger = logging.getLogger('netpulse')
logger.setLevel(logging.DEBUG)

# Handler pour fichier
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Handler pour console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Ajouter les handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_info(message: str, module: Optional[str] = None):
    """
    Enregistre un message d'information.
    
    Args:
        message (str): Message à enregistrer
        module (str, optional): Nom du module source
    """
    if module:
        logger.info(f"[{module}] {message}")
    else:
        logger.info(message)


def log_warning(message: str, module: Optional[str] = None):
    """
    Enregistre un avertissement.
    
    Args:
        message (str): Message à enregistrer
        module (str, optional): Nom du module source
    """
    if module:
        logger.warning(f"[{module}] {message}")
    else:
        logger.warning(message)


def log_error(message: str, exception: Optional[Exception] = None, module: Optional[str] = None):
    """
    Enregistre une erreur.
    
    Args:
        message (str): Message d'erreur
        exception (Exception, optional): Exception associée
        module (str, optional): Nom du module source
    """
    if module:
        prefix = f"[{module}] "
    else:
        prefix = ""
    
    if exception:
        logger.error(f"{prefix}{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"{prefix}{message}")


def log_debug(message: str, module: Optional[str] = None):
    """
    Enregistre un message de debug.
    
    Args:
        message (str): Message à enregistrer
        module (str, optional): Nom du module source
    """
    if module:
        logger.debug(f"[{module}] {message}")
    else:
        logger.debug(message)


def log_critical(message: str, exception: Optional[Exception] = None, module: Optional[str] = None):
    """
    Enregistre une erreur critique.
    
    Args:
        message (str): Message d'erreur
        exception (Exception, optional): Exception associée
        module (str, optional): Nom du module source
    """
    if module:
        prefix = f"[{module}] "
    else:
        prefix = ""
    
    if exception:
        logger.critical(f"{prefix}{message}: {str(exception)}", exc_info=True)
    else:
        logger.critical(f"{prefix}{message}")


def log_user_action(user_email: str, action: str, details: Optional[str] = None):
    """
    Enregistre une action utilisateur.
    
    Args:
        user_email (str): Email de l'utilisateur
        action (str): Action effectuée
        details (str, optional): Détails supplémentaires
    """
    message = f"USER_ACTION - {user_email} - {action}"
    if details:
        message += f" - {details}"
    logger.info(message)


def log_security_event(event_type: str, details: str, severity: str = "INFO"):
    """
    Enregistre un événement de sécurité.
    
    Args:
        event_type (str): Type d'événement (LOGIN_FAILED, UNAUTHORIZED_ACCESS, etc.)
        details (str): Détails de l'événement
        severity (str): Sévérité (INFO, WARNING, ERROR, CRITICAL)
    """
    message = f"SECURITY - {event_type} - {details}"
    
    if severity == "CRITICAL":
        logger.critical(message)
    elif severity == "ERROR":
        logger.error(message)
    elif severity == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)


def log_database_operation(operation: str, table: str, success: bool, details: Optional[str] = None):
    """
    Enregistre une opération de base de données.
    
    Args:
        operation (str): Type d'opération (INSERT, UPDATE, DELETE, SELECT)
        table (str): Table concernée
        success (bool): Succès de l'opération
        details (str, optional): Détails supplémentaires
    """
    status = "SUCCESS" if success else "FAILED"
    message = f"DATABASE - {operation} on {table} - {status}"
    if details:
        message += f" - {details}"
    
    if success:
        logger.debug(message)
    else:
        logger.error(message)


def log_api_call(endpoint: str, method: str, status_code: int, response_time: float):
    """
    Enregistre un appel API.
    
    Args:
        endpoint (str): Point de terminaison appelé
        method (str): Méthode HTTP (GET, POST, etc.)
        status_code (int): Code de statut HTTP
        response_time (float): Temps de réponse en ms
    """
    message = f"API - {method} {endpoint} - {status_code} - {response_time:.2f}ms"
    logger.info(message)


# Fonction pour obtenir le logger
def get_logger(name: str = 'netpulse') -> logging.Logger:
    """
    Retourne le logger configuré.
    
    Args:
        name (str): Nom du logger
        
    Returns:
        logging.Logger: Logger configuré
    """
    return logging.getLogger(name)
