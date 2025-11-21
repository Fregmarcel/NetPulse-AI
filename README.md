# 📡 NetPulse-AI

**Plateforme de Supervision Intelligente des Liaisons Micro-ondes FH**

NetPulse-AI est une solution complète de monitoring en temps réel des liaisons hertziennes (FH - Faisceaux Hertziens) avec intelligence artificielle pour la détection d'anomalies et la prédiction de pannes.

---

## ✨ Fonctionnalités

### 🎯 Supervision en Temps Réel
- **Dashboard interactif** avec graphiques Plotly (RSSI, SNR, BER)
- **Métriques temps réel** : RSSI, SNR, BER, ACM, latence, perte de paquets
- **Analyse de corrélation** pluie vs performances
- **Code couleur** selon seuils ITU/ETSI

### 🚨 Système d'Alertes Intelligent
- **7 niveaux de sévérité** (CRITIQUE, MAJEURE, MINEURE, WARNING, INFO, PREDICTIVE, SECURITY)
- **Détection automatique** des dégradations
- **Gestion des alertes** : résolution, suppression, filtrage
- **Historique complet** avec recommandations

### 🤖 Intelligence Artificielle
- **Détection d'anomalies** par Z-score et analyse statistique
- **Prédictions** à 2h avec régression linéaire
- **Analyse de tendances** et patterns
- **Explications** des prédictions IA

### 💬 Chatbot Assistant
- **Reconnaissance d'intention** par NLP simple
- **Réponses contextuelles** sur état, alertes, métriques
- **Recommandations personnalisées**
- **Interface conversationnelle** intuitive

### 📤 Import de Données
- **Support CSV/Excel** avec validation
- **Vérification de schéma** et plages de valeurs
- **Gestion des doublons**
- **Statistiques d'import** détaillées

### 🔐 Sécurité
- **Authentification** par email/mot de passe
- **Hashing bcrypt** des mots de passe
- **3 rôles utilisateurs** (ADMIN, TECH, GUEST)
- **Traçabilité** des connexions et actions

---

## 🚀 Installation

### Prérequis
- Python 3.9+
- pip

### Étapes

```bash
# 1. Aller dans le dossier
cd netpulse-ai

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Initialiser la base de données
python backend/database/init_db.py

# 6. Lancer l'application
streamlit run app.py
```

L'application sera accessible sur **http://localhost:8501**

---

## 🔑 Identifiants de Test

| Rôle | Email | Mot de passe | Permissions |
|------|-------|--------------|-------------|
| **Admin** | admin@netpulse.ai | admin123 | Toutes |
| **Tech** | tech@netpulse.ai | tech123 | Vue, résolution alertes, export |
| **Guest** | guest@netpulse.ai | guest123 | Lecture seule |

---

## 📊 Base de Données

### 7 Tables SQLAlchemy

1. **Utilisateur** : Comptes utilisateurs avec rôles
2. **FHLink** : Liaisons micro-ondes FH
3. **MesureKPI** : Mesures temps réel (RSSI, SNR, BER, etc.)
4. **KPISynthese** : Synthèses journalières
5. **Alerte** : Alertes système
6. **TraceConnexion** : Logs de connexion
7. **ParametresSysteme** : Configuration système

### Seuils ITU/ETSI

| Métrique | Excellent | Bon | Acceptable | Dégradé | Critique |
|----------|-----------|-----|------------|---------|----------|
| **RSSI (dBm)** | ≥ -50 | ≥ -60 | ≥ -70 | ≥ -75 | < -75 |
| **SNR (dB)** | ≥ 30 | ≥ 20 | ≥ 15 | ≥ 10 | < 10 |
| **BER** | ≤ 1e-9 | ≤ 1e-7 | ≤ 1e-6 | ≤ 1e-5 | > 1e-5 |

---

## 💻 Stack Technique

- **Frontend** : Streamlit 1.31.0
- **Backend** : Python 3.9+
- **Base de données** : SQLite (SQLAlchemy 2.0.25)
- **ML/IA** : Scikit-learn 1.4.0
- **Visualisation** : Plotly 5.18.0
- **Traitement données** : Pandas 2.2.0, NumPy 1.26.3
- **Sécurité** : Bcrypt 4.1.2

---

## 📖 Utilisation

### 1. Import de Données

1. Se connecter en tant qu'**Admin**
2. Aller sur la page **📤 Import**
3. Uploader le fichier **data/sample_fh_data.csv** (100 lignes fournies)
4. Valider et importer

### 2. Supervision

1. Sélectionner une liaison dans la sidebar
2. Consulter le **Dashboard** pour les graphiques
3. Vérifier les **Alertes** actives
4. Analyser les tendances

### 3. Chatbot

Exemples de questions :
- "Quel est l'état de la liaison ?"
- "Affiche les alertes actives"
- "Donne les métriques RSSI et SNR"
- "Quelles sont les recommandations ?"
- "Prévisions pour les 2 prochaines heures"

---

## 📄 Licence

© 2025 NetPulse-AI - Tous droits réservés

---

**Version** : 1.0.0  
**Date** : Novembre 2025

**NetPulse-AI** - *Intelligence artificielle au service des télécommunications*
