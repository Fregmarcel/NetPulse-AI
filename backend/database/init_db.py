"""
Script d'initialisation de la base de données.
Crée les tables et insère les données de test (utilisateurs et liaisons FH).
"""
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.database.models import (
    Base, Utilisateur, FHLink, ParametresSysteme, UserRole
)
from backend.database.connection import engine, get_db_context
from backend.security.auth import hash_password
import config


def create_tables():
    """Crée toutes les tables de la base de données."""
    print("📦 Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")


def create_default_users():
    """Crée les utilisateurs par défaut."""
    print("👤 Création des utilisateurs par défaut...")
    
    with get_db_context() as db:
        # Vérifier si des utilisateurs existent déjà
        existing_users = db.query(Utilisateur).count()
        if existing_users > 0:
            print(f"⚠️ {existing_users} utilisateur(s) existent déjà, skip création")
            return
        
        users_data = [
            {
                'email': 'admin@netpulse.ai',
                'password': 'admin123',
                'role': UserRole.ADMIN,
                'nom_complet': 'Administrateur Système'
            },
            {
                'email': 'tech@netpulse.ai',
                'password': 'tech123',
                'role': UserRole.TECH,
                'nom_complet': 'Technicien Support'
            },
            {
                'email': 'guest@netpulse.ai',
                'password': 'guest123',
                'role': UserRole.GUEST,
                'nom_complet': 'Invité Lecture Seule'
            }
        ]
        
        for user_data in users_data:
            user = Utilisateur(
                email=user_data['email'],
                password_hash=hash_password(user_data['password']),
                role=user_data['role'],
                nom_complet=user_data['nom_complet'],
                actif=True,
                date_creation=datetime.utcnow()
            )
            db.add(user)
            print(f"  ✓ Utilisateur créé : {user.email} (rôle: {user.role.value})")
        
        db.commit()
        print("✅ Utilisateurs créés avec succès")


def create_default_links():
    """Crée les liaisons FH par défaut."""
    print("📡 Création des liaisons FH par défaut...")
    
    with get_db_context() as db:
        # Vérifier si des liaisons existent déjà
        existing_links = db.query(FHLink).count()
        if existing_links > 0:
            print(f"⚠️ {existing_links} liaison(s) existent déjà, skip création")
            return
        
        links_data = [
            {
                'nom': 'Siège CNPS – Datacenter CNPS Kennedy',
                'site_a': 'Siège CNPS Yaoundé',
                'site_b': 'Datacenter CNPS Kennedy',
                'frequence_ghz': 18.5,
                'distance_km': 12.3,
                'latitude_a': 3.8667,
                'longitude_a': 11.5167,
                'latitude_b': 3.8480,
                'longitude_b': 11.5020,
                'description': 'Liaison principale entre le siège et le datacenter de secours'
            },
            {
                'nom': 'Datacenter Kennedy – Agence Douala',
                'site_a': 'Datacenter CNPS Kennedy',
                'site_b': 'Agence CNPS Douala',
                'frequence_ghz': 23.0,
                'distance_km': 198.5,
                'latitude_a': 3.8480,
                'longitude_a': 11.5020,
                'latitude_b': 4.0511,
                'longitude_b': 9.7679,
                'description': 'Liaison longue distance vers l\'agence principale de Douala'
            }
        ]
        
        for link_data in links_data:
            link = FHLink(**link_data)
            db.add(link)
            print(f"  ✓ Liaison créée : {link.nom}")
            print(f"    • {link.site_a} ↔ {link.site_b}")
            print(f"    • Fréquence : {link.frequence_ghz} GHz")
            print(f"    • Distance : {link.distance_km} km")
        
        db.commit()
        print("✅ Liaisons FH créées avec succès")


def create_system_parameters():
    """Crée les paramètres système par défaut."""
    print("⚙️ Création des paramètres système...")
    
    with get_db_context() as db:
        # Vérifier si des paramètres existent déjà
        existing_params = db.query(ParametresSysteme).count()
        if existing_params > 0:
            print(f"⚠️ {existing_params} paramètre(s) existent déjà, skip création")
            return
        
        params_data = [
            {
                'cle': 'rssi_seuil_critique',
                'valeur': str(config.SEUILS_RSSI['CRITIQUE']),
                'description': 'Seuil RSSI critique (dBm)',
                'type_donnee': 'float',
                'categorie': 'seuils'
            },
            {
                'cle': 'snr_seuil_critique',
                'valeur': str(config.SEUILS_SNR['CRITIQUE']),
                'description': 'Seuil SNR critique (dB)',
                'type_donnee': 'float',
                'categorie': 'seuils'
            },
            {
                'cle': 'ia_anomaly_threshold',
                'valeur': str(config.IA_CONFIG['anomaly_threshold']),
                'description': 'Seuil de détection d\'anomalies (écarts-types)',
                'type_donnee': 'float',
                'categorie': 'ia'
            },
            {
                'cle': 'ia_prediction_horizon',
                'valeur': str(config.IA_CONFIG['prediction_horizon']),
                'description': 'Horizon de prédiction (heures)',
                'type_donnee': 'int',
                'categorie': 'ia'
            },
            {
                'cle': 'alertes_auto_resolution',
                'valeur': 'false',
                'description': 'Résolution automatique des alertes',
                'type_donnee': 'bool',
                'categorie': 'alertes'
            },
            {
                'cle': 'system_version',
                'valeur': config.APP_VERSION,
                'description': 'Version de l\'application',
                'type_donnee': 'string',
                'categorie': 'system',
                'modifiable': False
            }
        ]
        
        for param_data in params_data:
            param = ParametresSysteme(**param_data)
            db.add(param)
        
        db.commit()
        print(f"✅ {len(params_data)} paramètres système créés")


def display_summary():
    """Affiche un résumé des données créées."""
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE L'INITIALISATION")
    print("="*60)
    
    with get_db_context() as db:
        nb_users = db.query(Utilisateur).count()
        nb_links = db.query(FHLink).count()
        nb_params = db.query(ParametresSysteme).count()
        
        print(f"\n👥 Utilisateurs créés : {nb_users}")
        for user in db.query(Utilisateur).all():
            print(f"   • {user.email} ({user.role.value})")
        
        print(f"\n📡 Liaisons FH créées : {nb_links}")
        for link in db.query(FHLink).all():
            print(f"   • {link.nom}")
        
        print(f"\n⚙️ Paramètres système : {nb_params}")
        
        print("\n" + "="*60)
        print("🔐 IDENTIFIANTS DE CONNEXION")
        print("="*60)
        print("\n Admin   : admin@netpulse.ai / admin123")
        print(" Tech    : tech@netpulse.ai / tech123")
        print(" Guest   : guest@netpulse.ai / guest123")
        
        print("\n" + "="*60)
        print("🚀 LANCEMENT DE L'APPLICATION")
        print("="*60)
        print("\n Commande : streamlit run app.py")
        print("\n" + "="*60 + "\n")


def main():
    """Fonction principale d'initialisation."""
    print("\n" + "="*60)
    print("🚀 INITIALISATION DE LA BASE DE DONNÉES NETPULSE-AI")
    print("="*60 + "\n")
    
    try:
        # 1. Créer les tables
        create_tables()
        
        # 2. Créer les utilisateurs
        create_default_users()
        
        # 3. Créer les liaisons FH
        create_default_links()
        
        # 4. Créer les paramètres système
        create_system_parameters()
        
        # 5. Afficher le résumé
        display_summary()
        
        print("✅ Initialisation terminée avec succès !\n")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
