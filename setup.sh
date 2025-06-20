#!/bin/bash

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "pip3 n'est pas installé. Installation en cours..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Créer et activer un environnement virtuel
echo "Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo "Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Installer les dépendances système nécessaires
echo "Installation des dépendances système..."
sudo apt update
sudo apt install -y portaudio19-dev python3-dev ffmpeg pulseaudio-utils libxcb-cursor0

# Demander la clé API OpenAI
read -p "Veuillez entrer votre clé API OpenAI: " openai_key

echo "Configuration de la clé API..."
echo "export OPENAI_API_KEY='$openai_key'" >> ~/.bashrc
echo "export OPENAI_API_KEY='$openai_key'" >> ~/.profile

# Rendre les scripts exécutables
chmod +x src/main.py

# Message de fin
echo """
Installation terminée !

Pour lancer l'application, utilisez les commandes suivantes :

    source venv/bin/activate
    python src/main.py

Vous pouvez aussi ajouter l'alias suivant à votre fichier ~/.bashrc :
    alias voice-transcriptor='cd $(pwd) && source venv/bin/activate && python src/main.py'
"""

# Redémarrer le shell pour appliquer les changements
source ~/.bashrc
source ~/.profile
