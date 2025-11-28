"""
Script de test pour vérifier l'import de données et la génération d'alertes.
"""
import pandas as pd
from backend.ingestion.data_loader import load_measures_to_db
from backend.alerts.alert_engine import get_active_alerts, get_alerts_count_by_severity
from backend.database.connection import get_db_context
from backend.database.models import MesureKPI, Alerte

print("=" * 60)
print("TEST - Import de données et génération d'alertes")
print("=" * 60)

# 1. Charger le fichier CSV de test
print("\n1️⃣ Chargement du fichier CSV...")
df = pd.read_csv('data/sample_fh_data.csv')
print(f"✅ {len(df)} lignes chargées")

# 2. Afficher un aperçu des données
print("\n2️⃣ Aperçu des données:")
print(df.head())
print(f"\nPlage RSSI: {df['rssi_dbm'].min():.1f} à {df['rssi_dbm'].max():.1f} dBm")
print(f"Plage SNR: {df['snr_db'].min():.1f} à {df['snr_db'].max():.1f} dB")

# 3. Import dans la base de données
print("\n3️⃣ Import dans la base de données...")
success, stats = load_measures_to_db(df)

if success:
    print(f"✅ Import réussi!")
    print(f"   - Total: {stats['total']}")
    print(f"   - Importées: {stats['imported']}")
    print(f"   - Doublons: {stats['duplicates']}")
    print(f"   - Erreurs: {stats['errors']}")
    print(f"   - Alertes générées: {stats.get('alerts_generated', 0)}")
else:
    print(f"❌ Erreur lors de l'import")
    print(f"   Stats: {stats}")

# 4. Vérifier les alertes créées
print("\n4️⃣ Vérification des alertes...")
with get_db_context() as db:
    # Trouver l'ID de la liaison
    first_row = df.iloc[0]
    link_name = first_row['link_name']
    
    from backend.database.models import FHLink
    link = db.query(FHLink).filter(FHLink.nom == link_name).first()
    
    if link:
        print(f"📡 Liaison trouvée: {link.nom} (ID: {link.id})")
        
        # Compter les alertes
        active_alerts = db.query(Alerte).filter(
            Alerte.link_id == link.id,
            Alerte.resolved == False
        ).all()
        
        print(f"🚨 {len(active_alerts)} alerte(s) active(s)")
        
        if active_alerts:
            print("\n📋 Liste des alertes:")
            for alert in active_alerts:
                print(f"   - [{alert.severite}] {alert.type}: {alert.message}")
        
        # Statistiques par sévérité
        counts = get_alerts_count_by_severity(link.id)
        if counts:
            print(f"\n📊 Statistiques par sévérité:")
            for severity, count in counts.items():
                print(f"   - {severity}: {count}")
    else:
        print(f"⚠️ Liaison '{link_name}' non trouvée")

# 5. Vérifier les mesures
print("\n5️⃣ Vérification des mesures importées...")
with get_db_context() as db:
    total_measures = db.query(MesureKPI).count()
    print(f"📊 Total de mesures dans la BD: {total_measures}")

print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)
