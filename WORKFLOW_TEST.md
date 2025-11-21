# 🧪 WORKFLOW DE TEST COMPLET - NetPulse-AI

## 📋 Vue d'ensemble du projet

**NetPulse-AI** est une plateforme de supervision intelligente pour liaisons micro-ondes FH (Faisceaux Hertziens) avec :
- **Backend** : Python 3.11, SQLAlchemy, MySQL 8.4.3
- **Frontend** : Streamlit 1.51.0 (4 pages)
- **IA** : Scikit-learn (détection anomalies, prédictions)
- **Base de données** : 7 tables, 30 mesures de test, 3 utilisateurs, 2 liaisons FH

### Architecture des fichiers
```
netpulse-ai/
├── app.py                          # Point d'entrée, authentification
├── config.py                       # Configuration, seuils ITU/ETSI
├── .env                           # Variables d'environnement
├── pages/
│   ├── 1_📊_Dashboard.py          # Graphiques temps réel
│   ├── 2_🚨_Alertes.py            # Gestion alertes
│   ├── 3_💬_Chatbot.py            # Assistant IA
│   └── 4_📤_Import.py             # Import CSV/Excel
├── backend/
│   ├── database/
│   │   ├── connection.py          # Connexion MySQL
│   │   └── models.py              # 7 modèles SQLAlchemy
│   ├── security/
│   │   └── auth.py                # Authentification, bcrypt
│   ├── analytics/
│   │   ├── kpi_calculator.py      # Calculs KPI
│   │   └── trend_analyzer.py      # Analyse tendances
│   ├── ai_engine/
│   │   ├── anomaly_detector.py    # Détection anomalies
│   │   └── predictor.py           # Prédictions ML
│   ├── alerts/
│   │   └── alert_engine.py        # Moteur alertes
│   ├── chatbot/
│   │   ├── intent_recognizer.py   # Reconnaissance NLP
│   │   └── response_generator.py  # Génération réponses
│   └── ingestion/
│       └── data_loader.py         # Import CSV/Excel
└── data/                          # Fichiers CSV de test
```

---

## 🔧 PHASE 1 : PRÉPARATION

### 1.1 Vérifier l'environnement

```powershell
# Terminal PowerShell dans c:\Users\FTAB TECH\Desktop\netpulse-ai

# Activer l'environnement Python 3.11
.\venv311\Scripts\Activate.ps1

# Vérifier la version Python
python --version
# ✅ Attendu : Python 3.11.9

# Vérifier les packages installés
pip list | Select-String "streamlit|pandas|sqlalchemy|pymysql|scikit-learn"
# ✅ Attendu :
#    streamlit      1.51.0
#    pandas         2.3.3
#    sqlalchemy     2.0.44
#    pymysql        1.1.2
#    scikit-learn   1.7.2
```

### 1.2 Vérifier MySQL (Laragon)

```powershell
# Démarrer Laragon (interface graphique)
# Menu : MySQL > Démarrer

# Tester la connexion
python test_mysql.py

# ✅ Attendu :
#    ✓ Connexion MySQL réussie!
#    ✓ 3 utilisateurs trouvés
#    ✓ 2 liaisons FH trouvées
#    ✓ 30 mesures KPI trouvées
```

**⚠️ SI ERREUR "Can't connect to MySQL server"** :
- Ouvrir Laragon → Démarrer MySQL
- Vérifier `.env` : `DATABASE_URL=mysql+pymysql://root:@localhost:3306/netpulse_ai`

### 1.3 Lancer l'application

```powershell
# Lancer Streamlit (terminal dédié)
streamlit run app.py

# ✅ Attendu :
#    Local URL: http://localhost:8501
#    Network URL: http://192.168.x.x:8501
```

**⚠️ SI ERREUR** : Vérifier que le terminal "streamlit" n'a pas d'erreur Python

---

## 🔐 PHASE 2 : TESTS D'AUTHENTIFICATION

### 2.1 Test connexion ADMIN

**URL** : http://localhost:8501

**Étapes** :
1. Saisir email : `admin@netpulse.ai`
2. Saisir mot de passe : `admin123`
3. Cliquer "🔓 Se connecter"

