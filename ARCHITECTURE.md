# 🏗️ ARCHITECTURE NETPULSE-AI

## 📐 Vue d'ensemble

**NetPulse-AI** est une application full-stack de monitoring de liaisons micro-ondes FH (Faisceaux Hertziens) avec intelligence artificielle.

### Stack technologique
- **Backend** : Python 3.11.9
- **Frontend** : Streamlit 1.51.0 (multi-pages)
- **Base de données** : MySQL 8.4.3 (Laragon)
- **ORM** : SQLAlchemy 2.0.44 + PyMySQL 1.1.2
- **ML/IA** : Scikit-learn 1.7.2 (Isolation Forest, Linear Regression)
- **Visualisation** : Plotly 6.5.0, Altair 5.5.0

---

## 📁 Structure des fichiers

```
netpulse-ai/
│
├── 🏠 RACINE
│   ├── app.py                      # Point d'entrée principal Streamlit
│   ├── config.py                   # Configuration globale (seuils ITU/ETSI)
│   ├── .env                        # Variables d'environnement (DATABASE_URL)
│   ├── requirements.txt            # Dépendances Python
│   └── README.md                   # Documentation utilisateur
│
├── 📄 PAGES STREAMLIT (pages/)
│   ├── 1_📊_Dashboard.py           # Visualisation KPI temps réel
│   ├── 2_🚨_Alertes.py             # Gestion alertes système
│   ├── 3_💬_Chatbot.py             # Assistant IA conversationnel
│   └── 4_📤_Import.py              # Import CSV/Excel
│
├── ⚙️ BACKEND (backend/)
│   │
│   ├── 🗄️ database/
│   │   ├── connection.py           # Gestionnaire connexion MySQL
│   │   └── models.py               # 7 modèles SQLAlchemy ORM
│   │
│   ├── 🔐 security/
│   │   └── auth.py                 # Authentification bcrypt, gestion rôles
│   │
│   ├── 📊 analytics/
│   │   ├── kpi_calculator.py       # Calculs KPI (RSSI, SNR, BER, disponibilité)
│   │   └── trend_analyzer.py       # Analyse tendances, corrélations
│   │
│   ├── 🤖 ai_engine/
│   │   ├── anomaly_detector.py     # Détection anomalies (Z-score, Isolation Forest)
│   │   └── predictor.py            # Prédictions ML (Linear Regression)
│   │
│   ├── 🚨 alerts/
│   │   └── alert_engine.py         # Moteur alertes, vérification seuils
│   │
│   ├── 💬 chatbot/
│   │   ├── intent_recognizer.py    # Reconnaissance intention NLP
│   │   └── response_generator.py   # Génération réponses XAI
│   │
│   └── 📥 ingestion/
│       └── data_loader.py          # Import CSV/Excel, validation schéma
│
├── 📊 DATA (data/)
│   └── scenario_*.csv              # Fichiers CSV de test
│
├── 🧪 TESTS (tests/)
│   └── test_*.py                   # Tests unitaires
│
└── 🐍 ENVIRONNEMENT
    ├── venv311/                    # Environnement Python 3.11
    ├── setup_venv_py311.ps1        # Script installation automatique
    └── test_mysql.py               # Script test connexion DB
```

---

## 🗄️ SCHÉMA BASE DE DONNÉES

### Table `utilisateurs`
```sql
CREATE TABLE utilisateurs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'TECH', 'GUEST') DEFAULT 'GUEST',
    nom_complet VARCHAR(255),
    actif BOOLEAN DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Rôles** :
- **ADMIN** : Accès complet (Dashboard, Alertes, Chatbot, Import)
- **TECH** : Supervision (Dashboard, Alertes, Chatbot)
- **GUEST** : Lecture seule (Dashboard uniquement)

### Table `fh_links`
```sql
CREATE TABLE fh_links (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) UNIQUE NOT NULL,
    site_a VARCHAR(255) NOT NULL,
    site_b VARCHAR(255) NOT NULL,
    frequence_ghz FLOAT NOT NULL,
    distance_km FLOAT NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Exemple** : "Siège CNPS - Datacenter Kennedy" (23 GHz, 12.5 km)

