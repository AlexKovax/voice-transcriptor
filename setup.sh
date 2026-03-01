#!/bin/bash

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}  Voice Transcriptor - Installation${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erreur: Python 3 n'est pas installé.${NC}"
    echo "Veuillez l'installer avant de continuer:"
    echo "  sudo apt update && sudo apt install -y python3"
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}pip3 n'est pas installé. Installation en cours...${NC}"
    sudo apt update
    sudo apt install -y python3-pip
fi

# Créer et activer un environnement virtuel
echo -e "${BLUE}Création de l'environnement virtuel...${NC}"
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo -e "${BLUE}Installation des dépendances Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Installer les dépendances système nécessaires
echo -e "${BLUE}Installation des dépendances système...${NC}"
echo "Cette opération nécessite les droits administrateur (sudo)"
sudo apt update
sudo apt install -y portaudio19-dev python3-dev ffmpeg pulseaudio-utils libxcb-cursor0

echo ""
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}  Configuration des clés API${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo "L'application supporte deux providers de transcription:"
echo "  1. OpenAI (GPT-4o Transcribe)"
echo "  2. Mistral (Voxtral Mini Transcribe)"
echo ""
echo "Vous pouvez configurer les deux clés maintenant, ou seulement celle que vous comptez utiliser."
echo ""

# Demander le provider par défaut
echo "Quel provider souhaitez-vous utiliser par défaut ?"
echo "  1) OpenAI"
echo "  2) Mistral"
read -p "Votre choix (1 ou 2): " provider_choice

if [ "$provider_choice" = "2" ]; then
    DEFAULT_PROVIDER="mistral"
    echo -e "${GREEN}Provider sélectionné: Mistral${NC}"
else
    DEFAULT_PROVIDER="openai"
    echo -e "${GREEN}Provider sélectionné: OpenAI${NC}"
fi

echo ""

# Demander la clé API OpenAI
read -p "Clé API OpenAI (laissez vide si vous ne l'utilisez pas): " openai_key

# Demander la clé API Mistral
read -p "Clé API Mistral (laissez vide si vous ne l'utilisez pas): " mistral_key

echo ""
echo -e "${BLUE}Création du fichier de configuration .env...${NC}"

# Créer le fichier .env
cat > .env << EOF
# ============================================
# Configuration Voice Transcriptor
# ============================================

# --------------------------------------------
# PROVIDER DE TRANSCRIPTION
# --------------------------------------------
# Choix du provider : 'openai' ou 'mistral'
TRANSCRIPTION_PROVIDER=$DEFAULT_PROVIDER

# --------------------------------------------
# CLÉS API
# --------------------------------------------
EOF

# Ajouter la clé OpenAI si fournie
if [ -n "$openai_key" ]; then
    echo "OPENAI_API_KEY=$openai_key" >> .env
else
    echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
fi

# Ajouter la clé Mistral si fournie
if [ -n "$mistral_key" ]; then
    echo "MISTRAL_API_KEY=$mistral_key" >> .env
else
    echo "MISTRAL_API_KEY=your_mistral_api_key_here" >> .env
fi

# Ajouter le reste de la configuration
cat >> .env << 'EOF'

# --------------------------------------------
# CONFIGURATION AUDIO (optionnel)
# --------------------------------------------
# Taux d'échantillonnage audio (Hz)
# SAMPLE_RATE=44100

# Nombre de canaux audio
# 1 = Mono, 2 = Stéréo
# CHANNELS=1

# --------------------------------------------
# CONFIGURATION MISTRAL (optionnel)
# --------------------------------------------
# Modèle Voxtral à utiliser
# MISTRAL_MODEL=voxtral-mini-latest

# Langue de transcription (optionnel)
# Exemples: fr, en, de, es
# MISTRAL_LANGUAGE=fr

# Context biasing (optionnel)
# MISTRAL_CONTEXT_BIAS=mot1,mot2,mot3
EOF

echo -e "${GREEN}✓ Fichier .env créé avec succès${NC}"

# Rendre les scripts exécutables
chmod +x bin/launch-voice-transcriptor.sh
chmod +x src/main.py

echo ""
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}  Installation terminée !${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo -e "${BLUE}Pour lancer l'application:${NC}"
echo ""
echo "  1. Via le script de lancement:"
echo "     ./bin/launch-voice-transcriptor.sh"
echo ""
echo "  2. Manuellement:"
echo "     source venv/bin/activate"
echo "     python src/main.py"
echo ""
echo -e "${BLUE}Pour changer de provider:${NC}"
echo "  Éditez le fichier .env et modifiez TRANSCRIPTION_PROVIDER"
echo "  Valeurs possibles: openai ou mistral"
echo ""
echo -e "${YELLOW}Note:${NC} Les enregistrements sont sauvegardés dans ~/VoiceRecordings/"
echo -e "${YELLOW}Note:${NC} Les logs sont disponibles dans ~/VoiceRecordings/voice_transcriptor.log"
echo ""

# Vérifier si une clé API est configurée
if [ -z "$openai_key" ] && [ -z "$mistral_key" ]; then
    echo -e "${YELLOW}⚠️  Attention: Aucune clé API n'a été configurée.${NC}"
    echo "   Veuillez éditer le fichier .env et ajouter au moins une clé API"
    echo "   avant de lancer l'application."
    echo ""
fi

echo -e "${GREEN}Bonne utilisation !${NC}"
echo ""

# Ne pas essayer de sourcer .bashrc car on est dans un script
echo -e "${YELLOW}Note:${NC} Si vous souhaitez utiliser les commandes python/pip du venv"
echo "      dans votre shell actuel, exécutez: source venv/bin/activate"
