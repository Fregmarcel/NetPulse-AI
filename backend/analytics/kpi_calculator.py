"""
Calculateur de KPIs pour les liaisons micro-ondes FH.
Calcule les métriques et indicateurs de performance.
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple
from backend.database.models import MesureKPI, FHLink, KPISynthese
from backend.database.connection import get_db_context
import config


def calculate_link_status(rssi: float, snr: float, ber: float) -> str:
    """
    Détermine l'état global d'une liaison selon les seuils ITU/ETSI.
    
    Args:
        rssi (float): RSSI en dBm
        snr (float): SNR en dB
        ber (float): BER
        
    Returns:
        str: État (NORMAL, DEGRADED, CRITIQUE)
    """
    seuils_rssi = config.SEUILS_RSSI
    seuils_snr = config.SEUILS_SNR
    seuils_ber = config.SEUILS_BER
    
    # Évaluation RSSI
    if rssi >= seuils_rssi['BON']:
        rssi_status = 'EXCELLENT'
    elif rssi >= seuils_rssi['ACCEPTABLE']:
        rssi_status = 'BON'
    elif rssi >= seuils_rssi['DEGRADED']:
        rssi_status = 'DEGRADED'
    else:
        rssi_status = 'CRITIQUE'
    
    # Évaluation SNR
    if snr >= seuils_snr['BON']:
        snr_status = 'EXCELLENT'
    elif snr >= seuils_snr['ACCEPTABLE']:
        snr_status = 'BON'
    elif snr >= seuils_snr['DEGRADED']:
        snr_status = 'DEGRADED'
    else:
        snr_status = 'CRITIQUE'
    
    # Évaluation BER
    if ber <= seuils_ber['EXCELLENT']:
        ber_status = 'EXCELLENT'
    elif ber <= seuils_ber['BON']:
        ber_status = 'BON'
    elif ber <= seuils_ber['ACCEPTABLE']:
        ber_status = 'ACCEPTABLE'
    elif ber <= seuils_ber['DEGRADED']:
        ber_status = 'DEGRADED'
    else:
        ber_status = 'CRITIQUE'
    
    # Déterminer l'état global (le pire des trois)
    if 'CRITIQUE' in [rssi_status, snr_status, ber_status]:
        return 'CRITIQUE'
    elif 'DEGRADED' in [rssi_status, snr_status, ber_status]:
        return 'DEGRADED'
    else:
        return 'NORMAL'


def get_latest_kpis(link_id: int) -> Dict:
    """
    Récupère les dernières métriques KPI d'une liaison.
    
    Args:
        link_id (int): ID de la liaison
        
    Returns:
        Dict: Dictionnaire des KPIs ou None si aucune donnée
    """
    with get_db_context() as db:
        latest_measure = (
            db.query(MesureKPI)
            .filter(MesureKPI.link_id == link_id)
            .order_by(MesureKPI.timestamp.desc())
            .first()
        )
        
        if not latest_measure:
            return None
        
        etat = calculate_link_status(
            latest_measure.rssi_dbm,
            latest_measure.snr_db,
            latest_measure.ber
        )
        
        return {
            'timestamp': latest_measure.timestamp,
            'rssi_dbm': latest_measure.rssi_dbm,
            'snr_db': latest_measure.snr_db,
            'ber': latest_measure.ber,
            'acm_modulation': latest_measure.acm_modulation,
            'latency_ms': latest_measure.latency_ms,
            'packet_loss': latest_measure.packet_loss,
            'rainfall_mm': latest_measure.rainfall_mm,
            'etat_global': etat
        }


def calculate_period_statistics(link_id: int, hours: int = 24) -> Dict:
    """
    Calcule les statistiques sur une période donnée.
    
    Args:
        link_id (int): ID de la liaison
        hours (int): Nombre d'heures à analyser
        
    Returns:
        Dict: Statistiques calculées
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
        
        if not measures:
            return None
        
        # Conversion en DataFrame pour faciliter les calculs
        df = pd.DataFrame([{
            'timestamp': m.timestamp,
            'rssi_dbm': m.rssi_dbm,
            'snr_db': m.snr_db,
            'ber': m.ber,
            'latency_ms': m.latency_ms,
            'packet_loss': m.packet_loss,
            'rainfall_mm': m.rainfall_mm
        } for m in measures])
        
        # Calcul des statistiques
        stats = {
            'periode': f"{hours}h",
            'nb_mesures': len(df),
            'rssi': {
                'avg': df['rssi_dbm'].mean(),
                'min': df['rssi_dbm'].min(),
                'max': df['rssi_dbm'].max(),
                'std': df['rssi_dbm'].std()
            },
            'snr': {
                'avg': df['snr_db'].mean(),
                'min': df['snr_db'].min(),
                'max': df['snr_db'].max(),
                'std': df['snr_db'].std()
            },
            'ber': {
                'avg': df['ber'].mean(),
                'min': df['ber'].min(),
                'max': df['ber'].max()
            },
            'latency': {
                'avg': df['latency_ms'].mean(),
                'max': df['latency_ms'].max()
            },
            'packet_loss': {
                'avg': df['packet_loss'].mean(),
                'max': df['packet_loss'].max()
            },
            'rainfall': {
                'avg': df['rainfall_mm'].mean(),
                'max': df['rainfall_mm'].max()
            }
        }
        
        # Calculer la disponibilité (% de temps en état NORMAL)
        normal_count = sum(1 for _, row in df.iterrows() 
                          if calculate_link_status(row['rssi_dbm'], row['snr_db'], row['ber']) == 'NORMAL')
        stats['disponibilite'] = (normal_count / len(df)) * 100
        
        return stats


