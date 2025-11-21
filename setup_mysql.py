"""
Script d'initialisation de la base de données MySQL pour NetPulse-AI.
À exécuter une seule fois pour créer la base de données.
"""
import pymysql
import sys
from backend.database.init_db import init_database

def create_mysql_database():
    """Crée la base de données MySQL si elle n'existe pas."""
    
    print("🔧 Configuration de MySQL pour NetPulse-AI")
    print("=" * 50)
    
    # Paramètres de connexion Laragon par défaut
    host = input("Hôte MySQL [localhost]: ").strip() or "localhost"
    port = input("Port MySQL [3306]: ").strip() or "3306"
    user = input("Utilisateur MySQL [root]: ").strip() or "root"
    password = input("Mot de passe MySQL [vide pour Laragon]: ").strip() or ""
    database = input("Nom de la base de données [netpulse_ai]: ").strip() or "netpulse_ai"
    
    try:
        # Connexion au serveur MySQL (sans spécifier de base de données)
        print(f"\n📡 Connexion à MySQL sur {host}:{port}...")
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Vérifier si la base existe
            cursor.execute("SHOW DATABASES LIKE %s", (database,))
            result = cursor.fetchone()
            
            if result:
                print(f"⚠️  La base de données '{database}' existe déjà.")
                confirm = input("Voulez-vous la supprimer et la recréer ? [o/N]: ").strip().lower()
                
                if confirm == 'o':
                    print(f"🗑️  Suppression de la base '{database}'...")
                    cursor.execute(f"DROP DATABASE `{database}`")
                    print(f"✅ Base de données '{database}' supprimée.")
                else:
                    print("ℹ️  Conservation de la base existante.")
                    connection.close()
                    
                    # Initialiser les tables dans la base existante
                    print("\n📊 Initialisation des tables...")
                    init_database()
                    print("✅ Tables initialisées avec succès !")
                    return
            
            # Créer la base de données
            print(f"🔨 Création de la base de données '{database}'...")
            cursor.execute(f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de données '{database}' créée avec succès !")
            
        connection.close()
        
        # Mettre à jour le fichier .env
        print(f"\n📝 Mise à jour du fichier .env...")
        database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la ligne DATABASE_URL
        import re
        new_content = re.sub(
            r'DATABASE_URL=.*',
            f'DATABASE_URL={database_url}',
            content
        )
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fichier .env mis à jour avec : {database_url}")
        
        # Initialiser les tables
        print("\n📊 Création des tables et données initiales...")
        init_database()
        
        print("\n" + "=" * 50)
        print("🎉 Configuration MySQL terminée avec succès !")
        print("=" * 50)
        print(f"\n📋 Récapitulatif :")
        print(f"   • Base de données : {database}")
        print(f"   • Hôte : {host}:{port}")
        print(f"   • Utilisateur : {user}")
        print(f"\n🔐 Comptes utilisateurs créés :")
        print(f"   • Admin : admin@netpulse.ai / admin123")
        print(f"   • Tech  : tech@netpulse.ai / tech123")
        print(f"   • Guest : guest@netpulse.ai / guest123")
        print(f"\n🚀 Vous pouvez maintenant lancer l'application :")
        print(f"   streamlit run app.py")
        
    except pymysql.Error as e:
        print(f"\n❌ Erreur MySQL : {e}")
        print("\n💡 Vérifiez que :")
        print("   1. Laragon est démarré")
        print("   2. Le service MySQL est actif dans Laragon")
        print("   3. Les identifiants sont corrects")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_mysql_database()