### Table `mesures_kpi`
```sql
CREATE TABLE mesures_kpi (
    id INT PRIMARY KEY AUTO_INCREMENT,
    link_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    rssi_dbm FLOAT NOT NULL,
    snr_db FLOAT NOT NULL,
    ber FLOAT NOT NULL,
    acm_modulation VARCHAR(50),
    rainfall_mm FLOAT DEFAULT 0,
    latency_ms FLOAT DEFAULT 0,
    packet_loss FLOAT DEFAULT 0,
    FOREIGN KEY (link_id) REFERENCES fh_links(id),
    UNIQUE KEY idx_link_timestamp (link_id, timestamp)
);
```

**Métriques clés** :
- `rssi_dbm` : Received Signal Strength Indicator (dBm)
- `snr_db` : Signal-to-Noise Ratio (dB)
- `ber` : Bit Error Rate (sans unité, ex: 1e-8)
- `acm_modulation` : Adaptive Coding Modulation (64QAM, 32QAM, 16QAM)

### Table `alertes`
```sql
CREATE TABLE alertes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    link_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    type VARCHAR(100) NOT NULL,
    severite ENUM('CRITIQUE', 'MAJEURE', 'MINEURE', 'WARNING', 'INFO', 'PREDICTIVE', 'SECURITY'),
    message TEXT NOT NULL,
    recommandation TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    valeur_mesuree FLOAT,
    seuil_declenche FLOAT,
    ia_generated BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolved_by VARCHAR(255),
    FOREIGN KEY (link_id) REFERENCES fh_links(id)
);
```

**Types d'alertes** :
- `RSSI_DEGRADED`, `RSSI_CRITICAL` : Puissance signal faible
- `SNR_LOW`, `SNR_CRITICAL` : Bruit élevé
- `BER_HIGH`, `BER_UNACCEPTABLE` : Taux d'erreur élevé
- `LATENCY_HIGH` : Latence anormale
- `PACKET_LOSS_HIGH` : Perte de paquets
- `ANOMALY_DETECTED` : Anomalie détectée par IA
- `PREDICTION_DEGRADATION` : Prédiction de panne

### Table `kpi_syntheses`
```sql
CREATE TABLE kpi_syntheses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    link_id INT NOT NULL,
    date DATE NOT NULL,
    rssi_avg FLOAT,
    rssi_min FLOAT,
    rssi_max FLOAT,
    snr_avg FLOAT,
    snr_min FLOAT,
    snr_max FLOAT,
    ber_avg FLOAT,
    ber_max FLOAT,
    disponibilite FLOAT,
    etat_global VARCHAR(50),
    nb_alertes INT DEFAULT 0,
    FOREIGN KEY (link_id) REFERENCES fh_links(id),
    UNIQUE KEY idx_link_date (link_id, date)
);
```

**Usage** : Synthèse journalière automatique, historique long terme

### Table `traces_connexion`
```sql
CREATE TABLE traces_connexion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    action VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
);
```

**Usage** : Audit sécurité, traçabilité actions

### Table `parametres_systeme`
```sql
CREATE TABLE parametres_systeme (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cle VARCHAR(255) UNIQUE NOT NULL,
    valeur TEXT,
    description TEXT,
    type_valeur VARCHAR(50),
    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Usage** : Configuration dynamique, seuils personnalisables

---

## 🔄 FLUX DE DONNÉES

### 1. Authentification
```
[Utilisateur] → app.py → backend/security/auth.py
                              ↓
                       authenticate_user()
                              ↓
                     Vérification bcrypt
                              ↓
                    Session Streamlit créée
                              ↓
              st.session_state['authenticated'] = True
              st.session_state['user'] = User object
```

### 2. Dashboard - Affichage métriques
```
[Dashboard.py] → get_latest_kpis(link_id)
                        ↓
                backend/analytics/kpi_calculator.py
                        ↓
               Query: SELECT * FROM mesures_kpi 
                      WHERE link_id = ? 
                      ORDER BY timestamp DESC LIMIT 1
                        ↓
               calculate_link_status(rssi, snr, ber)
                        ↓
               Return: {'rssi_dbm': -65, 'etat_global': 'DEGRADED', ...}
                        ↓
                [Affichage Streamlit]
```

### 3. Dashboard - Graphiques avec filtre période
```
[Dashboard.py] → Utilisateur sélectionne "12 heures"
                        ↓
              date_from = utcnow() - timedelta(hours=12)
                        ↓
              Query: SELECT * FROM mesures_kpi 
                     WHERE link_id = ? AND timestamp >= ?
                     ORDER BY timestamp
                        ↓
              Conversion en dictionnaires (dans session DB)
                        ↓
              DataFrame pandas → Plotly graphs
