"""
Générateur flexible de données CSV avec choix de la période.
"""
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

print("=" * 80)
print("📄 GÉNÉRATEUR DE DONNÉES CSV NETPULSE-AI")
print("=" * 80)

# Menu de sélection
print("\n📅 Choisissez la période des données:")
print("   1. Dernières 24 heures (recommandé)")
print("   2. Dernières 48 heures")
print("   3. Dernière semaine")
print("   4. Données en temps réel (dernières 6 heures)")

choix = input("\nVotre choix (1-4): ").strip()

# Configuration selon le choix
if choix == "1":
    periode = 24
    nb_mesures = 96
    nom_fichier = "mesures_24h"
    print("\n✅ Génération de 96 mesures sur 24h (1 toutes les 15 min)")
elif choix == "2":
    periode = 48
    nb_mesures = 192
    nom_fichier = "mesures_48h"
    print("\n✅ Génération de 192 mesures sur 48h (1 toutes les 15 min)")
elif choix == "3":
    periode = 168  # 7 jours
    nb_mesures = 168
    nom_fichier = "mesures_7j"
    print("\n✅ Génération de 168 mesures sur 7 jours (1 par heure)")
elif choix == "4":
    periode = 6
    nb_mesures = 24
    nom_fichier = "mesures_temps_reel_6h"
    print("\n✅ Génération de 24 mesures sur 6h (1 toutes les 15 min)")
else:
    print("\n❌ Choix invalide, utilisation par défaut : 24h")
    periode = 24
    nb_mesures = 96
    nom_fichier = "mesures_24h"

# Nom de la liaison
link_name = "Siège CNPS – Datacenter CNPS Kennedy"

# Intervalle entre mesures
interval_minutes = (periode * 60) // nb_mesures

# Générer les timestamps
now = datetime.now()
start_time = now - timedelta(hours=periode)
timestamps = [start_time + timedelta(minutes=i * interval_minutes) for i in range(nb_mesures)]

print(f"\n📊 Configuration:")
print(f"   Période: {periode}h")
print(f"   Nombre de mesures: {nb_mesures}")
print(f"   Intervalle: {interval_minutes} minutes")
print(f"   De: {timestamps[0].strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   À:  {timestamps[-1].strftime('%Y-%m-%d %H:%M:%S')}")

# Type de scénario
print("\n🎭 Choisissez le scénario:")
print("   1. Normal (valeurs stables)")
print("   2. Dégradation progressive")
print("   3. Pic de dégradation (pluie)")
print("   4. Aléatoire réaliste")

scenario = input("\nScénario (1-4, défaut=2): ").strip() or "2"

data = []

for i, ts in enumerate(timestamps):
    progress = i / nb_mesures
    
    if scenario == "1":
        # Normal : valeurs stables
        rssi = -50 + np.random.normal(0, 2)
        snr = 30 + np.random.normal(0, 2)
        ber = 1.5e-9 + np.random.normal(0, 0.5e-9)
        rainfall = np.random.uniform(0, 1)
        
    elif scenario == "2":
        # Dégradation progressive
        rssi = -48 - (20 * progress) + np.random.normal(0, 1)
        snr = 32 - (22 * progress) + np.random.normal(0, 0.5)
        ber = 1.2e-9 * (1 + 100 * progress) + np.random.normal(0, 1e-9)
        rainfall = 2 + 10 * progress + np.random.uniform(0, 2)
        
    elif scenario == "3":
        # Pic de dégradation au milieu (pluie)
        mid = nb_mesures // 2
        distance_from_mid = abs(i - mid) / mid
        degradation = 1 - distance_from_mid
        
        rssi = -50 - (15 * degradation) + np.random.normal(0, 1)
        snr = 30 - (18 * degradation) + np.random.normal(0, 0.5)
        ber = 1.5e-9 * (1 + 50 * degradation) + np.random.normal(0, 1e-9)
        rainfall = 20 * degradation + np.random.uniform(0, 2)
        
    else:
        # Aléatoire réaliste
        base_rssi = -52
        base_snr = 28
        variation = np.sin(progress * 4 * np.pi) * 10
        
        rssi = base_rssi + variation + np.random.normal(0, 2)
        snr = base_snr - (variation / 3) + np.random.normal(0, 1)
        ber = 2e-9 * (1 + abs(variation) / 5) + np.random.normal(0, 0.5e-9)
        rainfall = max(0, 5 * np.sin(progress * 2 * np.pi) + np.random.uniform(0, 2))
    
    # Sécuriser les valeurs
    ber = max(1e-10, ber)
    rainfall = max(0, rainfall)
    
    # Modulation selon RSSI
    if rssi > -55:
        modulation = "256QAM"
    elif rssi > -60:
        modulation = "128QAM"
    elif rssi > -65:
        modulation = "64QAM"
    elif rssi > -70:
        modulation = "32QAM"
    elif rssi > -75:
        modulation = "16QAM"
    else:
        modulation = "QPSK"
    
    # Latence et perte selon qualité
    quality_factor = (rssi + 80) / 30  # 0 = mauvais, 1 = excellent
    latency = 2 + (15 * (1 - quality_factor)) + np.random.normal(0, 0.5)
    packet_loss = 0.01 + (1 * (1 - quality_factor)) + np.random.normal(0, 0.05)
    packet_loss = max(0, packet_loss)
    
    data.append({
        'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
        'link_name': link_name,
        'rssi_dbm': round(rssi, 1),
        'snr_db': round(snr, 1),
        'ber': f"{ber:.2e}",
        'acm_modulation': modulation,
        'latency_ms': round(latency, 1),
        'packet_loss': round(packet_loss, 2),
        'rainfall_mm': round(rainfall, 1)
    })

# Créer le DataFrame
df = pd.DataFrame(data)

# Sauvegarder
output_file = f'data/{nom_fichier}.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Fichier généré : {output_file}")
print(f"   Nombre de lignes : {len(df)}")

# Statistiques
print(f"\n📊 Statistiques:")
print(f"   RSSI : {df['rssi_dbm'].min():.1f} à {df['rssi_dbm'].max():.1f} dBm (moy: {df['rssi_dbm'].mean():.1f})")
print(f"   SNR  : {df['snr_db'].min():.1f} à {df['snr_db'].max():.1f} dB (moy: {df['snr_db'].mean():.1f})")
print(f"   Pluie: 0 à {df['rainfall_mm'].max():.1f} mm (moy: {df['rainfall_mm'].mean():.1f})")

# Compter les valeurs critiques
rssi_critique = len(df[df['rssi_dbm'] < -75])
snr_critique = len(df[df['snr_db'] < 10])

print(f"\n⚠️  Valeurs critiques:")
print(f"   RSSI < -75 dBm: {rssi_critique} mesure(s)")
print(f"   SNR < 10 dB: {snr_critique} mesure(s)")

if rssi_critique > 0 or snr_critique > 0:
    print(f"   → {rssi_critique + snr_critique} alerte(s) devraient être générées")

print("\n" + "=" * 80)
print("✅ TERMINÉ !")
print(f"\n📤 Pour importer dans NetPulse-AI:")
print(f"   1. Lancez: streamlit run app.py")
print(f"   2. Connectez-vous en admin")
print(f"   3. Allez sur 📤 Import")
print(f"   4. Uploadez: {output_file}")
print("=" * 80)
