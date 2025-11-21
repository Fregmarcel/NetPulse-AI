# Script de configuration d'environnement virtuel Python 3.11
# Pour NetPulse-AI

Write-Host "Configuration de l'environnement Python 3.11 pour NetPulse-AI" -ForegroundColor Cyan
Write-Host "=" * 60

# Verifier si Python 3.11 est disponible
Write-Host "`nVerification de Python 3.11..." -ForegroundColor Yellow

$pythonVersions = @(
    "py -3.11",
    "python3.11",
    "python"
)

$pythonCmd = $null

foreach ($cmd in $pythonVersions) {
    try {
        $version = & $cmd.Split() --version 2>&1
        if ($version -match "3\.11") {
            $pythonCmd = $cmd
            Write-Host "[OK] Python 3.11 trouve: $cmd" -ForegroundColor Green
            Write-Host "   Version: $version" -ForegroundColor Gray
            break
        }
    }
    catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERREUR] Python 3.11 n'est pas installe!" -ForegroundColor Red
    Write-Host "`nSolutions:" -ForegroundColor Yellow
    Write-Host "   1. Telechargez Python 3.11 depuis: https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host "   2. Installez-le avec 'Add Python to PATH' coche" -ForegroundColor Gray
    Write-Host "   3. Relancez ce script" -ForegroundColor Gray
    exit 1
}

# Creer l'environnement virtuel
Write-Host "`nCreation de l'environnement virtuel..." -ForegroundColor Yellow

if (Test-Path "venv311") {
    Write-Host "[ATTENTION] Un environnement 'venv311' existe deja" -ForegroundColor Yellow
    $response = Read-Host "Voulez-vous le supprimer et recreer? (o/N)"
    if ($response -eq "o" -or $response -eq "O") {
        Write-Host "Suppression de l'ancien environnement..." -ForegroundColor Gray
        Remove-Item -Recurse -Force "venv311"
    }
    else {
        Write-Host "[OK] Utilisation de l'environnement existant" -ForegroundColor Green
        & "venv311\Scripts\Activate.ps1"
        Write-Host "`n[OK] Environnement active!" -ForegroundColor Green
        Write-Host "`nProchaines etapes:" -ForegroundColor Cyan
        Write-Host "   1. pip install -r requirements.txt" -ForegroundColor Gray
        Write-Host "   2. streamlit run app.py" -ForegroundColor Gray
        exit 0
    }
}

Write-Host "Creation du venv avec $pythonCmd..." -ForegroundColor Gray
& $pythonCmd.Split() -m venv venv311

if (-not $?) {
    Write-Host "[ERREUR] Echec de la creation de l'environnement virtuel" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Environnement virtuel cree!" -ForegroundColor Green

# Activer l'environnement
Write-Host "`nActivation de l'environnement..." -ForegroundColor Yellow
& "venv311\Scripts\Activate.ps1"

# Mettre a jour pip
Write-Host "`nMise a jour de pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Installer les dependances
Write-Host "`nInstallation des dependances..." -ForegroundColor Yellow
Write-Host "   Cela peut prendre quelques minutes..." -ForegroundColor Gray

pip install -r requirements.txt

if (-not $?) {
    Write-Host "[ERREUR] Erreur lors de l'installation des dependances" -ForegroundColor Red
    Write-Host "`nEssayez d'installer manuellement:" -ForegroundColor Yellow
    Write-Host "   pip install streamlit pandas numpy sqlalchemy scikit-learn plotly openpyxl python-dotenv bcrypt pymysql cryptography altair" -ForegroundColor Gray
    exit 1
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "[OK] INSTALLATION TERMINEE AVEC SUCCES!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`nResume de l'installation:" -ForegroundColor Cyan
Write-Host "   - Environnement: venv311" -ForegroundColor Gray
Write-Host "   - Python: 3.11.x" -ForegroundColor Gray
Write-Host "   - Base de donnees: MySQL (netpulse_ai)" -ForegroundColor Gray
Write-Host "   - Dependances: Installees" -ForegroundColor Gray

Write-Host "`nPour lancer l'application:" -ForegroundColor Cyan
Write-Host "   1. Assurez-vous que Laragon/MySQL est demarre" -ForegroundColor Gray
Write-Host "   2. Activez l'environnement: venv311\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   3. Lancez Streamlit: streamlit run app.py" -ForegroundColor Gray

Write-Host "`nIdentifiants de connexion:" -ForegroundColor Cyan
Write-Host "   - Admin: admin@netpulse.ai / admin123" -ForegroundColor Gray
Write-Host "   - Tech:  tech@netpulse.ai / tech123" -ForegroundColor Gray
Write-Host "   - Guest: guest@netpulse.ai / guest123" -ForegroundColor Gray

Write-Host "`nCommandes utiles:" -ForegroundColor Cyan
Write-Host "   - Tester MySQL: python test_mysql.py" -ForegroundColor Gray
Write-Host "   - Importer donnees: python import_scenario.py" -ForegroundColor Gray
Write-Host "   - Desactiver venv: deactivate" -ForegroundColor Gray

Write-Host "`n" -ForegroundColor Gray