def calculate_availability(link_id: int, date_from: datetime, date_to: datetime) -> float:
    """
    Calcule le taux de disponibilité d'une liaison sur une période.
    
    Args:
        link_id (int): ID de la liaison
        date_from (datetime): Date de début
        date_to (datetime): Date de fin
        
    Returns:
        float: Taux de disponibilité en %
    """
    with get_db_context() as db:
        measures = (
            db.query(MesureKPI)
            .filter(
                MesureKPI.link_id == link_id,
                MesureKPI.timestamp >= date_from,
                MesureKPI.timestamp <= date_to
            )
            .all()
        )
        
        if not measures:
            return 0.0
        
        # Compter les mesures en état NORMAL
        normal_count = sum(
            1 for m in measures
            if calculate_link_status(m.rssi_dbm, m.snr_db, m.ber) == 'NORMAL'
        )
        
        return (normal_count / len(measures)) * 100


def generate_daily_synthesis(link_id: int, date: datetime) -> Tuple[bool, str]:
    """
    Génère une synthèse KPI journalière et la sauvegarde en DB.
    
    Args:
        link_id (int): ID de la liaison
        date (datetime): Date de la synthèse
        
    Returns:
        Tuple[bool, str]: (Succès, Message)
    """
    try:
        with get_db_context() as db:
            # Récupérer les mesures du jour
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            measures = (
                db.query(MesureKPI)
                .filter(
                    MesureKPI.link_id == link_id,
                    MesureKPI.timestamp >= date_start,
                    MesureKPI.timestamp < date_end
                )
                .all()
            )
            
            if not measures:
                return False, "Aucune mesure pour cette date"
            
            # Calculer les statistiques
            df = pd.DataFrame([{
                'rssi_dbm': m.rssi_dbm,
                'snr_db': m.snr_db,
                'ber': m.ber
            } for m in measures])
            
            # Calculer disponibilité
            normal_count = sum(
                1 for m in measures
                if calculate_link_status(m.rssi_dbm, m.snr_db, m.ber) == 'NORMAL'
            )
            disponibilite = (normal_count / len(measures)) * 100
            
            # Déterminer état global
            if disponibilite >= 99.9:
                etat_global = 'NORMAL'
            elif disponibilite >= 95:
                etat_global = 'DEGRADED'
            else:
                etat_global = 'CRITIQUE'
            
            # Créer ou mettre à jour la synthèse
            synthese = db.query(KPISynthese).filter(
                KPISynthese.link_id == link_id,
                KPISynthese.date == date_start
            ).first()
            
            if synthese:
                # Mise à jour
                synthese.rssi_avg = df['rssi_dbm'].mean()
                synthese.rssi_min = df['rssi_dbm'].min()
                synthese.rssi_max = df['rssi_dbm'].max()
                synthese.snr_avg = df['snr_db'].mean()
                synthese.snr_min = df['snr_db'].min()
                synthese.snr_max = df['snr_db'].max()
                synthese.ber_avg = df['ber'].mean()
                synthese.ber_max = df['ber'].max()
                synthese.disponibilite = disponibilite
                synthese.etat_global = etat_global
                synthese.nb_mesures = len(measures)
            else:
                # Création
                synthese = KPISynthese(
                    link_id=link_id,
                    date=date_start,
                    rssi_avg=df['rssi_dbm'].mean(),
                    rssi_min=df['rssi_dbm'].min(),
                    rssi_max=df['rssi_dbm'].max(),
                    snr_avg=df['snr_db'].mean(),
                    snr_min=df['snr_db'].min(),
                    snr_max=df['snr_db'].max(),
                    ber_avg=df['ber'].mean(),
                    ber_max=df['ber'].max(),
                    disponibilite=disponibilite,
                    etat_global=etat_global,
                    nb_mesures=len(measures)
                )
                db.add(synthese)
            
            db.commit()
            return True, f"Synthèse générée : {len(measures)} mesures, dispo={disponibilite:.2f}%"
            
    except Exception as e:
        return False, f"Erreur : {str(e)}"


def get_kpi_trend(link_id: int, metric: str, days: int = 7) -> pd.DataFrame:
    """
    Récupère la tendance d'une métrique sur plusieurs jours.
    
    Args:
        link_id (int): ID de la liaison
        metric (str): Métrique ('rssi', 'snr', 'ber', 'disponibilite')
        days (int): Nombre de jours
        
    Returns:
        pd.DataFrame: DataFrame avec la tendance
    """
    with get_db_context() as db:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        syntheses = (
            db.query(KPISynthese)
            .filter(
                KPISynthese.link_id == link_id,
                KPISynthese.date >= date_from
            )
            .order_by(KPISynthese.date)
            .all()
        )
        
        data = []
        for s in syntheses:
            row = {'date': s.date}
            if metric == 'rssi':
                row['value'] = s.rssi_avg
            elif metric == 'snr':
                row['value'] = s.snr_avg
            elif metric == 'ber':
                row['value'] = s.ber_avg
            elif metric == 'disponibilite':
                row['value'] = s.disponibilite
            data.append(row)
        
        return pd.DataFrame(data)
