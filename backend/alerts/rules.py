"""
Règles de déclenchement des alertes.
"""
import config


def get_alert_severity_for_rssi(rssi_dbm: float) -> str:
    """Détermine la sévérité d'alerte selon le RSSI."""
    if rssi_dbm < config.SEUILS_RSSI['CRITIQUE']:
        return 'CRITIQUE'
    elif rssi_dbm < config.SEUILS_RSSI['DEGRADED']:
        return 'MAJEURE'
    elif rssi_dbm < config.SEUILS_RSSI['ACCEPTABLE']:
        return 'MINEURE'
    else:
        return 'INFO'


def get_alert_severity_for_snr(snr_db: float) -> str:
    """Détermine la sévérité d'alerte selon le SNR."""
    if snr_db < config.SEUILS_SNR['CRITIQUE']:
        return 'CRITIQUE'
    elif snr_db < config.SEUILS_SNR['DEGRADED']:
        return 'MAJEURE'
    elif snr_db < config.SEUILS_SNR['ACCEPTABLE']:
        return 'MINEURE'
    else:
        return 'INFO'


def should_trigger_alert(metric: str, value: float, threshold: float) -> bool:
    """Détermine si une alerte doit être déclenchée."""
    if metric in ['rssi_dbm', 'snr_db']:
        return value < threshold
    else:
        return value > threshold
