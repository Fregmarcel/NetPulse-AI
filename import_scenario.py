"""
Script pour importer les données de scénario de dégradation.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from backend.ingestion.csv_parser import parse_uploaded_file
from backend.ingestion.data_loader import load_measures_to_db
import pandas as pd

def import_scenario_data():
    """Importe les données de scénario dans la base."""
    
    print("=" * 70)
    print("📥 IMPORT DES DONNÉES DE SCÉNARIO")
    print("=" * 70)
    print()
    
    # Chemin du fichier
    csv_file = root_dir / "data" / "scenario_degradation.csv"
    
    if not csv_file.exists():
        print(f"❌ Fichier non trouvé : {csv_file}")
        return
    
    print(f"📂 Lecture du fichier : {csv_file}")
    
    # Lire le CSV
    try:
        with open(csv_file, 'rb') as f:
            df, success, message = parse_uploaded_file(f)
        
        if not success:
            print(f"❌ Erreur de parsing : {message}")
            return
        
        print(f"✅ {message}")
        print(f"📊 Lignes lues : {len(df)}")
        print()
        
        # Afficher un aperçu
        print("📋 Aperçu des données :")
        print(df.head(10).to_string())
        print()
        
        # Importer dans la base
        print("💾 Import dans la base de données...")
        success, stats = load_measures_to_db(df)
        
        if success:
            print()
            print("✅ IMPORT RÉUSSI !")
            print(f"   • Total : {stats['total']}")
            print(f"   • Importées : {stats['imported']}")
            print(f"   • Ignorées : {stats['skipped']}")
            print(f"   • Erreurs : {stats['errors']}")
            
            if stats['duplicates'] > 0:
                print(f"   • Doublons : {stats['duplicates']}")
        else:
            print(f"❌ Erreur lors de l'import : {stats}")
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import_scenario_data()