```

### 4. Alertes - Vérification automatique
```
[Alertes.py] → Clic "Vérifier Alertes"
                        ↓
              backend/alerts/alert_engine.py
                        ↓
              check_and_create_alerts(link_id)
                        ↓
              Récupération dernière mesure KPI
                        ↓
              Si RSSI < -75 dBm → create_alert('RSSI_CRITICAL')
              Si SNR < 12 dB → create_alert('SNR_LOW')
              Si BER > 1e-5 → create_alert('BER_HIGH')
                        ↓
              INSERT INTO alertes (...)
                        ↓
              Return: [Liste nouvelles alertes]
```

### 5. Chatbot - Réponse XAI
```
[Chatbot.py] → Utilisateur tape "Quel est l'état de la liaison ?"
                        ↓
              backend/chatbot/intent_recognizer.py
                        ↓
              recognize_intent(message) → 'link_status'
                        ↓
              backend/chatbot/response_generator.py
                        ↓
              get_link_status_response(link_id)
                        ↓
              ┌─────────────────────────────────┐
              │ 1. get_latest_kpis(link_id)     │
              │ 2. calculate_period_statistics() │
              │ 3. get_active_alerts(link_id)   │
              │ 4. detect_anomalies_zscore()    │
              │ 5. predict_next_values()        │
              └─────────────────────────────────┘
                        ↓
              Génération réponse formatée avec :
              - Métriques actuelles
              - Statistiques 24h
              - Diagnostic IA (cause + confiance)
              - Recommandations ITU
              - Prédictions 2h
                        ↓
              Return: Texte formaté markdown
                        ↓
              [Affichage bulle chatbot]
```

### 6. Import - CSV vers DB
```
[Import.py] → Upload CSV file
                        ↓
              backend/ingestion/data_loader.py
                        ↓
              validate_csv_schema(df)
                        ↓
              Si colonnes manquantes → Erreur
              Si OK → load_measures_from_dataframe(df, link_id)
                        ↓
              Pour chaque ligne :
                  ├─ Vérifier doublon (link_id + timestamp)
                  ├─ Si nouveau → INSERT INTO mesures_kpi
                  └─ Si doublon → Ignorer
                        ↓
              Return: (nb_importées, nb_doublons)
                        ↓
              [Affichage statistiques]
```

---

## 🤖 INTELLIGENCE ARTIFICIELLE

### 1. Détection d'anomalies (Z-score)

**Fichier** : `backend/ai_engine/anomaly_detector.py`

**Algorithme** :
```python
# 1. Récupérer mesures des 48h
measures = query(MesureKPI).filter(timestamp >= date_from).all()
values = [m.rssi_dbm for m in measures]

# 2. Calculer Z-score
mean = np.mean(values)
std = np.std(values)
z_scores = [(v - mean) / std for v in values]

# 3. Détecter anomalies (|z| > 3)
anomalies = [m for i, m in enumerate(measures) if abs(z_scores[i]) > 3]
```

**Seuil** : 3 écarts-types (config `IA_CONFIG['anomaly_threshold']`)

### 2. Prédictions (Régression linéaire)

**Fichier** : `backend/ai_engine/predictor.py`

**Algorithme** :
```python
from sklearn.linear_model import LinearRegression

# 1. Données d'entraînement (48h)
X = [[i] for i in range(len(measures))]  # Index temporel
y = [m.rssi_dbm for m in measures]       # Valeurs RSSI

# 2. Entraînement
model = LinearRegression()
model.fit(X, y)

# 3. Prédiction 2h (8 points à 15 min)
future_X = [[len(measures) + i] for i in range(8)]
predictions = model.predict(future_X)

# 4. Calcul confiance (R² score)
r2 = model.score(X, y)
confidence = max(0, min(100, r2 * 100))
```

**Horizon** : 2 heures (configurable dans `config.IA_CONFIG`)

### 3. Détection chutes brutales

**Fichier** : `backend/ai_engine/anomaly_detector.py`

**Algorithme** :
```python
drops = []
for i in range(1, len(measures)):
    delta = measures[i].rssi_dbm - measures[i-1].rssi_dbm
    if delta < -10:  # Chute > 10 dBm
        drops.append({
            'timestamp': measures[i].timestamp,
            'drop': delta,
            'from': measures[i-1].rssi_dbm,
            'to': measures[i].rssi_dbm
        })
```

**Usage** : Détection coupures, interférences

### 4. Analyse corrélation pluie-RSSI

**Fichier** : `backend/analytics/trend_analyzer.py`

**Algorithme** :
```python
import pandas as pd

