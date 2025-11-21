# Guide d'installation avec Python 3.11

## Pourquoi Python 3.11 ?

Python 3.14 est très récent et certaines bibliothèques (comme PyArrow) ne sont pas encore compatibles. Python 3.11 est stable et parfaitement compatible avec toutes les dépendances de NetPulse-AI.

## 🔧 Installation automatique (Recommandée)

### Méthode rapide avec le script PowerShell

```powershell
# Dans le dossier netpulse-ai
.\setup_venv_py311.ps1
```

Ce script va :
- ✅ Détecter Python 3.11 sur votre système
- ✅ Créer un environnement virtuel `venv311`
- ✅ Installer toutes les dépendances
- ✅ Configurer l'environnement pour MySQL

## 📋 Installation manuelle

Si vous préférez installer manuellement :

### Étape 1 : Vérifier Python 3.11

```powershell
# Vérifier la version
python --version

# Ou essayer avec py launcher
py -3.11 --version
```

**Si Python 3.11 n'est pas installé :**
1. Téléchargez depuis : https://www.python.org/downloads/release/python-3119/
2. Installez avec "Add Python to PATH" coché
3. Redémarrez PowerShell

### Étape 2 : Créer l'environnement virtuel

```powershell
# Avec python direct (si c'est la version par défaut)
python -m venv venv311

# OU avec py launcher (si plusieurs versions installées)
py -3.11 -m venv venv311
```

### Étape 3 : Activer l'environnement

```powershell
venv311\Scripts\Activate.ps1
```

**Note** : Si vous avez une erreur de politique d'exécution :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Étape 4 : Mettre à jour pip

```powershell
python -m pip install --upgrade pip
```

### Étape 5 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

**Si ça échoue**, installez manuellement :
```powershell
pip install streamlit pandas numpy sqlalchemy scikit-learn plotly openpyxl python-dotenv bcrypt pymysql cryptography altair
```

### Étape 6 : Vérifier l'installation

```powershell
# Tester la connexion MySQL
python test_mysql.py

# Si succès, lancer l'application
streamlit run app.py
```

## 🔍 Dépannage

### Erreur : "Python 3.11 introuvable"

**Solution 1** : Utilisez py launcher
```powershell
py -0  # Liste toutes les versions Python installées
py -3.11 -m venv venv311
```

**Solution 2** : Spécifiez le chemin complet
```powershell
C:\Users\FTAB TECH\AppData\Local\Programs\Python\Python311\python.exe -m venv venv311
```

**Solution 3** : Installez Python 3.11
- Téléchargez : https://www.python.org/downloads/
- Installez avec "Add to PATH"
- Redémarrez le terminal

### Erreur : "Impossible d'activer le script"

```powershell
# Modifier la politique d'exécution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Puis réessayer
venv311\Scripts\Activate.ps1
```

### Erreur lors de l'installation de packages

```powershell
# Installer sans cache
pip install --no-cache-dir streamlit pandas numpy

# OU installer un par un
pip install streamlit
pip install pandas
pip install sqlalchemy
# etc...
```

### MySQL ne se connecte pas

1. **Vérifiez Laragon** : Le service MySQL doit être démarré (icône verte)
2. **Testez la connexion** :
   ```powershell
   python test_mysql.py
   ```
3. **Vérifiez le .env** :
   ```
   DATABASE_URL=mysql+pymysql://root:@localhost:3306/netpulse_ai
   ```

## ✅ Vérification finale

Une fois tout installé :

```powershell
# 1. Activer l'environnement
venv311\Scripts\Activate.ps1

# 2. Vérifier Python
python --version
# Doit afficher : Python 3.11.x

# 3. Vérifier les packages
pip list

# 4. Tester MySQL
python test_mysql.py

# 5. Lancer l'application
streamlit run app.py
```

## 📊 Structure après installation

```
netpulse-ai/
├── venv311/               ← Environnement virtuel Python 3.11
│   ├── Scripts/
│   │   ├── activate
│   │   ├── Activate.ps1
│   │   ├── python.exe
│   │   └── pip.exe
│   └── Lib/
├── backend/
├── pages/
├── data/
├── app.py
├── requirements.txt
├── .env                   ← Configuration MySQL
└── test_mysql.py
```

## 🚀 Commandes quotidiennes

### Démarrer l'application

```powershell
# 1. Ouvrir PowerShell dans le dossier netpulse-ai
cd C:\Users\FTAB TECH\Desktop\netpulse-ai

# 2. Activer l'environnement
venv311\Scripts\Activate.ps1

# 3. Lancer Streamlit
streamlit run app.py
```

### Arrêter l'application

- Dans le terminal : `Ctrl+C`
- Pour désactiver le venv : `deactivate`

### Mettre à jour les dépendances

```powershell
venv311\Scripts\Activate.ps1
pip install --upgrade streamlit pandas numpy
```

## 📝 Identifiants de test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| **Administrateur** | admin@netpulse.ai | admin123 |
| **Technicien** | tech@netpulse.ai | tech123 |
| **Invité** | guest@netpulse.ai | guest123 |

## 🎯 Checklist complète

- [ ] Python 3.11 installé
- [ ] Environnement virtuel créé (`venv311`)
- [ ] Dépendances installées
- [ ] Laragon démarré
- [ ] MySQL actif
- [ ] Base `netpulse_ai` créée
- [ ] Données importées (30 mesures)
- [ ] Test MySQL réussi
- [ ] Streamlit lancé
- [ ] Connexion admin testée

## 💡 Astuces

### Raccourci pour activer le venv

Créez un fichier `start.ps1` :
```powershell
venv311\Scripts\Activate.ps1
streamlit run app.py
```

Puis lancez simplement :
```powershell
.\start.ps1
```

### Ouvrir directement dans VS Code

```powershell
code .
```

### Logs détaillés de Streamlit

```powershell
streamlit run app.py --logger.level=debug
```

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez `INSTALLATION_MYSQL.md`
2. Vérifiez `test_mysql.py`
3. Regardez les logs dans le terminal
4. Assurez-vous que Laragon/MySQL est démarré
