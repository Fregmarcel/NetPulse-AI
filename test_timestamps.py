"""
Script de diagnostic pour vérifier les timestamps des mesures.
"""
from backend.database.connection import get_db_context
from backend.database.models import MesureKPI
from datetime import datetime, timedelta

with get_db_context() as db:
    # Compter toutes les mesures
    total = db.query(MesureKPI).count()
    print(f"Total mesures dans la DB: {total}")
    
    # Récupérer les 5 dernières mesures
    measures = db.query(MesureKPI).order_by(MesureKPI.timestamp.desc()).limit(5).all()
    
    print("\n=== Dernières mesures ===")
    for m in measures:
        print(f"Timestamp: {m.timestamp} | Link ID: {m.link_id} | RSSI: {m.rssi_dbm} dBm")
    
    # Vérifier par liaison
    print("\n=== Mesures par liaison ===")
    for link_id in [1, 2]:
        count = db.query(MesureKPI).filter(MesureKPI.link_id == link_id).count()
        print(f"Link ID {link_id}: {count} mesures")
        
        # Dernière mesure de cette liaison
        last = db.query(MesureKPI).filter(MesureKPI.link_id == link_id).order_by(MesureKPI.timestamp.desc()).first()
        if last:
            print(f"  Dernière: {last.timestamp}")
    
    print(f"\n=== Comparaison horaires ===")
    print(f"UTC now:   {datetime.utcnow()}")
    print(f"Local now: {datetime.now()}")
    
    # Tester les filtres de période
    print(f"\n=== Test filtres période (Link ID 1) ===")
    for hours in [6, 12, 24, 48, 72]:
        date_from_utc = datetime.utcnow() - timedelta(hours=hours)
        date_from_local = datetime.now() - timedelta(hours=hours)
        
        count_utc = db.query(MesureKPI).filter(
            MesureKPI.link_id == 1,
            MesureKPI.timestamp >= date_from_utc
        ).count()
        
        count_local = db.query(MesureKPI).filter(
            MesureKPI.link_id == 1,
            MesureKPI.timestamp >= date_from_local
        ).count()
        
        print(f"{hours}h: UTC={count_utc}, Local={count_local}")