# 1. Créer DataFrame
df = pd.DataFrame([{
    'rssi': m.rssi_dbm,
    'rain': m.rainfall_mm
} for m in measures])

# 2. Calcul corrélation Pearson
correlation = df['rssi'].corr(df['rain'])

# 3. Interprétation
if correlation < -0.7:
    strength = "forte corrélation négative"
elif correlation < -0.4:
    strength = "corrélation modérée"
else:
    strength = "faible corrélation"
```

**Référence ITU** : ITU-R P.530 (atténuation par précipitations)

---

## 🔐 SÉCURITÉ

### 1. Authentification
- **Hashing** : bcrypt (12 rounds, salt automatique)
- **Session** : Streamlit `st.session_state` (côté serveur)
- **Timeout** : 3600 secondes (1h, configurable)

### 2. Contrôle d'accès (RBAC)

**Fichier** : `backend/security/auth.py`

```python
ROLE_PERMISSIONS = {
    'ADMIN': ['all'],
    'TECH': ['view', 'resolve_alerts', 'chat'],
    'GUEST': ['view']
}

def check_permission(user, required_permissions):
    if user.role == 'ADMIN':
        return True
    return any(perm in ROLE_PERMISSIONS[user.role] for perm in required_permissions)
```

**Usage dans pages** :
```python
# Import.py (ligne 19)
if st.session_state.user.role != 'ADMIN':
    st.error("❌ Accès refusé - Réservé aux administrateurs")
    st.stop()
```

### 3. Validation données
- **Schema CSV** : Colonnes obligatoires vérifiées
- **Plages valeurs** : Respect limites physiques ITU
- **SQL Injection** : Protection par SQLAlchemy ORM (paramétrage automatique)

---

## 📊 SEUILS ITU/ETSI

**Fichier** : `config.py`

### RSSI (Received Signal Strength Indicator)
```python
SEUILS_RSSI = {
    'EXCELLENT': -50,   # > -50 dBm : Signal très fort
    'BON': -60,         # -50 à -60 : Signal fort
    'ACCEPTABLE': -70,  # -60 à -70 : Signal correct
    'DEGRADED': -75,    # -70 à -75 : Signal faible
    'CRITIQUE': -80     # < -80 : Signal critique
}
```

**Référence** : ITU-R P.530-17 (Propagation data for FH links)

### SNR (Signal-to-Noise Ratio)
```python
SEUILS_SNR = {
    'EXCELLENT': 30,    # > 30 dB : Excellent
    'BON': 20,          # 20-30 dB : Bon
    'ACCEPTABLE': 15,   # 15-20 dB : Acceptable
    'DEGRADED': 10,     # 10-15 dB : Dégradé
    'CRITIQUE': 5       # < 5 dB : Critique
}
```

**Référence** : ETSI EN 302 217 (Fixed Radio Systems)

### BER (Bit Error Rate)
```python
SEUILS_BER = {
    'EXCELLENT': 1e-9,   # < 10⁻⁹ : Excellent
    'BON': 1e-7,         # 10⁻⁹ à 10⁻⁷ : Bon
    'ACCEPTABLE': 1e-6,  # 10⁻⁷ à 10⁻⁶ : Acceptable
    'DEGRADED': 1e-5,    # 10⁻⁶ à 10⁻⁵ : Dégradé
    'CRITIQUE': 1e-4     # > 10⁻⁴ : Critique
}
```

**Référence** : ITU-T G.826 (Error performance parameters)

### Disponibilité
```python
SEUILS_DISPONIBILITE = {
    'EXCELLENT': 99.999,  # 5 nines : 5.26 min/an indispo
    'BON': 99.99,         # 4 nines : 52.6 min/an
    'ACCEPTABLE': 99.9,   # 3 nines : 8.76 h/an
    'DEGRADED': 99.0,     # 2 nines : 87.6 h/an
    'CRITIQUE': 95.0      # < 95% : Inacceptable
}
```

**Référence** : ITU-T G.827 (Availability objectives)

---

## 🎨 INTERFACE UTILISATEUR

### Design System

**Couleurs** :
- Bleu primaire : `#3B82F6` (liens, graphiques)
- Bleu foncé : `#1E3A8A` (header)
- Vert : `#10B981` (état NORMAL)
- Orange : `#FFA500` (état DEGRADED)
- Rouge : `#DC143C` (état CRITIQUE)

**Badges rôles** :
- 🔴 ADMIN : Rouge
- 🟡 TECH : Jaune
- 🟢 GUEST : Vert