**✅ Résultat attendu** :
- Redirection vers page d'accueil
- Sidebar affiche : `🔴 ADMIN` (badge rouge)
- Menu navigation : Accueil, Dashboard, Alertes, Chatbot, **Import** (visible uniquement ADMIN)
- Dropdown "Liaison FH" contient : "Siège CNPS - Datacenter Kennedy", "Datacenter Kennedy - Agence Douala"

**❌ Si erreur** :
- "Email ou mot de passe incorrect" → Vérifier table `utilisateurs` dans MySQL
- Page blanche → Vérifier logs terminal Streamlit

### 2.2 Test connexion TECH

**Étapes** :
1. Se déconnecter (bouton "🚪 Déconnexion" en bas du sidebar)
2. Connexion avec `tech@netpulse.ai` / `tech123`

**✅ Résultat attendu** :
- Badge : `🟡 TECH` (jaune)
- Menu : Accueil, Dashboard, Alertes, Chatbot (PAS d'Import)

### 2.3 Test connexion GUEST

**Étapes** :
1. Se déconnecter
2. Connexion avec `guest@netpulse.ai` / `guest123`

**✅ Résultat attendu** :
- Badge : `🟢 GUEST` (vert)
- Menu : Accueil, Dashboard (lecture seule)
- Pas d'accès aux pages Alertes/Chatbot

**⚠️ Se reconnecter en ADMIN** pour les tests suivants

---

## 📊 PHASE 3 : TESTS DASHBOARD

**Page** : `1_📊_Dashboard.py`
**Prérequis** : Connecté en ADMIN, liaison sélectionnée = "Siège CNPS - Datacenter Kennedy"

### 3.1 Métriques temps réel

**Section** : "📈 Métriques en Temps Réel"

**✅ Vérifications** :
- 5 métriques affichées : État, RSSI, SNR, BER, Modulation
- État = `⚠️ DEGRADED` ou `🔴 CRITIQUE` (dépend des données)
- RSSI ≈ `-80 dBm` (dernière mesure du scénario de dégradation)
- SNR ≈ `8 dB`
- BER ≈ `1e-05`
- Modulation = `16QAM` ou autre

**❌ Si "Aucune donnée disponible"** :
```powershell
# Réimporter les données de test
python import_scenario.py
# ✅ Attendu : "✓ 30 mesures importées avec succès"
```

### 3.2 Test du filtre de période

**Section** : "📉 Graphiques de Tendance"

**Étapes** :
1. Observer le dropdown "Période d'analyse" (valeur par défaut = 24h)
2. **CHANGER** la période vers **6 heures**
3. Attendre 2 secondes (rechargement Streamlit)

**✅ Résultat attendu** :
- Graphique RSSI affiche **moins de points** (seulement données 6h)
- Axe X réduit (seulement les 6 dernières heures)
- Si aucune donnée dans les 6h → "Données insuffisantes"

**Tester toutes les périodes** :
- 6h → 10-15 points (si données récentes)
- 12h → 20-25 points
- 24h → **30 points** (toutes les mesures de test)
- 48h → 30 points (pas de données au-delà de 24h)
- 72h → 30 points

**❌ Si le graphique ne change pas** :
- **BUG CORRIGÉ** dans ce commit
- Vérifier que `date_from` est calculé AVANT la requête DB

### 3.3 Graphiques et seuils

**Graphique RSSI** :
- Ligne bleue continue
- 2 lignes pointillées orange/rouge (seuils ITU)
- Annotations "Seuil Acceptable" (-70 dBm), "Seuil Dégradé" (-75 dBm)
- Points marqueurs visibles au survol

**Graphique SNR** :
- Ligne verte continue
- Seuils à 15 dB (orange) et 10 dB (rouge)

**Graphique "Corrélation RSSI vs Pluie"** :
- Ligne bleue (RSSI, axe gauche)
- Barres bleues transparentes (Pluie, axe droit)
- Vérifier que la pluie augmente quand RSSI chute (corrélation)

### 3.4 Statistiques détaillées

**Section** : "📊 Statistiques Détaillées"

**✅ Vérifications** :
- **RSSI** : Moyenne ≈ -65 dBm, Min ≈ -80 dBm, Max ≈ -52 dBm
- **SNR** : Moyenne ≈ 15 dB, Min ≈ 8 dB, Max ≈ 22 dB
- **Disponibilité** : 60-80% (car données incluent états DEGRADED/CRITIQUE)
- **Nombre de mesures** : 30 (pour période 24h)
- **Pluie** : Maximum ≈ 15-20 mm (pic de dégradation)

**Test du bouton Actualiser** :
- Cliquer "🔄 Actualiser les données"
- Page recharge, données restent identiques (car DB statique)

---

## 🚨 PHASE 4 : TESTS ALERTES

**Page** : `2_🚨_Alertes.py`
**Prérequis** : Connecté en ADMIN ou TECH

### 4.1 Vérification manuelle des alertes

**Section** : Bouton "🔍 Vérifier Alertes" (en haut à droite)

**Étapes** :
1. Cliquer sur le bouton
2. Attendre la vérification (2-3 secondes)

**✅ Résultat attendu** :
- Message : `✅ X nouvelle(s) alerte(s) créée(s)` (si nouvelles alertes)
- OU `Aucune nouvelle alerte` (si déjà créées)

**⚠️ Fonctionnement** :
- Analyse la dernière mesure KPI de la liaison sélectionnée
- Génère alertes si RSSI < -75 dBm, SNR < 12 dB, BER > 1e-5

### 4.2 Statistiques des alertes

**Section** : Métriques en haut (5 colonnes)

**✅ Vérifications** :
- **Total Actives** : 3-5 alertes
- **🔴 Critiques** : 1-2 (affiché en rouge si > 0)
- **Majeures** : 0-2
- **Mineures** : 0-1
- **Warnings** : 0

**Test** : Comparer avec la base de données
```sql
-- Ouvrir HeidiSQL (Laragon) ou MySQL Workbench
SELECT severite, COUNT(*) FROM alertes WHERE resolved = 0 GROUP BY severite;
```

### 4.3 Filtres

**Section** : "🔎 Filtres"

**Test 1 - Filtre par sévérité** :
1. Sélectionner "CRITIQUE" dans le multiselect
2. Liste affiche uniquement alertes critiques

**Test 2 - Filtre par statut** :
1. Changer "Actives" → "Toutes"
2. Liste affiche actives + résolues
3. Changer → "Résolues" : uniquement alertes résolues

**Test 3 - Filtre par période** :
1. Tester : Dernières 24h, Derniers 7 jours, Dernier mois, Tout
2. Vérifier que le nombre d'alertes change

### 4.4 Affichage des alertes

**Section** : "📋 Alertes (X)"

**✅ Vérifications pour chaque carte d'alerte** :
- **Icône** : 🔴 (critique), 🟠 (majeure), 🟡 (mineure)
- **Badge statut** : "🔴 ACTIVE" ou "🟢 RÉSOLUE"
- **Type** : RSSI_DEGRADED, SNR_LOW, etc.
- **Message** : Ex. "RSSI faible détecté : -78.50 dBm"
- **Détails** : Date, Valeur mesurée, Seuil déclenché, 🤖 IA (si générée par IA)
- **Recommandation** : Expandable avec texte explicatif

### 4.5 Actions sur les alertes

**Test RÉSOUDRE (rôle ADMIN ou TECH)** :
1. Trouver une alerte avec badge "🔴 ACTIVE"
2. Cliquer "✅ Résoudre" (colonne droite)
3. ✅ Attendu : Message succès, alerte passe à "🟢 RÉSOLUE"
4. Badge affiche : "✅ Résolue par admin@netpulse.ai le 2025-11-21 XX:XX"

**Test SUPPRIMER (rôle ADMIN uniquement)** :
1. Cliquer "🗑️ Supprimer" sur une alerte
2. ✅ Attendu : Alerte disparaît de la liste

**Test restriction GUEST** :
1. Se connecter en GUEST
2. Tenter d'accéder à `/2_🚨_Alertes`
3. ❌ Attendu : Erreur 403 ou redirection (à vérifier)

### 4.6 Graphique statistiques

**Section** : "📈 Statistiques" (en bas)

**✅ Vérifications** :
- **Pie chart** (camembert) avec répartition par sévérité
- Couleurs : Rouge (CRITIQUE), Orange (MAJEURE), Jaune (MINEURE)
- Légende interactive (cliquer désactive une catégorie)

---

## 💬 PHASE 5 : TESTS CHATBOT

**Page** : `3_💬_Chatbot.py`
**Prérequis** : Connecté en ADMIN ou TECH, liaison sélectionnée

### 5.1 Interface et suggestions

**Au chargement de la page** :

**✅ Vérifications** :
- Titre : "💬 Chatbot - Assistant Intelligent"
- Description : "Posez vos questions sur l'état des liaisons..."
- **6 boutons suggestions** affichés :
  - 👋 Bonjour
  - ❓ Qu'est-ce que tu sais faire ?
  - 📊 Quel est l'état de la liaison ?
  - 🚨 Quelles sont les alertes actives ?
  - 🔮 Prédiction pour les prochaines heures
  - 📈 Quelle est la tendance ?

### 5.2 Test Prompt 1 : Salutation

**Action** : Cliquer sur "👋 Bonjour" OU taper "Bonjour" dans le champ

**✅ Résultat attendu** :
```
🤖 Bot:
Bonjour ! Je suis l'assistant IA de NetPulse. 
Je peux vous aider à surveiller vos liaisons FH.
```

**Vérifications** :
- Message bot aligné à **gauche** (bulle gris clair `#f0f0f0`)
- Message utilisateur (si tapé) aligné à **droite** (bulle vert clair `#dcf8c6`)
- **Les 6 suggestions disparaissent** après le premier message
- Auto-scroll vers le haut de la conversation

### 5.3 Test Prompt 2 : Capacités

**Action** : Taper "Qu'est-ce que tu sais faire ?"

**✅ Résultat attendu** :
```
🤖 Bot:
Je peux vous aider avec :

📊 Analyse de liaison : État actuel, métriques KPI
🔍 Diagnostic : Analyse des dégradations
💡 Recommandations : Actions correctives
🔮 Prédictions : Évolution future (2h)
🧠 XAI : Explications des analyses IA
```

**Vérifications** :
- Liste des 5 capacités affichée
- Emoji présents
- Formatage clair avec sauts de ligne

### 5.4 Test Prompt 3 : État de la liaison (XAI complet)

**Action** : Taper "Quel est l'état de la liaison ?"

**✅ Résultat attendu** (exemple avec données de test) :
```
🤖 Bot:
📡 Analyse complète de "Siège CNPS - Datacenter Kennedy"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MÉTRIQUES ACTUELLES (2025-11-21 13:00:00)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• RSSI : -78.50 dBm ⚠️ DÉGRADÉ
• SNR : 9.20 dB ⚠️ DÉGRADÉ
• BER : 1.50e-05 🔴 CRITIQUE
• État global : 🔴 CRITIQUE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 STATISTIQUES 24H
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• RSSI moyen : -65.30 dBm (vs avg -60.00 dBm : ↓ -5.30 dBm)
• SNR moyen : 14.50 dB (vs avg 18.00 dB : ↓ -3.50 dB)
• Disponibilité : 68.50 %

🧠 DIAGNOSTIC IA (Confiance : 87%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cause principale identifiée : Atténuation par précipitations

🔍 Analyse :
- Pluie détectée : 18.50 mm (forte pluie)
- Corrélation pluie-RSSI : -0.89 (forte)
- Dégradation progressive sur 4 heures
- Seuils ITU-R P.530 dépassés

💡 RECOMMANDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Surveiller l'évolution (conditions météo)
✓ Vérifier ACM adaptatif
⚠ Préparer intervention si persistance
⚠ Alerter équipe si BER > 1e-4

🔮 PRÉVISIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dans 2h (prédiction IA) :
• RSSI prévu : -76.20 dBm (amélioration possible)
• SNR prévu : 10.80 dB
```

**Vérifications critiques** :
- ✅ Toutes les valeurs sont **réelles** (proviennent de la DB)
- ✅ Calcul statistiques 24h correct (moyenne, comparaison)
- ✅ Diagnostic mentionne la pluie si `rainfall_mm > 5`
- ✅ Confiance 87% affichée
- ✅ Recommandations adaptées à la sévérité
- ✅ Prédictions calculées par ML (LinearRegression)

### 5.5 Test Prompt 4 : Alertes actives

**Action** : Taper "Quelles sont les alertes actives ?"

**✅ Résultat attendu** :
```
🤖 Bot:
🚨 Alertes actives pour "Siège CNPS" (5 alertes)

🔴 Critiques (2):
- RSSI critique : -80.00 dBm (seuil : -75 dBm)
- BER inacceptable : 2.50e-05 (seuil : 1.00e-05)

🟠 Majeures (2):
- SNR faible : 8.50 dB (seuil : 10 dB)
- Latence élevée : 45 ms (seuil : 40 ms)

🟡 Mineures (1):
- Perte de paquets : 0.85% (seuil : 0.5%)

💡 Recommandation : Consultez page Alertes pour actions
```

**Vérifications** :
- Groupement par sévérité (Critiques/Majeures/Mineures/Prédictives)
- Nombre total correct
- Messages d'alertes réels de la DB
- Limite de 3 alertes par catégorie (si plus, tronqué avec "...")

### 5.6 Test Prompts supplémentaires

**Test variations orthographiques** :
- "bonjour" (minuscule) → Doit fonctionner
- "BONJOUR" (majuscule) → Doit fonctionner
- "bjr" (abréviation) → Reconnu comme salutation

**Test prompts non reconnus** :
- "Quelle heure est-il ?" → Réponse générique
- "Blabla random" → Réponse d'aide par défaut

**Test auto-scroll** :
- Envoyer 10 messages successifs
- ✅ Attendu : Scroll automatique vers le haut à chaque message

### 5.7 Historique de conversation

**Étapes** :
1. Envoyer 5 messages différents
2. Actualiser la page (F5)
3. ✅ Attendu : Historique conservé (session Streamlit)

**Réinitialisation** :
1. Se déconnecter puis reconnecter
2. ✅ Attendu : Historique effacé (nouvelle session)

---

## 📤 PHASE 6 : TESTS IMPORT

**Page** : `4_📤_Import.py`
**Prérequis** : Connecté en **ADMIN uniquement**

### 6.1 Vérification accès

**Test restriction rôle** :
1. Se connecter en TECH
2. Menu navigation ne doit **PAS** afficher "Import"
3. Tenter URL directe : `http://localhost:8501/4_📤_Import`
4. ❌ Attendu : Erreur ou redirection (si implémenté)

**Se reconnecter en ADMIN** pour tests suivants

### 6.2 Créer fichier CSV de test

**Créer** : `c:\Users\FTAB TECH\Desktop\netpulse-ai\data\test_import.csv`

```csv
timestamp,rssi_dbm,snr_db,ber,acm_modulation,rainfall_mm,latency_ms,packet_loss
2025-11-21 15:00:00,-55.5,19.2,1.2e-08,64QAM,0.0,12.5,0.05
2025-11-21 15:15:00,-56.0,18.8,1.5e-08,64QAM,0.5,13.0,0.06
2025-11-21 15:30:00,-58.2,17.5,2.0e-08,32QAM,1.2,14.2,0.08
2025-11-21 15:45:00,-62.0,15.0,5.0e-07,32QAM,3.5,16.0,0.12
2025-11-21 16:00:00,-68.5,12.5,1.5e-05,16QAM,8.0,20.5,0.25
```

### 6.3 Import CSV valide

**Étapes** :
1. Sélectionner liaison : "Datacenter Kennedy - Agence Douala"
2. Cliquer "Parcourir" (File uploader)
3. Sélectionner `test_import.csv`
4. Attendre validation automatique (2 secondes)

**✅ Résultat attendu** :
- Section "📊 Aperçu des données" apparaît
- Tableau avec 5 lignes affichées
- Bouton "✅ Confirmer l'import" activé

**Cliquer "✅ Confirmer l'import"** :
- ✅ Message succès : "✓ 5 mesures importées avec succès"
- Statistiques :
  - Total lignes : 5
  - Valides : 5
  - Doublons ignorés : 0

### 6.4 Test gestion doublons

**Étapes** :
1. **Réimporter le même fichier** `test_import.csv`
2. Cliquer "✅ Confirmer l'import"

**✅ Résultat attendu** :
- Message : "✓ 0 mesures importées (5 doublons ignorés)"
- Statistiques : Doublons = 5

**⚠️ Mécanisme** :
- Doublon = même `link_id` + `timestamp`
- Fonction `load_measures_from_dataframe()` vérifie existence dans DB

### 6.5 Test validation schéma

**Créer fichier invalide** : `test_invalid.csv`
```csv
timestamp,rssi_dbm
2025-11-21 15:00:00,-55.5
```

**Étapes** :
1. Upload `test_invalid.csv`

**❌ Résultat attendu** :
- Message erreur : "Colonnes manquantes : snr_db, ber, acm_modulation, rainfall_mm, latency_ms, packet_loss"
- Bouton "Confirmer" désactivé

### 6.6 Test validation valeurs

**Créer fichier hors limites** : `test_outliers.csv`
```csv
timestamp,rssi_dbm,snr_db,ber,acm_modulation,rainfall_mm,latency_ms,packet_loss
2025-11-21 15:00:00,-150.0,50.0,0.5,64QAM,0.0,12.5,0.05
```

**Étapes** :
1. Upload `test_outliers.csv`

**⚠️ Résultat attendu** :
- Import accepté (validation basique uniquement)
- OU erreur si validation stricte implémentée

**Plages normales ITU** :
- RSSI : -100 à -30 dBm
- SNR : 0 à 40 dB
- BER : 1e-12 à 1e-3
- Rainfall : 0 à 100 mm
- Latency : 0 à 200 ms
- Packet loss : 0 à 100 %

### 6.7 Test import Excel

**Créer** : `test_import.xlsx` (Excel)
- Même structure que CSV
- 5 lignes de données

**Étapes** :
1. Upload `test_import.xlsx`
2. ✅ Attendu : Détection automatique Excel, import réussi

---

## 🔬 PHASE 7 : TESTS AVANCÉS

### 7.1 Test intégrité base de données

```powershell
# Terminal PowerShell
python

# Console Python
>>> from backend.database.connection import get_db_context
>>> from backend.database.models import MesureKPI, Alerte, Utilisateur
>>> 
>>> with get_db_context() as db:
...     print(f"Mesures : {db.query(MesureKPI).count()}")
...     print(f"Alertes : {db.query(Alerte).count()}")
...     print(f"Utilisateurs : {db.query(Utilisateur).count()}")
... 
# ✅ Attendu :
#    Mesures : 35+ (30 initiales + 5 importées)
#    Alertes : 3-10
#    Utilisateurs : 3
```

### 7.2 Test calculs KPI

```python
>>> from backend.analytics.kpi_calculator import calculate_period_statistics
>>> 
>>> stats = calculate_period_statistics(link_id=1, hours=24)
>>> print(f"RSSI moyen : {stats['rssi']['avg']:.2f} dBm")
>>> print(f"Disponibilité : {stats['disponibilite']:.2f} %")
# ✅ Vérifier cohérence des valeurs
```

### 7.3 Test détection anomalies

```python
>>> from backend.ai_engine.anomaly_detector import detect_anomalies_zscore
>>> 
>>> anomalies = detect_anomalies_zscore(link_id=1, metric='rssi_dbm', hours=24)
>>> print(f"Anomalies détectées : {len(anomalies)}")
>>> for a in anomalies[:3]:
...     print(f"  {a['timestamp']} : {a['value']:.2f} dBm (z-score: {a['z_score']:.2f})")
... 
# ✅ Attendu : 2-5 anomalies (pics de dégradation)
```

### 7.4 Test prédictions ML

```python
>>> from backend.ai_engine.predictor import predict_next_values
>>> 
>>> predictions = predict_next_values(link_id=1, metric='rssi_dbm', hours_ahead=2)
>>> print(f"RSSI dans 2h : {predictions['predicted_value']:.2f} dBm")
>>> print(f"Confiance : {predictions['confidence']:.2f}")
# ✅ Attendu : Valeur entre -80 et -50 dBm
```

### 7.5 Test génération alertes

```python
>>> from backend.alerts.alert_engine import check_and_create_alerts
>>> 
>>> new_alerts = check_and_create_alerts(link_id=1)
>>> print(f"Nouvelles alertes : {len(new_alerts)}")
>>> for alert in new_alerts:
...     print(f"  {alert['type']} : {alert['message']}")
... 
# ✅ Attendu : 0-3 alertes (si conditions remplies)
```

### 7.6 Test chatbot NLP

```python
>>> from backend.chatbot.intent_recognizer import recognize_intent
>>> 
>>> intent = recognize_intent("Quel est l'état de la liaison ?")
>>> print(f"Intent : {intent}")
# ✅ Attendu : 'link_status'
>>> 
>>> intent = recognize_intent("Bonjour !")
>>> print(f"Intent : {intent}")
# ✅ Attendu : 'greeting'
```

---

## 🐛 PHASE 8 : RAPPORT D'ERREURS

### Format de rapport

**Quand vous trouvez une erreur**, fournissez :

```
🐛 BUG REPORT

📄 Page/Fonctionnalité : [Ex: Dashboard - Filtre période]

🔍 Étapes pour reproduire :
1. [Action 1]
2. [Action 2]
3. [Action 3]

❌ Résultat actuel :
[Ce qui se passe]

✅ Résultat attendu :
[Ce qui devrait se passer]

📋 Logs/Erreur (si applicable) :
[Copier message d'erreur du terminal Streamlit]

🖥️ Contexte :
- Rôle utilisateur : [ADMIN/TECH/GUEST]
- Liaison sélectionnée : [Nom]
- Navigateur : [Chrome/Firefox/Edge]
```

### Exemples d'erreurs courantes

**Erreur 1 : DetachedInstanceError**
```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <X> is not bound to a Session
```
→ **Cause** : Accès attribut SQLAlchemy hors session
→ **Localisation** : Dashboard, Alertes, Chatbot

**Erreur 2 : KeyError**
```
KeyError: 'rssi_dbm'
```
→ **Cause** : Clé manquante dans dictionnaire
→ **Localisation** : KPI calculator, Response generator

**Erreur 3 : TypeError**
```
TypeError: unsupported operand type(s) for -: 'NoneType' and 'timedelta'
```
→ **Cause** : Valeur None inattendue
→ **Localisation** : Date filtering, Period calculations

---

## ✅ CHECKLIST COMPLÈTE

### Authentification
- [ ] Connexion ADMIN réussie
- [ ] Connexion TECH réussie
- [ ] Connexion GUEST réussie
- [ ] Badges rôles affichés correctement
- [ ] Menu navigation adapté au rôle
- [ ] Déconnexion fonctionne

### Dashboard
- [ ] Métriques temps réel affichées
- [ ] Filtre période 6h fonctionne
- [ ] Filtre période 12h fonctionne
- [ ] Filtre période 24h fonctionne
- [ ] Filtre période 48h fonctionne
- [ ] Filtre période 72h fonctionne
- [ ] Graphique RSSI avec seuils
- [ ] Graphique SNR avec seuils
- [ ] Graphique corrélation pluie
- [ ] Statistiques détaillées calculées
- [ ] Bouton actualiser fonctionne

### Alertes
- [ ] Bouton vérifier alertes fonctionne
- [ ] Statistiques sévérité affichées
- [ ] Filtre par sévérité fonctionne
- [ ] Filtre par statut fonctionne
- [ ] Filtre par période fonctionne
- [ ] Cartes alertes affichées correctement
- [ ] Bouton résoudre fonctionne (ADMIN/TECH)
- [ ] Bouton supprimer fonctionne (ADMIN)
- [ ] Graphique statistiques affiché
- [ ] Restrictions rôle GUEST

### Chatbot
- [ ] 6 suggestions affichées au démarrage
- [ ] Prompt "Bonjour" fonctionne
- [ ] Prompt "Capacités" fonctionne
- [ ] Prompt "État liaison" avec XAI complet
- [ ] Prompt "Alertes actives" fonctionne
- [ ] Prompt "Prédictions" fonctionne
- [ ] Prompt "Tendances" fonctionne
- [ ] Suggestions disparaissent après 1er message
- [ ] Auto-scroll fonctionne
- [ ] Messages bulles alignées (user droite, bot gauche)
- [ ] Historique conservé dans session

### Import
- [ ] Page accessible uniquement par ADMIN
- [ ] Upload CSV valide fonctionne
- [ ] Upload Excel valide fonctionne
- [ ] Détection doublons fonctionne
- [ ] Validation schéma fonctionne
- [ ] Aperçu données affiché
- [ ] Statistiques import affichées
- [ ] Gestion erreurs validation

### Tests avancés
- [ ] Intégrité base de données vérifiée
- [ ] Calculs KPI corrects
- [ ] Détection anomalies fonctionne
- [ ] Prédictions ML fonctionnent
- [ ] Génération alertes dynamique
- [ ] Reconnaissance intent NLP

---

## 📊 DONNÉES DE RÉFÉRENCE

### Utilisateurs de test
```
Email                 | Mot de passe | Rôle
----------------------|--------------|-------
admin@netpulse.ai     | admin123     | ADMIN
tech@netpulse.ai      | tech123      | TECH
guest@netpulse.ai     | guest123     | GUEST
```

### Liaisons FH
```
ID | Nom
---|--------------------------------------------
1  | Siège CNPS - Datacenter Kennedy
2  | Datacenter Kennedy - Agence Douala
```

### Scénario de données (30 mesures)
```
Temps         | RSSI    | SNR   | État
--------------|---------|-------|--------
07:45-09:00   | -52 dBm | 22 dB | NORMAL
09:00-10:30   | -58 dBm | 18 dB | NORMAL
10:30-11:45   | -68 dBm | 14 dB | DEGRADED
11:45-13:00   | -80 dBm | 8 dB  | CRITIQUE
```

### Seuils ITU/ETSI
```
Métrique | Excellent | Bon   | Acceptable | Dégradé | Critique
---------|-----------|-------|------------|---------|----------
RSSI     | -50 dBm   | -60   | -70        | -75     | -80
SNR      | 30 dB     | 20    | 15         | 10      | 5
BER      | 1e-9      | 1e-7  | 1e-6       | 1e-5    | 1e-4
```

---

## 🎯 RÉSUMÉ EXÉCUTIF

**Durée estimée du workflow** : 45-60 minutes

**Priorité des tests** :
1. 🔴 **CRITIQUE** : Authentification, Dashboard, Alertes (fonctionnalités principales)
2. 🟡 **IMPORTANT** : Chatbot XAI, Import CSV (fonctionnalités avancées)
3. 🟢 **OPTIONNEL** : Tests avancés Python (validation technique)

**Checklist minimale pour validation** :
- ✅ Connexion 3 rôles fonctionne
- ✅ Dashboard affiche graphiques avec filtre période
- ✅ Alertes affichées et actions fonctionnent
- ✅ Chatbot répond aux 3 prompts principaux avec données réelles
- ✅ Import CSV valide réussit

**⚠️ BUGS CONNUS CORRIGÉS** :
- ✅ Filtre période Dashboard (corrigé dans ce commit)
- ✅ DetachedInstanceError Dashboard (corrigé précédemment)
- ✅ DetachedInstanceError Alertes (corrigé dans ce commit)
- ✅ DetachedInstanceError Chatbot (corrigé précédemment)

**📧 Contact pour support** :
- Ouvrir ce document `WORKFLOW_TEST.md`
- Copier format rapport d'erreur
- Envoyer avec logs terminal Streamlit

---

**BON TEST ! 🚀**
