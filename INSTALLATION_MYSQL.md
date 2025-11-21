# Guide d'installation MySQL avec Laragon

## 📋 Prérequis

1. **Laragon** doit être installé et démarré
2. Le service **MySQL** doit être actif dans Laragon

## 🚀 Étapes d'installation

### Étape 1 : Démarrer Laragon

1. Ouvrez **Laragon**
2. Cliquez sur **Démarrer tout** (Start All)
3. Vérifiez que MySQL est démarré (icône verte)

### Étape 2 : Configurer la connexion MySQL

Le fichier `.env` a été configuré avec les paramètres par défaut de Laragon :

```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/netpulse_ai
```

**Paramètres par défaut Laragon :**
- **Utilisateur** : `root`
- **Mot de passe** : (vide)
- **Hôte** : `localhost`
- **Port** : `3306`
- **Base de données** : `netpulse_ai`

### Étape 3 : Créer la base de données

#### Option A : Via HeidiSQL (inclus dans Laragon)

1. Dans Laragon, cliquez sur **Database** → **HeidiSQL**
2. Clic droit sur **Unnamed** → **Create new** → **Database**
3. Nom : `netpulse_ai`
4. Charset : `utf8mb4`
5. Collation : `utf8mb4_unicode_ci`
6. Cliquez sur **OK**

#### Option B : Via le terminal Laragon

1. Dans Laragon, cliquez sur **Terminal**
2. Exécutez :
```bash
mysql -u root
```
3. Dans MySQL :
```sql
CREATE DATABASE netpulse_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Étape 4 : Initialiser les tables

Dans votre terminal PowerShell du projet :

```powershell
python backend\database\init_db.py
```

Cette commande va :
- Créer toutes les tables (7 tables)
- Créer 3 utilisateurs par défaut
- Créer 2 liaisons FH de test

### Étape 5 : Importer les données de scénario

```powershell
python import_scenario.py
```

Cela importera 30 mesures KPI avec un scénario de dégradation réaliste.

### Étape 6 : Lancer l'application

```powershell
streamlit run app.py
```

## 🔐 Comptes utilisateurs

Après l'initialisation, 3 comptes sont disponibles :

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| **Administrateur** | admin@netpulse.ai | admin123 |
| **Technicien** | tech@netpulse.ai | tech123 |
| **Invité** | guest@netpulse.ai | guest123 |

## 🔧 Configuration avancée

### Modifier les paramètres MySQL

Si votre configuration Laragon est différente, modifiez le fichier `.env` :

```env
# Format: mysql+pymysql://utilisateur:mot_de_passe@hôte:port/nom_base
DATABASE_URL=mysql+pymysql://votre_user:votre_mdp@localhost:3306/netpulse_ai
```

### Revenir à SQLite

Si vous voulez utiliser SQLite au lieu de MySQL :

```env
DATABASE_URL=sqlite:///netpulse.db
```

## ❗ Résolution de problèmes

### Erreur : "Can't connect to MySQL server"

✅ **Solution** :
1. Vérifiez que Laragon est démarré
2. Vérifiez que MySQL est actif (icône verte dans Laragon)
3. Redémarrez MySQL dans Laragon : clic droit sur Laragon → MySQL → Reload

### Erreur : "Access denied for user 'root'"

✅ **Solution** :
1. Dans Laragon, vérifiez le mot de passe MySQL
2. Menu Laragon → MySQL → Root Password
3. Mettez à jour le `.env` avec le bon mot de passe

### Erreur : "Unknown database 'netpulse_ai'"

✅ **Solution** :
La base de données n'existe pas. Créez-la avec HeidiSQL ou via le terminal (voir Étape 3).

### Les dépendances ne s'installent pas

✅ **Solution** :
```powershell
# Installer seulement les dépendances essentielles
python -m pip install streamlit pandas numpy sqlalchemy scikit-learn plotly openpyxl python-dotenv bcrypt pymysql cryptography altair
```

## 📊 Vérification de l'installation

Pour vérifier que tout fonctionne :

1. **Base de données créée** :
   - Ouvrez HeidiSQL
   - Vérifiez que `netpulse_ai` existe
   - Vérifiez les 7 tables : `utilisateurs`, `fh_links`, `mesures_kpi`, `kpi_synthese`, `alertes`, `traces_connexion`, `parametres_systeme`

2. **Données importées** :
   - Dans HeidiSQL, ouvrez la table `mesures_kpi`
   - Vérifiez qu'il y a 30 lignes

3. **Application fonctionnelle** :
   - Lancez `streamlit run app.py`
   - Connectez-vous avec `admin@netpulse.ai` / `admin123`
   - Vérifiez que le Dashboard affiche des graphiques

## 📝 Structure de la base de données

```
netpulse_ai
├── utilisateurs          (Comptes utilisateurs)
├── fh_links             (Liaisons FH configurées)
├── mesures_kpi          (Mesures collectées)
├── kpi_synthese         (Synthèses KPI)
├── alertes              (Alertes générées)
├── traces_connexion     (Logs de connexion)
└── parametres_systeme   (Paramètres globaux)
```

## 🎯 Prochaines étapes

1. ✅ Tester le chatbot avec les 3 prompts :
   - "Bonjour"
   - "Qu'est-ce que tu sais faire ?"
   - "Quel est l'état de la liaison ?"

2. ✅ Explorer le Dashboard avec les données importées

3. ✅ Capturer les screenshots pour votre mémoire

---

**Besoin d'aide ?** Consultez la documentation de Laragon : https://laragon.org/docs/
