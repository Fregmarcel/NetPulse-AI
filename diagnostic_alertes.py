"""
Script de diagnostic pour comprendre pourquoi les alertes ne sont pas générées.
"""
import sys
from backend.database.connection import get_db_context
from backend.database.models import FHLink, MesureKPI, Alerte
from backend.analytics.kpi_calculator import get_latest_kpis
from backend.alerts.alert_engine import check_and_create_alerts
import config

print("=" * 70)
print("🔍 DIAGNOSTIC DU SYSTÈME D'ALERTES")
print("=" * 70)

# 1. Vérifier les liaisons
print("\n1️⃣ LIAISONS DANS LA BASE DE DONNÉES")
print("-" * 70)
with get_db_context() as db:
    links = db.query(FHLink).all()
    print(f"Nombre de liaisons: {len(links)}")
    for link in links:
        print(f"   • ID={link.id} | Nom: {link.nom} | Actif: {link.actif}")

if not links:
    print("❌ PROBLÈME: Aucune liaison trouvée !")
    sys.exit(1)

# 2. Vérifier les mesures
print("\n2️⃣ MESURES KPI")
print("-" * 70)
with get_db_context() as db:
    for link in links:
        count = db.query(MesureKPI).filter(MesureKPI.link_id == link.id).count()
        print(f"   • Liaison {link.id} ({link.nom}): {count} mesure(s)")
        
        if count > 0:
            # Dernière mesure
            last_measure = db.query(MesureKPI).filter(
                MesureKPI.link_id == link.id
            ).order_by(MesureKPI.timestamp.desc()).first()
            
            print(f"      Dernière mesure: {last_measure.timestamp}")
            print(f"      RSSI: {last_measure.rssi_dbm:.1f} dBm")
            print(f"      SNR: {last_measure.snr_db:.1f} dB")
            print(f"      BER: {last_measure.ber:.2e}")

# 3. Vérifier les seuils
print("\n3️⃣ SEUILS CONFIGURÉS")
print("-" * 70)
print(f"RSSI:")
print(f"   • CRITIQUE: < {config.SEUILS_RSSI['CRITIQUE']} dBm")
print(f"   • DEGRADED: < {config.SEUILS_RSSI['DEGRADED']} dBm")
print(f"   • ACCEPTABLE: < {config.SEUILS_RSSI['ACCEPTABLE']} dBm")
print(f"SNR:")
print(f"   • CRITIQUE: < {config.SEUILS_SNR['CRITIQUE']} dB")
print(f"   • DEGRADED: < {config.SEUILS_SNR['DEGRADED']} dB")

# 4. Vérifier les alertes existantes
print("\n4️⃣ ALERTES EXISTANTES")
print("-" * 70)
with get_db_context() as db:
    for link in links:
        all_alerts = db.query(Alerte).filter(Alerte.link_id == link.id).all()
        active_alerts = db.query(Alerte).filter(
            Alerte.link_id == link.id,
            Alerte.resolved == False
        ).all()
        
        print(f"   • Liaison {link.id}:")
        print(f"      - Total: {len(all_alerts)} alerte(s)")
        print(f"      - Actives: {len(active_alerts)} alerte(s)")
        
        if active_alerts:
            for alert in active_alerts:
                print(f"         [{alert.severite}] {alert.type}: {alert.message}")

# 5. Tester la génération d'alertes
print("\n5️⃣ TEST DE GÉNÉRATION D'ALERTES")
print("-" * 70)
for link in links:
    print(f"\n📡 Test pour liaison {link.id} ({link.nom})...")
    
    # Vérifier les KPIs
    kpis = get_latest_kpis(link.id)
    if kpis:
        print(f"   KPIs trouvés:")
        print(f"      RSSI: {kpis['rssi_dbm']:.1f} dBm")
        print(f"      SNR: {kpis['snr_db']:.1f} dB")
        print(f"      État: {kpis['etat_global']}")
        
        # Vérifier si des alertes devraient être créées
        should_alert_rssi = kpis['rssi_dbm'] < config.SEUILS_RSSI['DEGRADED']
        should_alert_snr = kpis['snr_db'] < config.SEUILS_SNR['DEGRADED']
        
        print(f"   Analyse:")
        print(f"      Devrait alerter RSSI: {'OUI' if should_alert_rssi else 'NON'}")
        print(f"      Devrait alerter SNR: {'OUI' if should_alert_snr else 'NON'}")
        
        # Tenter de créer des alertes
        print(f"\n   Tentative de génération d'alertes...")
        alerts_created = check_and_create_alerts(link.id)
        print(f"   Résultat: {len(alerts_created)} alerte(s) créée(s)")
    else:
        print(f"   ❌ Aucun KPI trouvé")

print("\n" + "=" * 70)
print("DIAGNOSTIC TERMINÉ")
print("=" * 70)
