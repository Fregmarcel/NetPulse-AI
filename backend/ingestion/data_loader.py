"""
Loader de données pour insérer les mesures dans la base de données.
"""
import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Set
from backend.database.models import MesureKPI, FHLink
from backend.database.connection import get_db_context
from backend.security.logger import log_info, log_error


def get_or_create_link(link_name: str) -> Tuple[int, bool]:
    """
    Récupère l'ID d'une liaison ou la crée si elle n'existe pas.
    
    Args:
        link_name (str): Nom de la liaison
        
    Returns:
        Tuple[int, bool]: (ID de la liaison, Créée ou non)
    """
    with get_db_context() as db:
        # Chercher la liaison existante
        link = db.query(FHLink).filter(FHLink.nom == link_name).first()
        
        if link:
            return link.id, False
        
        # Créer une nouvelle liaison
        new_link = FHLink(
            nom=link_name,
            site_a="Site A",
            site_b="Site B",
            frequence_ghz=18.0,
            distance_km=10.0,
            actif=True,
            description=f"Liaison créée automatiquement lors de l'import"
        )
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        log_info(f"Nouvelle liaison créée : {link_name}", "DataLoader")
        return new_link.id, True


def load_measures_to_db(df: pd.DataFrame, link_name: str = None) -> Tuple[bool, Dict]:
    """
    Charge les mesures d'un DataFrame dans la base de données.
    
    Args:
        df (pd.DataFrame): DataFrame contenant les mesures
        link_name (str, optional): Nom de la liaison (si non présent dans le DataFrame)
        
    Returns:
        Tuple[bool, Dict]: (Succès, Statistiques d'import)
    """
    stats = {
        'total': len(df),
        'imported': 0,
        'skipped': 0,
        'errors': 0,
        'duplicates': 0,
        'alerts_generated': 0
    }
    
    # Ensemble pour suivre les liaisons importées
    imported_links: Set[int] = set()
    
    try:
        with get_db_context() as db:
            for idx, row in df.iterrows():
                try:
                    # Déterminer le nom de la liaison
                    current_link_name = row.get('link_name', link_name)
                    if not current_link_name:
                        stats['errors'] += 1
                        continue
                    
                    # Récupérer ou créer la liaison
                    link_id, _ = get_or_create_link(current_link_name)
                    imported_links.add(link_id)
                    
                    # Vérifier si la mesure existe déjà
                    timestamp = pd.to_datetime(row['timestamp'])
                    existing = db.query(MesureKPI).filter(
                        MesureKPI.link_id == link_id,
                        MesureKPI.timestamp == timestamp
                    ).first()
                    
                    if existing:
                        stats['duplicates'] += 1
                        stats['skipped'] += 1
                        continue
                    
                    # Créer la nouvelle mesure
                    mesure = MesureKPI(
                        link_id=link_id,
                        timestamp=timestamp,
                        rssi_dbm=float(row['rssi_dbm']),
                        snr_db=float(row['snr_db']),
                        ber=float(row['ber']),
                        acm_modulation=str(row['acm_modulation']),
                        latency_ms=float(row.get('latency_ms', 0)),
                        packet_loss=float(row.get('packet_loss', 0)),
                        rainfall_mm=float(row.get('rainfall_mm', 0)),
                        temperature_c=float(row.get('temperature_c')) if 'temperature_c' in row else None
                    )
                    
                    db.add(mesure)
                    stats['imported'] += 1
                    
                    # Commit par batch de 100 lignes
                    if stats['imported'] % 100 == 0:
                        db.commit()
                        log_info(f"Import en cours : {stats['imported']} lignes", "DataLoader")
                
                except Exception as e:
                    stats['errors'] += 1
                    log_error(f"Erreur ligne {idx}: {str(e)}", module="DataLoader")
                    continue
            
            # Commit final
            db.commit()
            
        success = stats['imported'] > 0
        log_info(f"Import terminé : {stats['imported']}/{stats['total']} lignes importées", "DataLoader")
        
        # Générer les alertes pour chaque liaison (même si doublons, vérifier quand même)
        if imported_links:
            from backend.alerts.alert_engine import check_and_create_alerts
            print(f"\n{'='*60}")
            print(f"🚨 GÉNÉRATION DES ALERTES")
            print(f"{'='*60}")
            log_info(f"Génération des alertes pour {len(imported_links)} liaison(s)", "DataLoader")
            
            for link_id in imported_links:
                try:
                    print(f"\n📡 Analyse de la liaison ID={link_id}")
                    alerts_created = check_and_create_alerts(link_id)
                    stats['alerts_generated'] += len(alerts_created)
                    if alerts_created:
                        log_info(f"Liaison {link_id}: {len(alerts_created)} alerte(s) générée(s)", "DataLoader")
                        print(f"   ✓ {len(alerts_created)} alerte(s) créée(s)")
                    else:
                        print(f"   • Aucune nouvelle alerte (seuils OK ou alertes déjà existantes)")
                except Exception as e:
                    log_error(f"Erreur génération alertes pour liaison {link_id}: {str(e)}", module="DataLoader")
                    print(f"   ✗ Erreur: {str(e)}")
            
            print(f"\n{'='*60}")
            print(f"📊 RÉSULTAT: {stats['alerts_generated']} alerte(s) générée(s) au total")
            print(f"{'='*60}\n")
            log_info(f"Total: {stats['alerts_generated']} alerte(s) générée(s)", "DataLoader")
        
        return success, stats
        
    except Exception as e:
        log_error(f"Erreur lors de l'import : {str(e)}", module="DataLoader")
        return False, stats


