"""
Script pour nettoyer la base de données et permettre un réimport.
Supprime toutes les mesures et alertes.
"""
from backend.database.connection import get_db_context
from backend.database.models import MesureKPI, Alerte, KPISynthese

print("=" * 80)
print("🧹 NETTOYAGE DE LA BASE DE DONNÉES")
print("=" * 80)

print("\n⚠️  ATTENTION: Cette opération va supprimer:")
print("   - Toutes les mesures KPI")
print("   - Toutes les alertes")
print("   - Toutes les synthèses KPI")
print("\nLes liaisons FH et les utilisateurs seront conservés.")

reponse = input("\n❓ Continuer ? (oui/non): ").strip().lower()

if reponse != 'oui':
    print("\n❌ Opération annulée")
    exit()

print("\n🗑️  Suppression en cours...")

with get_db_context() as db:
    # Compter avant suppression
    count_mesures = db.query(MesureKPI).count()
    count_alertes = db.query(Alerte).count()
    count_syntheses = db.query(KPISynthese).count()
    
    print(f"\n📊 État actuel:")
    print(f"   - Mesures: {count_mesures}")
    print(f"   - Alertes: {count_alertes}")
    print(f"   - Synthèses: {count_syntheses}")
    
    # Supprimer
    db.query(MesureKPI).delete()
    db.query(Alerte).delete()
    db.query(KPISynthese).delete()
    
    db.commit()
    
    print(f"\n✅ Suppression terminée!")
    print(f"   ✓ {count_mesures} mesure(s) supprimée(s)")
    print(f"   ✓ {count_alertes} alerte(s) supprimée(s)")
    print(f"   ✓ {count_syntheses} synthèse(s) supprimée(s)")

print("\n" + "=" * 80)
print("✅ Base de données nettoyée!")
print("Vous pouvez maintenant réimporter vos données.")
print("=" * 80)
