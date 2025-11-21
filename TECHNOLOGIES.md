# Technologies et Outils Utilisés - NetPulse-AI

## 🎯 Vue d'ensemble

NetPulse-AI est une plateforme de supervision intelligente des liaisons micro-ondes FH développée avec un stack technologique moderne et robuste.

---

## 💻 Backend / Core

### Langage Principal
- **Python 3.14** - Langage de programmation principal
  - Choisi pour sa richesse en bibliothèques IA/ML
  - Syntaxe claire et productive
  - Large communauté et écosystème mature

### Base de Données
- **SQLite** - Base de données relationnelle embarquée
  - Parfait pour le prototypage et déploiement léger
  - Support transactionnel ACID
  - Pas de serveur requis
  
- **SQLAlchemy 2.0.44** - ORM (Object-Relational Mapping)
  - Abstraction élégante de la base de données
  - Gestion automatique des sessions et transactions
  - Support des relations complexes entre tables

### Sécurité
- **Bcrypt 5.0.0** - Hashing de mots de passe
  - Algorithme de hashing sécurisé avec salt
  - Protection contre les attaques par force brute
  - Standard industriel pour le stockage de mots de passe

- **Python-dotenv 1.2.1** - Gestion des variables d'environnement
  - Configuration sécurisée des secrets
  - Séparation des configurations par environnement

---

## 🎨 Frontend / Interface Utilisateur

### Framework Principal
- **Streamlit 1.50.0** - Framework d'application web en Python
  - Développement rapide d'interfaces interactives
  - Architecture multi-pages native
  - Widgets riches (forms, charts, file uploaders)
  - Rechargement à chaud pour développement agile

### Visualisation de Données
- **Plotly 6.5.0** - Bibliothèque de graphiques interactifs
  - Graphiques temps réel pour RSSI, SNR, BER
  - Interactivité (zoom, pan, hover)
  - Graphiques de corrélation (RSSI vs pluviométrie)
  - Pie charts pour distribution des alertes

- **Altair 5.5.0** - Grammaire déclarative de visualisation
  - Intégration native avec Streamlit
  - Visualisations statistiques élégantes

---

## 🤖 Intelligence Artificielle / Machine Learning

### Bibliothèque ML
- **Scikit-learn 1.7.2** - Suite complète de ML
  - **Isolation Forest** - Détection d'anomalies non supervisée
  - **Linear Regression** - Prédiction des tendances RSSI/SNR
  - **StandardScaler** - Normalisation des données
  - **Z-score analysis** - Détection de dérives statistiques

### Calcul Scientifique
- **NumPy 2.3.5** - Calcul numérique haute performance
  - Opérations vectorielles optimisées
  - Support des matrices et tableaux multidimensionnels
  
- **SciPy 1.16.3** - Algorithmes scientifiques avancés
  - Statistiques et distributions
  - Optimisation numérique

---

## 📊 Traitement de Données

### Manipulation de Données
- **Pandas 2.3.3** - Analyse et manipulation de données
  - DataFrames pour gestion des mesures KPI
  - Opérations groupées et agrégations
  - Gestion des séries temporelles
  - Import/Export CSV et Excel

- **OpenPyXL 3.1.5** - Lecture/écriture fichiers Excel
  - Support des formats .xlsx et .xls
  - Validation des données importées

### Format de Données
- **PyArrow 22.0.0** - Sérialisation de données en colonnes
  - Performance optimale pour grandes données
  - Format Apache Arrow pour échanges efficaces

---

## 🔧 Utilitaires et Support

### Gestion d'État
- **Streamlit Session State** - Gestion de l'état applicatif
  - Persistance de la session utilisateur
  - Stockage de la liaison FH active
  - Cache des données

### Logging et Monitoring
- **Python logging** - Système de journalisation intégré
  - Traçabilité des connexions utilisateurs
  - Logs d'alertes et événements système

### Validation
- **Validators personnalisés** - Validation des données importées
  - Vérification des schémas CSV/Excel
  - Contrôle de cohérence des KPI
  - Calcul de score de qualité des données

---

## 📁 Architecture et Structure

### Patterns de Conception
- **MVC (Model-View-Controller)** adapté pour Streamlit
  - **Models** : SQLAlchemy ORM (7 tables)
  - **Views** : Pages Streamlit (Dashboard, Alertes, Chatbot, Import)
  - **Controllers** : Modules backend (analytics, AI, alerts)

### Organisation Modulaire
```
netpulse-ai/
├── backend/
│   ├── database/       # Modèles et connexions DB
│   ├── security/       # Authentification et autorisation
│   ├── ingestion/      # Import et validation données
│   ├── analytics/      # Calcul KPI et statistiques
│   ├── ai_engine/      # IA (anomalies, prédictions, XAI)
│   ├── alerts/         # Génération et gestion alertes
│   └── chatbot/        # NLP et génération réponses
├── pages/              # Pages Streamlit
├── data/               # Données de test
└── config.py           # Configuration centralisée
```

---

## 🌐 Standards et Normes

### Télécommunications
- **Normes ITU-R** - Seuils RSSI pour liaisons FH
  - Excellent : > -50 dBm
  - Bon : -50 à -60 dBm
  - Moyen : -60 à -70 dBm
  - Critique : < -75 dBm

- **Normes ETSI** - Seuils SNR pour QoS
  - Excellent : > 30 dB
  - Bon : 20-30 dB
  - Acceptable : 15-20 dB
  - Critique : < 10 dB

### Code Quality
- **PEP 8** - Style guide Python officiel
  - Conventions de nommage
  - Indentation et formatage
  - Docstrings pour toutes les fonctions

---

## 🚀 Déploiement et Environnement

### Environnement de Développement
- **Visual Studio Code** - IDE principal
- **Git** - Contrôle de version
- **Virtual Environment (venv)** - Isolation des dépendances

### Gestion des Dépendances
- **pip** - Gestionnaire de packages Python
- **requirements.txt** - Liste des dépendances versionnées

### Exécution
```bash
# Installation
pip install -r requirements.txt

# Initialisation DB
python backend/database/init_db.py

# Lancement
streamlit run app.py
```

---

## 📈 Performance et Optimisation

### Optimisations Appliquées
- **Context Managers** pour gestion des sessions DB
- **Lazy Loading** des données volumineuses
- **Caching Streamlit** pour requêtes répétitives
- **Extraction des données** hors contexte DB pour éviter DetachedInstanceError

### Scalabilité
- Architecture modulaire permettant migration vers PostgreSQL/MySQL
- Séparation backend/frontend facilitant déploiement distribué
- API-ready pour intégration avec NMS externes

---

## 🔐 Sécurité

### Mesures Implémentées
- Hashing bcrypt des mots de passe (12 rounds)
- Gestion des rôles (ADMIN, TECH, GUEST)
- Permissions granulaires par action
- Logs de connexion et traçabilité
- Variables d'environnement pour secrets
- Protection CSRF via Streamlit

---

## 📚 Documentation Technique

### Ressources
- **SQLAlchemy Docs** : https://docs.sqlalchemy.org/
- **Streamlit Docs** : https://docs.streamlit.io/
- **Scikit-learn Docs** : https://scikit-learn.org/
- **Plotly Docs** : https://plotly.com/python/

### Normes Référencées
- ITU-R F.746 - Fixed service systems
- ETSI EN 302 217 - Fixed Radio Systems
- IEEE 802.11 - Wireless LAN standards

---

**Version:** 1.0.0  
**Date:** Novembre 2025  
**Auteur:** Projet NetPulse-AI
