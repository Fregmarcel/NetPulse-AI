# 📄 Guide de Génération de Données CSV

## 🎯 Problème Résolu

Les données du fichier `sample_fh_data.csv` datent du **17 novembre 2025**, donc affichent "Il y a 11 jours" dans le Dashboard.

## ✅ Solutions

### Solution 1 : Script Simple (Recommandé)

Génère un fichier avec des données des **dernières 24 heures** :

```powershell
python generer_donnees_recentes.py
```

**Résultat** :
- Fichier créé : `data/mesures_recentes_24h.csv`
- 96 mesures (1 toutes les 15 minutes)
- Timestamps des dernières 24h
- Scénario : Dégradation progressive

---

### Solution 2 : Script Flexible (Personnalisé)

Permet de choisir la période et le scénario :

```powershell
python generer_csv_flexible.py
```

**Options disponibles :**

#### 📅 Périodes
1. **24 heures** (96 mesures, recommandé)
2. **48 heures** (192 mesures)
3. **7 jours** (168 mesures)
4. **6 heures** (24 mesures, temps réel)

#### 🎭 Scénarios
1. **Normal** : Valeurs stables, pas de problème
2. **Dégradation progressive** : Commence bien, finit mal
3. **Pic de dégradation** : Problème au milieu (épisode pluvieux)
4. **Aléatoire réaliste** : Variations naturelles

---

## 📤 Import dans NetPulse-AI

### Étape 1 : Générer les données

```powershell
# Option simple
python generer_donnees_recentes.py

# OU option flexible
python generer_csv_flexible.py
```

### Étape 2 : Nettoyer la base (si nécessaire)

Si vous avez déjà des données et voulez repartir de zéro :

```powershell
python nettoyer_bd.py
```

### Étape 3 : Lancer Streamlit

```powershell
streamlit run app.py
```

### Étape 4 : Importer

1. Connectez-vous en **admin** (admin@netpulse.ai / admin123)
2. Allez sur **📤 Import**
3. Uploadez le fichier généré (dans `data/`)
4. Cliquez sur **📤 Importer**

### Étape 5 : Vérifier

1. **📊 Dashboard** : Les graphiques affichent maintenant "Données récentes"
2. **🚨 Alertes** : Les alertes sont générées automatiquement

---

## 📊 Fichiers Générés

Les fichiers sont créés dans le dossier `data/` :

| Fichier | Période | Mesures | Génération |
|---------|---------|---------|------------|
| `mesures_24h.csv` | 24h | 96 | Script flexible |
| `mesures_48h.csv` | 48h | 192 | Script flexible |
| `mesures_7j.csv` | 7 jours | 168 | Script flexible |
| `mesures_temps_reel_6h.csv` | 6h | 24 | Script flexible |
| `mesures_recentes_24h.csv` | 24h | 96 | Script simple |

---

## 🎯 Exemples d'Utilisation

### Pour Tests Rapides
```powershell
python generer_donnees_recentes.py
```
→ Génère `data/mesures_recentes_24h.csv` avec dégradation progressive

### Pour Démonstration
```powershell
python generer_csv_flexible.py
# Choisir : 1 (24h)
# Scénario : 3 (Pic de dégradation)
```
→ Simule un épisode pluvieux au milieu

### Pour Supervision Continue
```powershell
python generer_csv_flexible.py
# Choisir : 4 (6h temps réel)
# Scénario : 1 (Normal)
```
→ Données récentes sans problème

---

## 🔍 Vérification

Après génération, vérifiez le fichier :

```powershell
python analyser_csv.py
```

Cela affiche :
- ✅ Colonnes présentes
- ✅ Plage temporelle
- ✅ Statistiques RSSI/SNR
- ✅ Nombre d'alertes attendues

---

## ⚠️ Important

### Les timestamps dans le CSV définissent l'affichage

Le Dashboard affiche **les dates du fichier CSV**, pas la date d'import.

**Exemple** :
- CSV avec dates du 17 nov → Dashboard affiche "Il y a 11j"
- CSV avec dates d'aujourd'hui → Dashboard affiche "Données récentes"

### Pour avoir des données "temps réel"

Utilisez **toujours** les scripts de génération qui créent des timestamps récents :
- `generer_donnees_recentes.py` → Dernières 24h
- `generer_csv_flexible.py` avec option 4 → Dernières 6h

---

## 📋 Workflow Complet

```powershell
# 1. Générer des données récentes
python generer_donnees_recentes.py

# 2. Nettoyer la base (optionnel)
python nettoyer_bd.py

# 3. Lancer l'application
streamlit run app.py

# 4. Importer le fichier
#    → 📤 Import
#    → Upload data/mesures_recentes_24h.csv
#    → Importer

# 5. Vérifier
#    → 📊 Dashboard : "Données récentes"
#    → 🚨 Alertes : Alertes affichées
```

---

## 🆘 Dépannage

### Problème : "96 doublons"
→ Les données existent déjà. Lancez `python nettoyer_bd.py` puis réimportez

### Problème : "Aucune alerte"
→ Lancez `python regenerer_alertes.py`

### Problème : "Il y a 10j"
→ Vous avez importé un fichier avec d'anciennes dates. Générez un nouveau CSV !

---

**Créé pour NetPulse-AI** 📡
