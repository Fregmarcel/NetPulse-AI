"""
Script pour analyser le fichier CSV avant import.
"""
import pandas as pd
import os

print("=" * 80)
print("📄 ANALYSE DU FICHIER CSV")
print("=" * 80)

# Chercher les fichiers CSV dans data/
csv_files = []
if os.path.exists('data'):
    for file in os.listdir('data'):
        if file.endswith('.csv'):
            csv_files.append(os.path.join('data', file))

if not csv_files:
    print("\n❌ Aucun fichier CSV trouvé dans le dossier 'data/'")
else:
    print(f"\n📁 Fichiers CSV trouvés:")
    for i, file in enumerate(csv_files, 1):
        print(f"   {i}. {file}")
    
    # Analyser le premier fichier
    file_to_analyze = csv_files[0]
    
    print(f"\n🔍 Analyse de: {file_to_analyze}")
    print("-" * 80)
    
    try:
        df = pd.read_csv(file_to_analyze)
        
        print(f"\n📊 Informations générales:")
        print(f"   - Nombre de lignes: {len(df)}")
        print(f"   - Nombre de colonnes: {len(df.columns)}")
        
        print(f"\n📋 Colonnes:")
        for col in df.columns:
            print(f"   • {col}")
        
        print(f"\n🔍 Aperçu des 3 premières lignes:")
        print(df.head(3).to_string())
        
        # Vérifier les colonnes requises
        required_cols = ['timestamp', 'link_name', 'rssi_dbm', 'snr_db', 'ber', 
                        'acm_modulation', 'latency_ms', 'packet_loss', 'rainfall_mm']
        
        print(f"\n✅ Vérification des colonnes requises:")
        missing = []
        for col in required_cols:
            if col in df.columns:
                print(f"   ✓ {col}")
            else:
                print(f"   ✗ {col} - MANQUANT")
                missing.append(col)
        
        if missing:
            print(f"\n❌ Colonnes manquantes: {', '.join(missing)}")
        else:
            print(f"\n✅ Toutes les colonnes requises sont présentes!")
        
        # Vérifier link_name
        if 'link_name' in df.columns:
            unique_links = df['link_name'].unique()
            print(f"\n📡 Liaisons dans le fichier:")
            for link in unique_links:
                count = len(df[df['link_name'] == link])
                print(f"   • {link}: {count} mesure(s)")
        
        # Vérifier les plages de valeurs
        if 'rssi_dbm' in df.columns:
            print(f"\n📊 Plages de valeurs RSSI:")
            print(f"   Min: {df['rssi_dbm'].min():.1f} dBm")
            print(f"   Max: {df['rssi_dbm'].max():.1f} dBm")
            print(f"   Moyenne: {df['rssi_dbm'].mean():.1f} dBm")
        
        # Vérifier les timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            print(f"\n📅 Plage temporelle:")
            print(f"   Du: {df['timestamp'].min()}")
            print(f"   Au: {df['timestamp'].max()}")
            
            # Calculer l'âge des données
            from datetime import datetime
            now = datetime.utcnow()
            age = (now - df['timestamp'].max()).days
            
            if age > 7:
                print(f"   ⚠️  Les données datent de {age} jours")
            elif age > 1:
                print(f"   ℹ️  Les données datent de {age} jours")
            else:
                print(f"   ✓ Les données sont récentes")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse: {e}")

print("\n" + "=" * 80)
