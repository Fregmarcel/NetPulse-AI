# 🔧 Guide de Dépannage - Données et Alertes

## ❓ Problème : Les données importées n'apparaissent pas

### Solution 1 : Vérifier les données dans la base
```powershell
python verifier_donnees.py
```

Ce script affiche :
- ✅ Toutes les liaisons dans la BD
- ✅ Le nombre de mesures par liaison
- ✅ Les dates des dernières mesures
- ✅ Les alertes actives

### Solution 2 : Vérifier la liaison sélectionnée
1. Dans l'application, regardez la **sidebar gauche**
2. Section "🔗 Liaison active"
3. **La liaison sélectionnée doit correspondre au nom dans votre fichier CSV**

### Solution 3 : Actualiser les données
1. **Après un import**, l'application se recharge automatiquement
2. Si ce n'est pas le cas, cliquez sur **🔄 Actualiser** en haut à droite du Dashboard
3. Ou utilisez F5 pour rafraîchir la page complète

## ❓ Problème : Aucune alerte ne s'affiche

### Diagnostic
```powershell
python diagnostic_alertes.py
```

### Régénération des alertes
```powershell
python regenerer_alertes.py
```

### Vérifications
1. **Les données ont-elles des valeurs critiques ?**
   - RSSI < -75 dBm → devrait créer une alerte
   - SNR < 10 dB → devrait créer une alerte

2. **La liaison sélectionnée est-elle la bonne ?**
   - Vérifiez dans la sidebar

3. **Cliquez sur "🔍 Vérifier Alertes"** dans la page Alertes

## ❓ Problème : Les graphiques affichent "Il y a 10j"

### Cause
Les données importées datent du **17 novembre 2025** (date dans le fichier CSV), mais nous sommes le **28 novembre 2025**.

### Solution 1 : Modifier les dates dans le CSV
Ouvrez votre fichier CSV et changez les dates pour aujourd'hui :
```csv
timestamp,link_name,rssi_dbm,snr_db,ber,...
2025-11-28 00:00:00,Ma Liaison,-50.2,32.1,1.2e-09,...
2025-11-28 00:15:00,Ma Liaison,-50.5,31.8,1.4e-09,...
```

### Solution 2 : Accepter les données historiques
Le système affiche un avertissement clair :
- 🔴 **> 7 jours** : Message d'erreur rouge
- ⚠️ **> 1 jour** : Warning orange
- ✅ **< 24h** : Succès vert

## 🔄 Workflow Normal

1. **Import** (page 📤 Import)
   - Upload du fichier
   - Validation automatique
   - Import en BD
   - Génération des alertes
   - **Rechargement automatique**

2. **Dashboard** (page 📊 Dashboard)
   - Affiche la liaison active
   - Données actualisées automatiquement
   - Bouton 🔄 pour actualiser manuellement
   - Période par défaut : "Tout"

3. **Alertes** (page 🚨 Alertes)
   - Affiche les alertes de la liaison active
   - Statistiques par sévérité
   - Bouton 🔍 pour forcer une vérification

## 📞 Support

Si le problème persiste :
1. Lancez `python verifier_donnees.py`
2. Copiez le résultat
3. Contactez le support avec cette information
