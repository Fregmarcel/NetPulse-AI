"""
Script pour vérifier le contenu de la base de données MySQL.
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Récupérer l'URL de connexion depuis .env
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/netpulse_ai')

# Parser l'URL
# Format: mysql+pymysql://root:@localhost:3306/netpulse_ai
parts = DATABASE_URL.replace('mysql+pymysql://', '').split('/')
host_port_part = parts[0].split('@')[1]
host = host_port_part.split(':')[0]
port = int(host_port_part.split(':')[1]) if ':' in host_port_part else 3306
database = parts[1]

user_pass = parts[0].split('@')[0]
user = user_pass.split(':')[0]
password = user_pass.split(':')[1] if ':' in user_pass else ''

print("=" * 80)
print("🔍 VÉRIFICATION DE LA BASE DE DONNÉES MYSQL")
print("=" * 80)

print(f"\n📋 Paramètres de connexion:")
print(f"   Hôte: {host}")
print(f"   Port: {port}")
print(f"   Utilisateur: {user}")
print(f"   Mot de passe: {'(vide)' if not password else '***'}")
print(f"   Base de données: {database}")

try:
    # Connexion à MySQL
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print(f"\n✅ Connexion réussie à MySQL!")
    
    with connection.cursor() as cursor:
        # Lister les tables
        print(f"\n📊 TABLES DANS LA BASE '{database}':")
        print("-" * 80)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ Aucune table trouvée!")
        else:
            for table in tables:
                table_name = list(table.values())[0]
                
                # Compter les lignes
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                count = cursor.fetchone()['count']
                
                print(f"   📋 {table_name}: {count} ligne(s)")
        
        # Détails des mesures_kpi
        print(f"\n📊 DÉTAILS DE LA TABLE 'mesures_kpi':")
        print("-" * 80)
        
        cursor.execute("SELECT COUNT(*) as count FROM mesures_kpi")
        total = cursor.fetchone()['count']
        print(f"   Total de mesures: {total}")
        
        if total > 0:
            # Dernières mesures
            cursor.execute("""
                SELECT link_id, timestamp, rssi_dbm, snr_db, ber 
                FROM mesures_kpi 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            measures = cursor.fetchall()
            
            print(f"\n   📝 Dernières mesures:")
            for m in measures:
                print(f"      • Liaison {m['link_id']} - {m['timestamp']}")
                print(f"        RSSI: {m['rssi_dbm']:.1f} dBm, SNR: {m['snr_db']:.1f} dB")
            
            # Par liaison
            cursor.execute("""
                SELECT link_id, COUNT(*) as count 
                FROM mesures_kpi 
                GROUP BY link_id
            """)
            by_link = cursor.fetchall()
            
            print(f"\n   📊 Mesures par liaison:")
            for item in by_link:
                print(f"      • Liaison ID={item['link_id']}: {item['count']} mesure(s)")
        
        # Détails des liaisons
        print(f"\n📡 LIAISONS (fh_links):")
        print("-" * 80)
        cursor.execute("SELECT id, nom, site_a, site_b, actif FROM fh_links")
        links = cursor.fetchall()
        
        if links:
            for link in links:
                print(f"   📡 ID={link['id']} - {link['nom']}")
                print(f"      {link['site_a']} ↔ {link['site_b']}")
                print(f"      Actif: {'Oui' if link['actif'] else 'Non'}")
        else:
            print("   ❌ Aucune liaison trouvée")
        
        # Alertes
        print(f"\n🚨 ALERTES:")
        print("-" * 80)
        cursor.execute("SELECT COUNT(*) as count FROM alertes WHERE resolved = 0")
        active_alerts = cursor.fetchone()['count']
        print(f"   Alertes actives: {active_alerts}")
    
    connection.close()
    
except pymysql.Error as e:
    print(f"\n❌ ERREUR MySQL: {e}")
    print(f"\nVérifiez que:")
    print(f"   1. MySQL est démarré dans Laragon")
    print(f"   2. La base de données '{database}' existe")
    print(f"   3. Les paramètres dans .env sont corrects")

print("\n" + "=" * 80)
