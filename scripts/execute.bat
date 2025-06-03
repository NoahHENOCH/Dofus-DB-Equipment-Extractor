@echo off
REM Créer l'environnement virtuel
python -m venv venv

REM Activer l'environnement virtuel
call venv\Scripts\activate

python.exe -m pip install --upgrade pip

REM Installer les dépendances si requirements.txt existe
IF EXIST requirements.txt (
    pip install -r requirements.txt
)

REM Lancer le script principal (remplace mon_script.py par ton fichier)
python src/main.py

pause
REM Désactiver l'environnement virtuel
