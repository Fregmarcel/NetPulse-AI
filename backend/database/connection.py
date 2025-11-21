"""
Gestion des connexions à la base de données.
Fournit des fonctions pour créer et gérer les sessions SQLAlchemy.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import config

# Création de l'engine SQLAlchemy
# Pour SQLite, on utilise check_same_thread=False pour permettre l'accès multi-thread
engine = create_engine(
    config.DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in config.DATABASE_URL else {},
    poolclass=StaticPool if 'sqlite' in config.DATABASE_URL else None,
    echo=config.ENVIRONMENT == 'development'
)

# Factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Session thread-safe pour l'application
ScopedSession = scoped_session(SessionLocal)


def get_db():
    """
    Générateur de session de base de données.
    Utiliser avec FastAPI ou dans un contexte asynchrone.
    
    Yields:
        Session: Session SQLAlchemy
        
    Example:
        db = next(get_db())
        try:
            # Utiliser db
            pass
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager pour la gestion de session de base de données.
    Ferme automatiquement la session après utilisation.
    
    Yields:
        Session: Session SQLAlchemy
        
    Example:
        with get_db_context() as db:
            user = db.query(Utilisateur).first()
            print(user)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_scoped_session():
    """
    Retourne une session thread-safe.
    Utiliser dans les applications multi-thread comme Streamlit.
    
    Returns:
        Session: Session SQLAlchemy thread-safe
        
    Example:
        session = get_scoped_session()
        users = session.query(Utilisateur).all()
    """
    return ScopedSession()


def close_scoped_session():
    """
    Ferme la session thread-safe actuelle.
    À appeler après utilisation de get_scoped_session().
    """
    ScopedSession.remove()


def init_database():
    """
    Initialise la base de données en créant toutes les tables.
    À appeler au démarrage de l'application.
    """
    from backend.database.models import Base
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de données initialisée : {config.DATABASE_URL}")


def drop_all_tables():
    """
    Supprime toutes les tables de la base de données.
    ATTENTION : Utiliser uniquement en développement !
    """
    from backend.database.models import Base
    if config.ENVIRONMENT != 'production':
        Base.metadata.drop_all(bind=engine)
        print("⚠️ Toutes les tables ont été supprimées")
    else:
        raise PermissionError("Impossible de supprimer les tables en production !")


def check_database_connection():
    """
    Vérifie que la connexion à la base de données fonctionne.
    
    Returns:
        bool: True si la connexion est OK, False sinon
    """
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données : {e}")
        return False
