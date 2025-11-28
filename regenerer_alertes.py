"""
Script pour supprimer toutes les alertes et les régénérer.
Utile pour tester le système de génération d'alertes.
"""
from backend.database.connection import get_db_context
from backend.database.models import Alerte, FHLink
from backend.alerts.alert_engine import check_and_create_alerts

print("=" * 70)
print("🔄 RÉINITIALISATION ET RÉGÉNÉRATION DES ALERTES")
print("=" * 70)

# 1. Supprimer toutes les alertes existantes
print("\n1️⃣ Suppression des alertes existantes...")
with get_db_context() as db:
    count = db.query(Alerte).count()
    db.query(Alerte).delete()
    db.commit()
    print(f"   ✓ {count} alerte(s) supprimée(s)")

# 2. Régénérer les alertes pour toutes les liaisons
print("\n2️⃣ Régénération des alertes...")
with get_db_context() as db:
    links = db.query(FHLink).all()
    total_alerts = 0
    
    for link in links:
        print(f"\n   📡 Analyse de la liaison: {link.nom} (ID={link.id})")
        alerts_created = check_and_create_alerts(link.id)
        total_alerts += len(alerts_created)
        
        if alerts_created:
            print(f"      ✓ {len(alerts_created)} alerte(s) créée(s)")
        else:
            print(f"      • Aucune alerte à créer (seuils OK)")

print(f"\n{'='*70}")
print(f"✅ TERMINÉ: {total_alerts} alerte(s) générée(s) au total")
print(f"{'='*70}")
