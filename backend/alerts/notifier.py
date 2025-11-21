"""
Module de notification (email, SMS, etc.).
Pour l'instant, simulation des notifications.
"""
from typing import List
from datetime import datetime


def send_email_notification(to: List[str], subject: str, body: str) -> bool:
    """
    Simule l'envoi d'une notification email.
    
    Args:
        to (List[str]): Liste d'emails destinataires
        subject (str): Sujet
        body (str): Corps du message
        
    Returns:
        bool: Succès de l'envoi
    """
    print(f"\n📧 EMAIL NOTIFICATION")
    print(f"To: {', '.join(to)}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print(f"Sent at: {datetime.utcnow()}\n")
    return True


def send_sms_notification(phone: str, message: str) -> bool:
    """
    Simule l'envoi d'une notification SMS.
    
    Args:
        phone (str): Numéro de téléphone
        message (str): Message
        
    Returns:
        bool: Succès de l'envoi
    """
    print(f"\n📱 SMS NOTIFICATION")
    print(f"To: {phone}")
    print(f"Message: {message}")
    print(f"Sent at: {datetime.utcnow()}\n")
    return True


def notify_alert(alert_type: str, severity: str, message: str, recipients: List[str]) -> bool:
    """
    Envoie une notification pour une alerte.
    
    Args:
        alert_type (str): Type d'alerte
        severity (str): Sévérité
        message (str): Message
        recipients (List[str]): Liste des destinataires
        
    Returns:
        bool: Succès de la notification
    """
    subject = f"[NetPulse-AI] Alerte {severity} - {alert_type}"
    return send_email_notification(recipients, subject, message)
