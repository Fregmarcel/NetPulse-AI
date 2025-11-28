"""
Moteur de génération et gestion des alertes.
"""
from datetime import datetime
from typing import List, Dict, Tuple
from backend.database.models import Alerte, MesureKPI, FHLink
from backend.database.connection import get_db_context
from backend.analytics.kpi_calculator import calculate_link_status, get_latest_kpis
from backend.ai_engine.anomaly_detector import is_anomalous
import config


def create_alert(
    link_id: int,
    alert_type: str,
    severite: str,
    message: str,
    recommandation: str = None,
    valeur_mesuree: float = None,
    seuil_declenche: float = None,
    ia_generated: bool = False
) -> Tuple[bool, int]:
    """
    Crée une nouvelle alerte dans la base de données.
    Évite les doublons d'alertes actives du même type.
    
    Args:
        link_id (int): ID de la liaison
        alert_type (str): Type d'alerte
        severite (str): Sévérité (CRITIQUE, MAJEURE, etc.)
        message (str): Message descriptif
        recommandation (str): Recommandations
        valeur_mesuree (float): Valeur qui a déclenché l'alerte
        seuil_declenche (float): Seuil dépassé
        ia_generated (bool): Alerte générée par l'IA
        
    Returns:
        Tuple[bool, int]: (Succès, ID de l'alerte)
    """
    try:
        with get_db_context() as db:
            # Vérifier si une alerte similaire existe déjà (même type, même liaison, non résolue)
            existing_alert = db.query(Alerte).filter(
                Alerte.link_id == link_id,
                Alerte.type == alert_type,
                Alerte.resolved == False
            ).first()
            
            # Si une alerte similaire existe déjà, ne pas créer de doublon
            if existing_alert:
                print(f"Alerte {alert_type} déjà active pour liaison {link_id}")
                return False, 0
            
            # Créer la nouvelle alerte
            alerte = Alerte(
                link_id=link_id,
                timestamp=datetime.utcnow(),
                type=alert_type,
                severite=severite,
                message=message,
                recommandation=recommandation,
                resolved=False,
                valeur_mesuree=valeur_mesuree,
                seuil_declenche=seuil_declenche,
                ia_generated=ia_generated
            )
            
            db.add(alerte)
            db.commit()
            db.refresh(alerte)
            
            print(f"✓ Alerte créée : {alert_type} [{severite}] pour liaison {link_id}")
            return True, alerte.id
            
    except Exception as e:
        print(f"Erreur création alerte : {e}")
        return False, 0


def check_and_create_alerts(link_id: int) -> List[int]:
    """
    Vérifie les métriques et crée des alertes si nécessaire.
    Analyse les dernières mesures pour détecter les problèmes.
    
    Args:
        link_id (int): ID de la liaison
        
    Returns:
        List[int]: Liste des IDs des alertes créées
    """
    created_alerts = []
    
    # Récupérer les dernières métriques
    kpis = get_latest_kpis(link_id)
    if not kpis:
        print(f"⚠️ Aucune métrique disponible pour liaison {link_id}")
        return created_alerts
    
    print(f"\n🔍 Vérification alertes pour liaison {link_id}")
    print(f"   RSSI: {kpis['rssi_dbm']:.1f} dBm | SNR: {kpis['snr_db']:.1f} dB | BER: {kpis['ber']:.2e}")
    
    # Vérifier RSSI
    if kpis['rssi_dbm'] < config.SEUILS_RSSI['CRITIQUE']:
        print(f"   → RSSI critique détecté ({kpis['rssi_dbm']:.1f} < {config.SEUILS_RSSI['CRITIQUE']})")
        success, alert_id = create_alert(
            link_id=link_id,
            alert_type='RSSI_LOW',
            severite='CRITIQUE',
            message=f"RSSI critique : {kpis['rssi_dbm']:.1f} dBm",
            recommandation="Vérifier immédiatement l'alignement des antennes et les conditions météo",
            valeur_mesuree=kpis['rssi_dbm'],
            seuil_declenche=config.SEUILS_RSSI['CRITIQUE']
        )
        if success:
            created_alerts.append(alert_id)
    
    elif kpis['rssi_dbm'] < config.SEUILS_RSSI['DEGRADED']:
        print(f"   → RSSI dégradé détecté ({kpis['rssi_dbm']:.1f} < {config.SEUILS_RSSI['DEGRADED']})")
        success, alert_id = create_alert(
            link_id=link_id,
            alert_type='RSSI_LOW',
            severite='MAJEURE',
            message=f"RSSI dégradé : {kpis['rssi_dbm']:.1f} dBm",
            recommandation="Surveillance accrue recommandée, planifier une inspection",
            valeur_mesuree=kpis['rssi_dbm'],
            seuil_declenche=config.SEUILS_RSSI['DEGRADED']
        )
        if success:
            created_alerts.append(alert_id)
    
    # Vérifier SNR
    if kpis['snr_db'] < config.SEUILS_SNR['CRITIQUE']:
        success, alert_id = create_alert(
            link_id=link_id,
            alert_type='SNR_LOW',
            severite='CRITIQUE',
            message=f"SNR critique : {kpis['snr_db']:.1f} dB",
            recommandation="Réduire les sources d'interférence, vérifier la configuration",
            valeur_mesuree=kpis['snr_db'],
            seuil_declenche=config.SEUILS_SNR['CRITIQUE']
        )
        if success:
            created_alerts.append(alert_id)
    
    elif kpis['snr_db'] < config.SEUILS_SNR['DEGRADED']:
        success, alert_id = create_alert(
            link_id=link_id,
            alert_type='SNR_LOW',
            severite='MAJEURE',
            message=f"SNR dégradé : {kpis['snr_db']:.1f} dB",
            recommandation="Surveiller l'évolution, identifier les sources d'interférence",
            valeur_mesuree=kpis['snr_db'],
            seuil_declenche=config.SEUILS_SNR['DEGRADED']
        )
        if success:
            created_alerts.append(alert_id)
    
    # Vérifier impact pluie
    if kpis['rainfall_mm'] > 15 and kpis['rssi_dbm'] < config.SEUILS_RSSI['ACCEPTABLE']:
        success, alert_id = create_alert(
            link_id=link_id,
            alert_type='RAINFALL_IMPACT',
            severite='MAJEURE',
            message=f"Impact pluie détecté : {kpis['rainfall_mm']:.1f} mm, RSSI={kpis['rssi_dbm']:.1f} dBm",
            recommandation="Atténuation due à la pluie, surveillance renforcée jusqu'à amélioration météo",
            valeur_mesuree=kpis['rainfall_mm'],
            seuil_declenche=15
        )
        if success:
            created_alerts.append(alert_id)
    
    # Vérifier anomalies IA
    anomaly_detected, anomaly_msg = is_anomalous(link_id)
    if anomaly_detected:
        success, alert_id = create_alert(
            link_id=link_id,
            alert_type='ANOMALY_DETECTED',
            severite='PREDICTIVE',
            message=f"Anomalie détectée par l'IA : {anomaly_msg}",
            recommandation="Analyser les métriques détaillées et les tendances",
            ia_generated=True
        )
        if success:
            created_alerts.append(alert_id)
    
    return created_alerts


