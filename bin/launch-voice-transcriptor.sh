#!/bin/bash
# Se déplacer dans le répertoire du projet
cd "$(dirname "$0")/.."

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python src/main.py