### Pages Streamlit

**app.py** (Accueil) :
- Authentification (email/password)
- Sélection liaison FH
- Aperçu statistiques
- Navigation vers pages

**Dashboard** :
- 5 métriques principales (cards)
- 4 métriques secondaires
- 3 graphiques Plotly interactifs
- Filtre période (6/12/24/48/72h)
- Statistiques détaillées

**Alertes** :
- Statistiques sévérité (5 colonnes)
- 3 filtres (sévérité, statut, période)
- Cartes alertes avec icônes
- Boutons résoudre/supprimer (rôle)
- Graphique pie chart répartition

**Chatbot** :
- 6 suggestions initiales (disparaissent)
- Bulles WhatsApp-style
- Auto-scroll
- Historique session
- Réponses XAI dynamiques

**Import** :
- File uploader (CSV/Excel)
- Validation schéma temps réel
- Aperçu DataFrame
- Statistiques import
- Gestion doublons

---

## 🚀 DÉPLOIEMENT

### Prérequis
1. **Python 3.11** (recommandé pour stabilité)
2. **MySQL 8.0+** (Laragon, XAMPP, ou serveur distant)
3. **Git** (optionnel)

### Installation

```powershell
# 1. Cloner/télécharger le projet
cd "C:\Users\FTAB TECH\Desktop\netpulse-ai"

# 2. Créer environnement virtuel Python 3.11
python -m venv venv311
.\venv311\Scripts\Activate.ps1

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configurer base de données (.env)
DATABASE_URL=mysql+pymysql://root:@localhost:3306/netpulse_ai
SECRET_KEY=your_secret_key_here
SESSION_TIMEOUT=3600
ENVIRONMENT=development

# 5. Créer base de données
python setup_mysql.py

# 6. Importer données de test
python import_scenario.py

# 7. Lancer l'application
streamlit run app.py
```

### Configuration production

**Variables d'environnement** :
```bash
DATABASE_URL=mysql+pymysql://user:password@prod-server:3306/netpulse_ai
SECRET_KEY=<clé_aléatoire_forte_256_bits>
SESSION_TIMEOUT=1800
ENVIRONMENT=production
```

**Sécurité** :
- SSL/TLS pour MySQL
- HTTPS pour Streamlit (reverse proxy Nginx)
- Firewall MySQL (port 3306)
- Backup quotidien base de données

**Performance** :
- Index sur `mesures_kpi(link_id, timestamp)`
- Partitionnement table `mesures_kpi` par mois
- Cache Redis pour KPI fréquents
- CDN pour assets statiques

---

## 📈 ÉVOLUTIONS FUTURES

### Fonctionnalités planifiées
- [ ] API REST (FastAPI) pour intégration externe
- [ ] Notifications email/SMS pour alertes critiques
- [ ] Dashboard multi-liaisons (vue agrégée)
- [ ] Export PDF rapports mensuels
- [ ] Modèles ML avancés (LSTM pour séries temporelles)
- [ ] Cartographie réseau avec Leaflet/Mapbox
- [ ] WebSockets pour mises à jour temps réel
- [ ] Module gestion incidents (ticketing)
- [ ] Intégration météo (API OpenWeatherMap)
- [ ] Logs structurés (ELK stack)

### Optimisations techniques
- [ ] Migration vers PostgreSQL (TimescaleDB pour time-series)
- [ ] Implémentation cache Redis
- [ ] Tests unitaires complets (pytest)
- [ ] CI/CD avec GitHub Actions
- [ ] Dockerisation (Docker Compose)
- [ ] Monitoring avec Prometheus/Grafana
- [ ] Documentation API avec Swagger

---

## 📚 RÉFÉRENCES

### Standards ITU/ETSI
- **ITU-R P.530-17** : Propagation data for terrestrial FH systems
- **ITU-T G.826** : Error performance parameters for digital links
- **ITU-T G.827** : Availability performance parameters
- **ETSI EN 302 217** : Fixed Radio Systems characteristics

### Documentation technique
- **Streamlit** : https://docs.streamlit.io
- **SQLAlchemy** : https://docs.sqlalchemy.org
- **Scikit-learn** : https://scikit-learn.org/stable/
- **Plotly** : https://plotly.com/python/

### Contact
- **Projet** : NetPulse-AI v1.0.0
- **Date** : Novembre 2025
- **Licence** : Propriétaire (usage académique autorisé)

---

**FIN DU DOCUMENT ARCHITECTURE** 🏗️
