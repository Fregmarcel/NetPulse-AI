"""
Script de vérification de la connexion MySQL avec Laragon.
"""
import pymysql
import sys

def test_mysql_connection():
    """Teste la connexion au serveur MySQL de Laragon."""
    
    print("🔍 Test de connexion à MySQL (Laragon)")
    print("=" * 50)
    
    # Configuration par défaut de Laragon
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',  # Laragon par défaut : pas de mot de passe
        'charset': 'utf8mb4'
    }
    
    try:
        # Test de connexion
        print(f"\n📡 Connexion à MySQL sur {config['host']}:{config['port']}...")
        connection = pymysql.connect(**config, cursorclass=pymysql.cursors.DictCursor)
        
        print("✅ Connexion réussie !")
        
        # Récupérer la version de MySQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 Version MySQL : {version['VERSION()']}")
            
            # Lister les bases de données
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"\n📂 Bases de données disponibles ({len(databases)}) :")
            for db in databases:
                db_name = db['Database']
                if db_name == 'netpulse_ai':
                    print(f"   ✅ {db_name} (Base NetPulse-AI)")
                else:
                    print(f"   • {db_name}")
            
            # Vérifier si netpulse_ai existe
            cursor.execute("SHOW DATABASES LIKE 'netpulse_ai'")
            result = cursor.fetchone()
            
            if result:
                print(f"\n🎯 La base 'netpulse_ai' existe déjà !")
                
                # Se connecter à la base netpulse_ai
                connection.select_db('netpulse_ai')
                
                # Lister les tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"📋 Tables dans netpulse_ai ({len(tables)}) :")
                    for table in tables:
                        table_name = list(table.values())[0]
                        # Compter les lignes
                        cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                        count = cursor.fetchone()['count']
                        print(f"   • {table_name} : {count} ligne(s)")
                else:
                    print("⚠️  Aucune table trouvée dans netpulse_ai")
                    print("💡 Exécutez : python backend\\database\\init_db.py")
            else:
                print(f"\n⚠️  La base 'netpulse_ai' n'existe pas encore")
                print("\n💡 Pour créer la base, deux options :")
                print("   Option 1 - Via HeidiSQL :")
                print("     1. Ouvrez HeidiSQL depuis Laragon")
                print("     2. Clic droit → Create new → Database")
                print("     3. Nom : netpulse_ai")
                print("     4. OK")
                print("\n   Option 2 - Via terminal :")
                print("     1. mysql -u root")
                print("     2. CREATE DATABASE netpulse_ai;")
                print("     3. EXIT;")
                print("\n   Puis exécutez : python backend\\database\\init_db.py")
        
        connection.close()
        
        print("\n" + "=" * 50)
        print("✅ Test terminé avec succès !")
        print("=" * 50)
        
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ Erreur MySQL : {e}")
        print("\n💡 Solutions possibles :")
        print("   1. Vérifiez que Laragon est démarré")
        print("   2. Vérifiez que le service MySQL est actif (icône verte)")
        print("   3. Redémarrez MySQL dans Laragon")
        print("   4. Vérifiez le mot de passe root dans Laragon")
        
        if "Can't connect" in str(e):
            print("\n🔧 Le serveur MySQL ne répond pas")
            print("   → Démarrez MySQL depuis Laragon")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mysql_connection()
    sys.exit(0 if success else 1)
