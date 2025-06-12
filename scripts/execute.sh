#!/bin/bash

sudo apt install -y python3 python3-venv

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances si requirements.txt existe
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Lancer le script principal (remplace src/main.py si besoin)
python src/main.py

# Pause (attend que l'utilisateur appuie sur une touche)
read -p "Appuyez sur une touche pour continuer..."

# Désactiver l'environnement virtuel
deactivate
