"""
Script pour ajouter des mesures récentes dans la base de données.
Génère des données pour les dernières 24h.
"""
from backend.database.connection import get_db_context
from backend.database.models import MesureKPI
from datetime import datetime, timedelta
import random

def generate_recent_data(link_id=1, hours=24):
    """Génère des mesures pour les dernières heures."""
    
    measures = []
    now = datetime.utcnow()
    
    # Générer une mesure toutes les 15 minutes
    for i in range(hours * 4):
        timestamp = now - timedelta(minutes=15 * i)
        
        # Simuler des variations réalistes
        base_rssi = -55 + random.uniform(-10, 10)
        base_snr = 18 + random.uniform(-5, 5)
        
        measure = MesureKPI(
            link_id=link_id,
            timestamp=timestamp,
            rssi_dbm=base_rssi,
            snr_db=base_snr,
            ber=random.uniform(1e-9, 1e-6),
            acm_modulation=random.choice(['64QAM', '32QAM', '16QAM']),
            rainfall_mm=random.uniform(0, 3),
            latency_ms=random.uniform(10, 25),
            packet_loss=random.uniform(0, 0.5)
        )
        measures.append(measure)
    
    return measures

# Générer et insérer les mesures
print("🔄 Génération de mesures récentes...")

with get_db_context() as db:
    # Link 1: 24h de données
    measures_link1 = generate_recent_data(link_id=1, hours=24)
    
    # Link 2: 12h de données
    measures_link2 = generate_recent_data(link_id=2, hours=12)
    
    # Supprimer les anciennes mesures pour éviter les doublons
    from datetime import datetime
    cutoff = datetime.utcnow() - timedelta(hours=25)
    db.query(MesureKPI).filter(MesureKPI.timestamp >= cutoff).delete()
    
    # Ajouter les nouvelles mesures
    db.add_all(measures_link1)
    db.add_all(measures_link2)
    db.commit()
    
    print(f"✅ {len(measures_link1)} mesures ajoutées pour Link 1")
    print(f"✅ {len(measures_link2)} mesures ajoutées pour Link 2")
    print(f"✅ Total: {len(measures_link1) + len(measures_link2)} mesures")

print("\n✓ Terminé ! Rechargez le Dashboard pour voir les nouvelles données.")
