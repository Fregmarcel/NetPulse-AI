"""
Script pour vérifier les données présentes dans la base de données.
Utile pour comprendre quelles données sont disponibles pour quelle liaison.
"""
from backend.database.connection import get_db_context
from backend.database.models import FHLink, MesureKPI, Alerte
from datetime import datetime

print("=" * 80)
print("🔍 VÉRIFICATION DES DONNÉES DANS LA BASE DE DONNÉES")
print("=" * 80)

# 1. Liaisons
print("\n1️⃣ LIAISONS FH")
print("-" * 80)
with get_db_context() as db:
    links = db.query(FHLink).all()
    
    if not links:
        print("❌ Aucune liaison trouvée dans la base de données")
    else:
        print(f"✓ {len(links)} liaison(s) trouvée(s):\n")
        
        for link in links:
            print(f"   📡 ID: {link.id}")
            print(f"      Nom: {link.nom}")
            print(f"      Sites: {link.site_a} ↔ {link.site_b}")
            print(f"      Fréquence: {link.frequence_ghz} GHz")
            print(f"      Distance: {link.distance_km} km")
            print(f"      Actif: {'✓ Oui' if link.actif else '✗ Non'}")
            print()

# 2. Mesures par liaison
print("\n2️⃣ MESURES KPI PAR LIAISON")
print("-" * 80)
with get_db_context() as db:
    for link in links:
        measures = db.query(MesureKPI).filter(MesureKPI.link_id == link.id).all()
        
        print(f"\n📡 Liaison ID={link.id} - {link.nom}")
        print(f"   Nombre de mesures: {len(measures)}")
        
        if measures:
            # Extraire timestamps
            timestamps = [m.timestamp for m in measures]
            oldest = min(timestamps)
            newest = max(timestamps)
            
            print(f"   Période: du {oldest.strftime('%d/%m/%Y %H:%M')} au {newest.strftime('%d/%m/%Y %H:%M')}")
            
            # Age des données
            now = datetime.utcnow()
            age_days = (now - newest).days
            age_hours = ((now - newest).seconds // 3600)
            
            if age_days > 0:
                print(f"   ⚠️  Dernière mesure: Il y a {age_days} jour(s) et {age_hours}h")
            else:
                print(f"   ✓ Dernière mesure: Il y a {age_hours}h")
            
            # Dernière mesure
            last_measure = max(measures, key=lambda m: m.timestamp)
            print(f"\n   📊 Dernière mesure:")
            print(f"      - Timestamp: {last_measure.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"      - RSSI: {last_measure.rssi_dbm:.1f} dBm")
            print(f"      - SNR: {last_measure.snr_db:.1f} dB")
            print(f"      - BER: {last_measure.ber:.2e}")
            print(f"      - Modulation: {last_measure.acm_modulation}")
            print(f"      - Pluie: {last_measure.rainfall_mm:.1f} mm")
            
            # Statistiques RSSI
            rssi_values = [m.rssi_dbm for m in measures]
            print(f"\n   📈 Statistiques RSSI:")
            print(f"      - Min: {min(rssi_values):.1f} dBm")
            print(f"      - Max: {max(rssi_values):.1f} dBm")
            print(f"      - Moyenne: {sum(rssi_values)/len(rssi_values):.1f} dBm")
        else:
            print("   ❌ Aucune mesure pour cette liaison")

# 3. Alertes par liaison
print("\n\n3️⃣ ALERTES PAR LIAISON")
print("-" * 80)
with get_db_context() as db:
    for link in links:
        all_alerts = db.query(Alerte).filter(Alerte.link_id == link.id).all()
        active_alerts = [a for a in all_alerts if not a.resolved]
        
        print(f"\n📡 Liaison ID={link.id} - {link.nom}")
        print(f"   Total alertes: {len(all_alerts)}")
        print(f"   Alertes actives: {len(active_alerts)}")
        
        if active_alerts:
            print(f"\n   🚨 Liste des alertes actives:")
            for alert in active_alerts:
                print(f"      • [{alert.severite}] {alert.type}")
                print(f"        Message: {alert.message}")
                print(f"        Créée le: {alert.timestamp.strftime('%d/%m/%Y %H:%M')}")
                print()

# 4. Résumé global
print("\n" + "=" * 80)
print("📊 RÉSUMÉ GLOBAL")
print("=" * 80)
with get_db_context() as db:
    total_links = db.query(FHLink).count()
    total_measures = db.query(MesureKPI).count()
    total_alerts = db.query(Alerte).count()
    active_alerts = db.query(Alerte).filter(Alerte.resolved == False).count()
    
    print(f"✓ Liaisons: {total_links}")
    print(f"✓ Mesures totales: {total_measures}")
    print(f"✓ Alertes totales: {total_alerts} (dont {active_alerts} actives)")

print("\n" + "=" * 80)
