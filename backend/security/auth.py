"""
Module d'authentification et de gestion des utilisateurs.
Gère le hashing des mots de passe et l'authentification.
"""
import bcrypt
from datetime import datetime
from typing import Tuple, Optional
from backend.database.models import Utilisateur, TraceConnexion
from backend.database.connection import get_db_context


def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.
    
    Args:
        password (str): Mot de passe en clair
        
    Returns:
        str: Hash du mot de passe
        
    Example:
        >>> hashed = hash_password("monmotdepasse123")
        >>> print(len(hashed))
        60
    """
    # Générer un salt et hasher le mot de passe
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash.
    
    Args:
        password (str): Mot de passe en clair à vérifier
        password_hash (str): Hash du mot de passe stocké
        
    Returns:
        bool: True si le mot de passe correspond, False sinon
        
    Example:
        >>> hashed = hash_password("test123")
        >>> verify_password("test123", hashed)
        True
        >>> verify_password("wrong", hashed)
        False
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception as e:
        print(f"Erreur lors de la vérification du mot de passe : {e}")
        return False


def authenticate_user(email: str, password: str, ip_address: str = None) -> Tuple[Optional[dict], bool, str]:
    """
    Authentifie un utilisateur avec son email et mot de passe.
    Enregistre la tentative de connexion dans les traces.
    
    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe en clair
        ip_address (str, optional): Adresse IP de l'utilisateur
        
    Returns:
        Tuple[Optional[dict], bool, str]: 
            - Dictionnaire avec données utilisateur si authentification réussie, None sinon
            - Bool indiquant le succès
            - Message de résultat
            
    Example:
        >>> user_data, success, message = authenticate_user("admin@netpulse.ai", "admin123")
        >>> if success:
        ...     print(f"Connecté en tant que {user_data['email']}")
    """
    with get_db_context() as db:
        # Rechercher l'utilisateur par email
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        
        if not user:
            # Utilisateur non trouvé
            log_connexion(
                None, ip_address, "LOGIN_FAILED",
                False, f"Email non trouvé : {email}"
            )
            return None, False, "Email ou mot de passe incorrect"
        
        # Vérifier si l'utilisateur est actif
        if not user.actif:
            log_connexion(
                user.id, ip_address, "LOGIN_FAILED",
                False, "Compte désactivé"
            )
            return None, False, "Compte désactivé. Contactez l'administrateur."
        
        # Vérifier le mot de passe
        if not verify_password(password, user.password_hash):
            log_connexion(
                user.id, ip_address, "LOGIN_FAILED",
                False, "Mot de passe incorrect"
            )
            return None, False, "Email ou mot de passe incorrect"
        
        # Authentification réussie - extraire les données pendant que la session est active
        user_data = {
            'id': user.id,
            'email': user.email,
            'nom_complet': user.nom_complet,
            'role': user.role,
            'actif': user.actif
        }
        
        log_connexion(
            user.id, ip_address, "LOGIN_SUCCESS",
            True, f"Connexion réussie pour {user.email}"
        )
        
        return user_data, True, f"Bienvenue {user.nom_complet or user.email} !"


def log_connexion(
    utilisateur_id: Optional[int],
    ip_address: Optional[str],
    action: str,
    success: bool,
    details: Optional[str] = None
):
    """
    Enregistre une trace de connexion ou d'action utilisateur.
    
    Args:
        utilisateur_id (int, optional): ID de l'utilisateur
        ip_address (str, optional): Adresse IP
        action (str): Action effectuée (LOGIN_SUCCESS, LOGIN_FAILED, etc.)
        success (bool): Succès de l'action
        details (str, optional): Détails supplémentaires
    """
    try:
        with get_db_context() as db:
            trace = TraceConnexion(
                utilisateur_id=utilisateur_id,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                action=action,
                success=success,
                details=details
            )
            db.add(trace)
            db.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la trace : {e}")


def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Change le mot de passe d'un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
        old_password (str): Ancien mot de passe
        new_password (str): Nouveau mot de passe
        
    Returns:
        Tuple[bool, str]: (Succès, Message)
    """
    with get_db_context() as db:
        user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
        
        if not user:
            return False, "Utilisateur non trouvé"
        
        # Vérifier l'ancien mot de passe
        if not verify_password(old_password, user.password_hash):
            log_connexion(user_id, None, "PASSWORD_CHANGE_FAILED", False, "Ancien mot de passe incorrect")
            return False, "Ancien mot de passe incorrect"
        
        # Valider le nouveau mot de passe
        if len(new_password) < 6:
            return False, "Le nouveau mot de passe doit contenir au moins 6 caractères"
        
        # Mettre à jour le mot de passe
        user.password_hash = hash_password(new_password)
        db.commit()
        
        log_connexion(user_id, None, "PASSWORD_CHANGED", True, "Mot de passe changé avec succès")
        return True, "Mot de passe changé avec succès"


def check_permission(user, required_permissions: list) -> bool:
    """
    Vérifie si un utilisateur a les permissions requises.
    
    Args:
        user: Objet Utilisateur ou dictionnaire avec données utilisateur
        required_permissions (list): Liste des permissions requises
        
    Returns:
        bool: True si l'utilisateur a les permissions, False sinon
    """
    import config
    
    if not user:
        return False
    
    # Support pour dictionnaire (données de session) ou objet SQLAlchemy
    if isinstance(user, dict):
        if not user.get('actif', True):  # Par défaut True si pas dans le dict
            return False
        role_value = user['role'].value if hasattr(user['role'], 'value') else user['role']
    else:
        if not user.actif:
            return False
        role_value = user.role.value
    
    user_permissions = config.USER_ROLES.get(role_value, {}).get('permissions', [])
    
    # Si l'utilisateur a la permission 'all', il a toutes les permissions
    if 'all' in user_permissions:
        return True
    
    # Vérifier si toutes les permissions requises sont présentes
    return all(perm in user_permissions for perm in required_permissions)


def get_user_by_id(user_id: int) -> Optional[Utilisateur]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        user_id (int): ID de l'utilisateur
        
    Returns:
        Optional[Utilisateur]: Utilisateur ou None
    """
    with get_db_context() as db:
        return db.query(Utilisateur).filter(Utilisateur.id == user_id).first()


def get_user_by_email(email: str) -> Optional[Utilisateur]:
    """
    Récupère un utilisateur par son email.
    
    Args:
        email (str): Email de l'utilisateur
        
    Returns:
        Optional[Utilisateur]: Utilisateur ou None
    """
    with get_db_context() as db:
        return db.query(Utilisateur).filter(Utilisateur.email == email).first()


def get_recent_connexions(user_id: int, limit: int = 10) -> list:
    """
    Récupère les dernières connexions d'un utilisateur.
    
    Args:
        user_id (int): ID de l'utilisateur
        limit (int): Nombre maximum de connexions à récupérer
        
    Returns:
        list: Liste des traces de connexion
    """
    with get_db_context() as db:
        return (
            db.query(TraceConnexion)
            .filter(TraceConnexion.utilisateur_id == user_id)
            .order_by(TraceConnexion.timestamp.desc())
            .limit(limit)
            .all()
        )
