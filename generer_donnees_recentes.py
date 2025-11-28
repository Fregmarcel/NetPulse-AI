"""
Script pour générer un fichier CSV avec des données récentes (dernières 24h).
"""
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

print("=" * 80)
print("📄 GÉNÉRATION D'UN FICHIER CSV AVEC DONNÉES RÉCENTES")
print("=" * 80)

# Paramètres
link_name = "Siège CNPS – Datacenter CNPS Kennedy"
nb_mesures = 96  # 96 mesures = 24h avec 1 mesure toutes les 15 min
interval_minutes = 15

# Générer les timestamps (dernières 24h)
now = datetime.now()
start_time = now - timedelta(hours=24)
timestamps = [start_time + timedelta(minutes=i * interval_minutes) for i in range(nb_mesures)]

print(f"\n📅 Génération de {nb_mesures} mesures")
print(f"   De: {timestamps[0]}")
print(f"   À:  {timestamps[-1]}")

# Générer des données réalistes avec dégradation progressive
data = []

for i, ts in enumerate(timestamps):
    # Simuler une dégradation progressive (plus on avance, plus ça se dégrade)
    degradation_factor = i / nb_mesures  # 0 à 1
    
    # RSSI : commence à -48 dBm et descend jusqu'à -68 dBm
    rssi = -48 - (20 * degradation_factor) + np.random.normal(0, 1)
    
    # SNR : commence à 32 dB et descend jusqu'à 10 dB
    snr = 32 - (22 * degradation_factor) + np.random.normal(0, 0.5)
    
    # BER : augmente avec la dégradation
    ber = 1.2e-9 * (1 + 100 * degradation_factor) + np.random.normal(0, 1e-9)
    ber = max(1e-10, ber)  # Minimum BER
    
    # Modulation : descend avec la dégradation
    if rssi > -55:
        modulation = "256QAM"
    elif rssi > -60:
        modulation = "128QAM"
    elif rssi > -65:
        modulation = "64QAM"
    elif rssi > -70:
        modulation = "32QAM"
    else:
        modulation = "16QAM"
    
    # Latence : augmente avec la dégradation
    latency = 2.3 + (10 * degradation_factor) + np.random.normal(0, 0.5)
    
    # Perte de paquets : augmente avec la dégradation
    packet_loss = 0.01 + (0.5 * degradation_factor) + np.random.normal(0, 0.01)
    packet_loss = max(0, packet_loss)
    
    # Pluie : simulation d'un épisode pluvieux au milieu
    if 30 < i < 60:
        rainfall = 5 + 10 * np.sin((i - 30) / 10 * np.pi)
    else:
        rainfall = np.random.uniform(0, 2)
    
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
output_file = 'data/mesures_recentes_24h.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Fichier généré : {output_file}")
print(f"   Nombre de lignes : {len(df)}")

# Statistiques
print(f"\n📊 Statistiques des données générées:")
print(f"   RSSI : {df['rssi_dbm'].min():.1f} à {df['rssi_dbm'].max():.1f} dBm")
print(f"   SNR : {df['snr_db'].min():.1f} à {df['snr_db'].max():.1f} dB")
print(f"   Pluie max : {df['rainfall_mm'].max():.1f} mm")

# Aperçu
print(f"\n📝 Aperçu des 5 premières lignes:")
print(df.head().to_string())

print(f"\n📝 Aperçu des 5 dernières lignes (les plus récentes):")
print(df.tail().to_string())

print("\n" + "=" * 80)
print("✅ TERMINÉ !")
print(f"Uploadez ce fichier dans Streamlit : {output_file}")
print("=" * 80)
