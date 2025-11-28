# 🔧 GUIDE DE DIAGNOSTIC - Problème d'Import

## 🎯 Votre Problème

**Symptôme** : Après l'import, la table `mesures_kpi` dans HeidiSQL montre **0 lignes**, mais Streamlit dit "96 doublons".

## 🔍 Diagnostic en 3 Étapes

### Étape 1 : Vérifier la connexion MySQL

```powershell
python verifier_mysql.py
```

**Ce script va vous dire :**
- ✅ Si la connexion MySQL fonctionne
- ✅ Combien de mesures sont dans `mesures_kpi`
- ✅ Combien de liaisons existent
- ✅ Les paramètres de connexion utilisés

**Résultats attendus :**
- Si 0 mesures → Les données ne sont PAS importées
- Si 96 mesures → Les données SONT importées, mais vous regardez la mauvaise base dans HeidiSQL

---

### Étape 2 : Analyser le fichier CSV

```powershell
python analyser_csv.py
```

**Ce script vérifie :**
- ✅ Les colonnes du CSV
- ✅ Le nom de la liaison
- ✅ Les valeurs RSSI/SNR
- ✅ Les timestamps

---

### Étape 3 : Nettoyer et réimporter

```powershell
python nettoyer_bd.py
```

**Ce script va :**
- 🗑️ Supprimer toutes les mesures existantes
- 🗑️ Supprimer toutes les alertes
- ✅ Permettre un nouvel import

**Ensuite, dans Streamlit :**
1. Allez sur 📤 Import
2. Réimportez votre fichier
3. Observez les logs dans la console

---

## 🔍 Causes Possibles

### 1. **Vous regardez la mauvaise base de données** ❌

**Problème** : HeidiSQL est connecté à une autre base que celle utilisée par l'application.

**Solution** :
1. Dans HeidiSQL, vérifiez la base sélectionnée (en haut à gauche)
2. Elle doit être : **`netpulse_ai`**
3. Si vous voyez une autre base, changez la sélection

**Vérification** :
- Dans HeidiSQL, cliquez sur `netpulse_ai` dans l'arbre à gauche
- Rafraîchissez avec F5
- Cliquez sur la table `mesures_kpi`
- Regardez l'onglet "Données"

---

### 2. **Les données sont déjà importées (doublons)** ✅

**Problème** : Vous avez déjà importé ce fichier. Le système détecte 96 doublons.

**Solution** :
1. Lancez `python nettoyer_bd.py` pour supprimer les mesures
2. Réimportez le fichier

**Ou** :
1. Modifiez les timestamps dans votre CSV pour avoir des dates différentes
2. Réimportez

---

### 3. **Le nom de la liaison ne correspond pas** ❌

**Problème** : Le `link_name` dans votre CSV ne correspond à aucune liaison existante.

**Solution** :
1. Lancez `python analyser_csv.py` pour voir le nom de liaison dans le CSV
2. Lancez `python verifier_mysql.py` pour voir les liaisons en base
3. Vérifiez qu'ils correspondent **exactement** (majuscules, accents, espaces)

---

### 4. **Problème de connexion MySQL** ❌

**Problème** : Le fichier `.env` pointe vers MySQL, mais MySQL n'est pas démarré ou la connexion échoue.

**Solution** :
1. Ouvrez Laragon
2. Vérifiez que MySQL est démarré (icône verte)
3. Lancez `python verifier_mysql.py` pour tester la connexion

**Si la connexion échoue** :
1. Ouvrez le fichier `.env`
2. Vérifiez : `DATABASE_URL=mysql+pymysql://root:@localhost:3306/netpulse_ai`
3. Vérifiez que la base `netpulse_ai` existe dans HeidiSQL

---

## 🎯 Procédure Complète de Réinitialisation

Si rien ne fonctionne, faites une **réinitialisation complète** :

### 1. Supprimer la base de données

Dans HeidiSQL :
```sql
DROP DATABASE IF EXISTS netpulse_ai;
CREATE DATABASE netpulse_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Réinitialiser les tables

```powershell
python backend/database/init_db.py
```

### 3. Vérifier la structure

```powershell
python verifier_mysql.py
```

Vous devriez voir :
- ✅ 3 utilisateurs
- ✅ 2 liaisons FH
- ✅ 0 mesures

### 4. Importer les données

1. Lancez Streamlit : `streamlit run app.py`
2. Connectez-vous en admin
3. Allez sur 📤 Import
4. Uploadez votre CSV
5. Cliquez sur **Importer**

### 5. Vérifier le résultat

```powershell
python verifier_mysql.py
```

Vous devriez maintenant voir vos mesures !

---

## 📋 Checklist Finale

Avant de dire que ça ne fonctionne pas, vérifiez :

- [ ] MySQL est démarré dans Laragon
- [ ] La base `netpulse_ai` existe
- [ ] HeidiSQL est connecté à `netpulse_ai` (pas à une autre base)
- [ ] Le fichier `.env` contient : `DATABASE_URL=mysql+pymysql://root:@localhost:3306/netpulse_ai`
- [ ] Le script `verifier_mysql.py` affiche les bonnes informations
- [ ] Le CSV contient bien une colonne `link_name`
- [ ] Le nom de la liaison dans le CSV correspond à une liaison en base

---

## 🆘 Si Rien ne Fonctionne

Lancez cette séquence complète et partagez-moi les résultats :

```powershell
# 1. Vérifier MySQL
python verifier_mysql.py

# 2. Analyser le CSV
python analyser_csv.py

# 3. Vérifier les données avec SQLAlchemy
python verifier_donnees.py
```

Copiez-moi tous les résultats !