def resolve_alert(alert_id: int, resolved_by: str) -> Tuple[bool, str]:
    """
    Marque une alerte comme résolue.
    
    Args:
        alert_id (int): ID de l'alerte
        resolved_by (str): Email de l'utilisateur qui résout
        
    Returns:
        Tuple[bool, str]: (Succès, Message)
    """
    try:
        with get_db_context() as db:
            alerte = db.query(Alerte).filter(Alerte.id == alert_id).first()
            
            if not alerte:
                return False, "Alerte non trouvée"
            
            if alerte.resolved:
                return False, "Alerte déjà résolue"
            
            alerte.resolved = True
            alerte.resolved_at = datetime.utcnow()
            alerte.resolved_by = resolved_by
            
            db.commit()
            
            return True, "Alerte résolue avec succès"
            
    except Exception as e:
        return False, f"Erreur : {str(e)}"


def get_active_alerts(link_id: int = None) -> List[Dict]:
    """
    Récupère les alertes actives sous forme de dictionnaires.
    
    Args:
        link_id (int, optional): Filtrer par liaison
        
    Returns:
        List[Dict]: Liste des alertes actives
    """
    with get_db_context() as db:
        query = db.query(Alerte).filter(Alerte.resolved == False)
        
        if link_id:
            query = query.filter(Alerte.link_id == link_id)
        
        alerts = query.order_by(Alerte.timestamp.desc()).all()
        
        # Convertir en dictionnaires DANS le contexte de la session
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'link_id': alert.link_id,
                'timestamp': alert.timestamp,
                'type': alert.type,
                'severite': alert.severite,
                'message': alert.message,
                'recommandation': alert.recommandation,
                'resolved': alert.resolved,
                'valeur_mesuree': alert.valeur_mesuree,
                'seuil_declenche': alert.seuil_declenche,
                'ia_generated': alert.ia_generated,
                'resolved_at': alert.resolved_at if hasattr(alert, 'resolved_at') else None,
                'resolved_by': alert.resolved_by if hasattr(alert, 'resolved_by') else None
            })
        
        return alerts_data


def get_alerts_count_by_severity(link_id: int = None) -> Dict:
    """
    Compte les alertes actives par sévérité.
    
    Args:
        link_id (int, optional): Filtrer par liaison
        
    Returns:
        Dict: Dictionnaire {sévérité: compte}
    """
    with get_db_context() as db:
        query = db.query(Alerte).filter(Alerte.resolved == False)
        
        if link_id:
            query = query.filter(Alerte.link_id == link_id)
        
        alerts = query.all()
        
        # Extraire les sévérités DANS le contexte de la session
        severities = [a.severite for a in alerts]
        
        counts = {}
        for severity in config.ALERT_SEVERITIES.keys():
            counts[severity] = severities.count(severity)
        
        return counts


def delete_alert(alert_id: int) -> Tuple[bool, str]:
    """
    Supprime une alerte.
    
    Args:
        alert_id (int): ID de l'alerte
        
    Returns:
        Tuple[bool, str]: (Succès, Message)
    """
    try:
        with get_db_context() as db:
            alerte = db.query(Alerte).filter(Alerte.id == alert_id).first()
            
            if not alerte:
                return False, "Alerte non trouvée"
            
            db.delete(alerte)
            db.commit()
            
            return True, "Alerte supprimée"
            
    except Exception as e:
        return False, f"Erreur : {str(e)}"