def load_single_measure(
    link_id: int,
    timestamp: datetime,
    rssi_dbm: float,
    snr_db: float,
    ber: float,
    acm_modulation: str,
    latency_ms: float = 0,
    packet_loss: float = 0,
    rainfall_mm: float = 0
) -> Tuple[bool, str]:
    """
    Insère une mesure unique dans la base de données.
    
    Args:
        link_id (int): ID de la liaison
        timestamp (datetime): Timestamp de la mesure
        rssi_dbm (float): RSSI en dBm
        snr_db (float): SNR en dB
        ber (float): BER
        acm_modulation (str): Modulation ACM
        latency_ms (float): Latence en ms
        packet_loss (float): Perte de paquets en %
        rainfall_mm (float): Pluie en mm
        
    Returns:
        Tuple[bool, str]: (Succès, Message)
    """
    try:
        with get_db_context() as db:
            mesure = MesureKPI(
                link_id=link_id,
                timestamp=timestamp,
                rssi_dbm=rssi_dbm,
                snr_db=snr_db,
                ber=ber,
                acm_modulation=acm_modulation,
                latency_ms=latency_ms,
                packet_loss=packet_loss,
                rainfall_mm=rainfall_mm
            )
            
            db.add(mesure)
            db.commit()
            
            return True, "Mesure insérée avec succès"
            
    except Exception as e:
        log_error(f"Erreur lors de l'insertion : {str(e)}", module="DataLoader")
        return False, f"Erreur : {str(e)}"


def bulk_load_measures(measures: list) -> Tuple[bool, Dict]:
    """
    Charge une liste de mesures en bulk.
    
    Args:
        measures (list): Liste de dictionnaires contenant les mesures
        
    Returns:
        Tuple[bool, Dict]: (Succès, Statistiques)
    """
    stats = {
        'total': len(measures),
        'imported': 0,
        'errors': 0
    }
    
    try:
        with get_db_context() as db:
            for measure_data in measures:
                try:
                    mesure = MesureKPI(**measure_data)
                    db.add(mesure)
                    stats['imported'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    log_error(f"Erreur mesure : {str(e)}", module="DataLoader")
            
            db.commit()
            
        return stats['imported'] > 0, stats
        
    except Exception as e:
        log_error(f"Erreur bulk load : {str(e)}", module="DataLoader")
        return False, stats


def delete_measures_by_link(link_id: int, date_from: datetime = None, date_to: datetime = None) -> Tuple[bool, int]:
    """
    Supprime les mesures d'une liaison pour une période donnée.
    
    Args:
        link_id (int): ID de la liaison
        date_from (datetime, optional): Date de début
        date_to (datetime, optional): Date de fin
        
    Returns:
        Tuple[bool, int]: (Succès, Nombre de mesures supprimées)
    """
    try:
        with get_db_context() as db:
            query = db.query(MesureKPI).filter(MesureKPI.link_id == link_id)
            
            if date_from:
                query = query.filter(MesureKPI.timestamp >= date_from)
            if date_to:
                query = query.filter(MesureKPI.timestamp <= date_to)
            
            count = query.count()
            query.delete(synchronize_session=False)
            db.commit()
            
            log_info(f"{count} mesure(s) supprimée(s) pour link_id={link_id}", "DataLoader")
            return True, count
            
    except Exception as e:
        log_error(f"Erreur lors de la suppression : {str(e)}", module="DataLoader")
        return False, 0


def get_import_statistics() -> Dict:
    """
    Retourne des statistiques sur les données importées.
    
    Returns:
        Dict: Statistiques d'import
    """
    try:
        with get_db_context() as db:
            total_measures = db.query(MesureKPI).count()
            total_links = db.query(FHLink).count()
            
            # Dernière mesure importée
            last_measure = db.query(MesureKPI).order_by(MesureKPI.timestamp.desc()).first()
            
            return {
                'total_measures': total_measures,
                'total_links': total_links,
                'last_import': last_measure.timestamp if last_measure else None
            }
            
    except Exception as e:
        log_error(f"Erreur statistiques : {str(e)}", module="DataLoader")
        return {}
