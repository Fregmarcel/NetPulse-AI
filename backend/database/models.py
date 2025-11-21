"""
Modèles de base de données SQLAlchemy pour NetPulse-AI.
Définit les 7 tables principales de l'application.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    """Énumération des rôles utilisateur."""
    ADMIN = "ADMIN"
    TECH = "TECH"
    GUEST = "GUEST"


class Utilisateur(Base):
    """Table des utilisateurs de l'application."""
    __tablename__ = 'utilisateurs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.GUEST)
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)
    nom_complet = Column(String(255))
    actif = Column(Boolean, default=True, nullable=False)
    
    # Relations
    traces = relationship("TraceConnexion", back_populates="utilisateur", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Utilisateur(id={self.id}, email='{self.email}', role={self.role.value})>"


class FHLink(Base):
    """Table des liaisons micro-ondes FH."""
    __tablename__ = 'fh_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(255), unique=True, nullable=False, index=True)
    site_a = Column(String(255), nullable=False)
    site_b = Column(String(255), nullable=False)
    frequence_ghz = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    latitude_a = Column(Float)
    longitude_a = Column(Float)
    latitude_b = Column(Float)
    longitude_b = Column(Float)
    date_installation = Column(DateTime, default=datetime.utcnow)
    actif = Column(Boolean, default=True, nullable=False)
    description = Column(Text)
    
    # Relations
    mesures = relationship("MesureKPI", back_populates="link", cascade="all, delete-orphan")
    syntheses = relationship("KPISynthese", back_populates="link", cascade="all, delete-orphan")
    alertes = relationship("Alerte", back_populates="link", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FHLink(id={self.id}, nom='{self.nom}', {self.site_a} <-> {self.site_b})>"


class MesureKPI(Base):
    """Table des mesures KPI en temps réel."""
    __tablename__ = 'mesures_kpi'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey('fh_links.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    rssi_dbm = Column(Float, nullable=False)
    snr_db = Column(Float, nullable=False)
    ber = Column(Float, nullable=False)
    acm_modulation = Column(String(50), nullable=False)
    latency_ms = Column(Float)
    packet_loss = Column(Float)
    rainfall_mm = Column(Float, default=0.0)
    temperature_c = Column(Float)
    
    # Relations
    link = relationship("FHLink", back_populates="mesures")
    
    def __repr__(self):
        return f"<MesureKPI(id={self.id}, link_id={self.link_id}, timestamp={self.timestamp})>"


class KPISynthese(Base):
    """Table des synthèses KPI journalières."""
    __tablename__ = 'kpi_syntheses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey('fh_links.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    rssi_avg = Column(Float)
    rssi_min = Column(Float)
    rssi_max = Column(Float)
    snr_avg = Column(Float)
    snr_min = Column(Float)
    snr_max = Column(Float)
    ber_avg = Column(Float)
    ber_max = Column(Float)
    disponibilite = Column(Float)  # Pourcentage
    etat_global = Column(String(50))  # NORMAL, DEGRADED, CRITIQUE
    nb_mesures = Column(Integer, default=0)
    nb_alertes = Column(Integer, default=0)
    
    # Relations
    link = relationship("FHLink", back_populates="syntheses")
    
    def __repr__(self):
        return f"<KPISynthese(id={self.id}, link_id={self.link_id}, date={self.date}, etat={self.etat_global})>"


class Alerte(Base):
    """Table des alertes système."""
    __tablename__ = 'alertes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey('fh_links.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    type = Column(String(100), nullable=False)
    severite = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    recommandation = Column(Text)
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(255))
    valeur_mesuree = Column(Float)
    seuil_declenche = Column(Float)
    ia_generated = Column(Boolean, default=False)
    
    # Relations
    link = relationship("FHLink", back_populates="alertes")
    
    def __repr__(self):
        status = "Résolue" if self.resolved else "Active"
        return f"<Alerte(id={self.id}, type='{self.type}', severite='{self.severite}', status='{status}')>"


class TraceConnexion(Base):
    """Table des traces de connexion et actions utilisateur."""
    __tablename__ = 'traces_connexion'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateurs.id', ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45))  # Support IPv4 et IPv6
    action = Column(String(255), nullable=False)
    success = Column(Boolean, nullable=False)
    details = Column(Text)
    user_agent = Column(String(500))
    
    # Relations
    utilisateur = relationship("Utilisateur", back_populates="traces")
    
    def __repr__(self):
        status = "Succès" if self.success else "Échec"
        return f"<TraceConnexion(id={self.id}, utilisateur_id={self.utilisateur_id}, action='{self.action}', status='{status}')>"


class ParametresSysteme(Base):
    """Table des paramètres système configurables."""
    __tablename__ = 'parametres_systeme'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cle = Column(String(255), unique=True, nullable=False, index=True)
    valeur = Column(Text, nullable=False)
    description = Column(Text)
    type_donnee = Column(String(50), default='string')  # string, int, float, bool, json
    categorie = Column(String(100))  # seuils, ia, alertes, system
    modifiable = Column(Boolean, default=True)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ParametresSysteme(id={self.id}, cle='{self.cle}', valeur='{self.valeur}')>"
