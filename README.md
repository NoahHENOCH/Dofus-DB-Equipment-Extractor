# Dofus DB Equipment Extractor

Ce projet permet d'extraire, de traiter et de générer des données sur les métiers et objets du jeu Dofus, à partir de fichiers JSON structurés.

## Structure du projet

```
execute.exe
favicon.ico
README.md
requirements.txt
.gitignore
data/
    csv/
    json/
        jobs.json
        results.json
scripts/
    execute.bat
src/
    extract_functions_dofusdb.py
    main.py
    utilities.py
```

## Installation

1. **Cloner le dépôt**  
   Clone ce dépôt sur ton ordinateur.

2. **Créer et activer un environnement virtuel**  
   Utilise le script fourni :
   ```bat
   execute.exe
   ```
   Ce script crée un environnement virtuel, installe les dépendances et lance le script principal.

3. **Installer sur Linux (optionnel)**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Utilisation

Lance le script principal pour générer ou mettre à jour les fichiers de résultats :
```sh
python src/main.py
```
Le script :
- Lit les métiers depuis `data/json/jobs.json`
- Extrait et traite les objets associés à chaque métier
- Écrit les résultats dans `data/json/results.json`

## Fichiers principaux

- [`src/main.py`](src/main.py) : Point d'entrée du projet.
- [`src/extract_functions_dofusdb.py`](src/extract_functions_dofusdb.py) : Fonctions d'extraction et de gestion des métiers.
- [`src/utilities.py`](src/utilities.py) : Fonctions utilitaires (lecture/écriture JSON, mesure du temps, etc.).
- [`data/json/jobs.json`](data/json/jobs.json) : Liste des métiers et catégories à traiter.
- [`data/json/results.json`](data/json/results.json) : Résultats générés par le script.

## Dépendances

Liste des dépendances dans [`requirements.txt`](requirements.txt).

## Auteurs

- Projet développé par Noah HENOCH
