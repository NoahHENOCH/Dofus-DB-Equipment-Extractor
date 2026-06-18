@echo off
REM Créer l'environnement virtuel
python -m venv venv

REM Activer l'environnement virtuel
call venv\Scripts\activate

REM Installer les dépendances si requirements.txt existe
IF EXIST requirements.txt (
    pip install -r requirements.txt
)

python src/main.py

pause
REM Désactiver l'environnement virtuel
