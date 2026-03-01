# 🎤 Voice Transcriber

Une application légère et efficace pour enregistrer de l'audio et le transcrire en temps réel. Supporte OpenAI (GPT-4o) et Mistral (Voxtral). Parfaite pour les notes vocales, les interviews ou la dictée.

## ✨ Fonctionnalités

- 🎙️ Enregistrement audio en un clic
- ⏱️ Affichage du temps d'enregistrement
- 🚀 **Double support transcription** :
  - OpenAI GPT-4o Transcribe
  - Mistral Voxtral Mini Transcribe
- 📋 Copie automatique dans le presse-papier
- 🎨 Interface utilisateur simple et intuitive
- ⚡ Fermeture automatique après transcription
- 📝 **Système de logs** pour le débogage

## 📋 Prérequis

- Python 3.8 ou supérieur
- Ubuntu (testé sur 20.04/22.04/24.04)
- Accès à un microphone fonctionnel
- Connexion Internet

### Dépendances système

```bash
sudo apt update
sudo apt install -y portaudio19-dev python3-dev ffmpeg libxcb-cursor0
```

## 🚀 Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/alexkovax/voice-transcriptor.git
cd voice-transcriptor
```

### 2. Lancer l'installation automatique

```bash
chmod +x setup.sh
./setup.sh
```

Le script va :
- Créer un environnement virtuel Python
- Installer toutes les dépendances
- Vous demander quel provider utiliser (OpenAI ou Mistral)
- Créer le fichier de configuration `.env`

### 3. Configuration manuelle (alternative)

Si vous préférez configurer manuellement :

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier et éditer la configuration
cp .env.example .env
# Éditez .env avec vos clés API
```

## ⚙️ Configuration

L'application utilise un fichier `.env` pour la configuration. Exemple :

```bash
# Choix du provider
TRANSCRIPTION_PROVIDER=mistral  # ou 'openai'

# Clés API
OPENAI_API_KEY=sk-votre-cle-openai
MISTRAL_API_KEY=votre-cle-mistral

# Options audio (optionnel)
SAMPLE_RATE=44100
CHANNELS=1

# Options Mistral (optionnel)
MISTRAL_MODEL=voxtral-mini-latest
MISTRAL_LANGUAGE=fr
```

### Obtenir une clé API

- **OpenAI** : https://platform.openai.com/api-keys
- **Mistral** : https://console.mistral.ai/

## 🎯 Utilisation

### Lancement rapide

```bash
./bin/launch-voice-transcriptor.sh
```

### Lancement manuel

```bash
source venv/bin/activate
python src/main.py
```

### Configuration du raccourci clavier (Ubuntu)

1. Ouvrez **Paramètres** → **Clavier** → **Raccourcis personnalisés**
2. Cliquez sur **+** pour ajouter un raccourci
3. Remplissez :
   - **Nom** : Voice Transcriber
   - **Commande** : `/chemin/complet/vers/voice-transcriptor/bin/launch-voice-transcriptor.sh`
4. Cliquez sur **Désactivé** et choisissez votre combinaison (ex: `Ctrl+Alt+V`)

### Utilisation de l'application

1. **Lancement** : L'enregistrement démarre automatiquement
2. **Terminer** : Arrête et transcrit l'audio
3. **Annuler** : Quitte sans transcription
4. **Résultat** : Le texte est copié dans le presse-papier

Les enregistrements sont sauvegardés dans `~/VoiceRecordings/`

## 🛠️ Dépannage

### Voir les logs

```bash
cat ~/VoiceRecordings/voice_transcriptor.log
```

### Problèmes courants

**Erreur "Unauthorized" ou "401"**
- Vérifiez votre clé API dans le fichier `.env`
- Assurez-vous que la variable `TRANSCRIPTION_PROVIDER` correspond à votre clé

**Microphone non détecté**
```bash
sudo apt install portaudio19-dev pulseaudio-utils
```

**Problème d'interface graphique (Qt)**
```bash
sudo apt install libxcb-cursor0
```

**Changer de provider**

Éditez le fichier `.env` :
```bash
TRANSCRIPTION_PROVIDER=mistral  # ou openai
```

## 🏗️ Architecture

```
src/
├── main.py              # Point d'entrée
├── config.py            # Configuration (.env)
├── audio_recorder.py    # Interface graphique
├── utils.py             # Utilitaires
└── providers/
    ├── base.py          # Classe abstraite
    ├── openai_provider.py
    └── mistral_provider.py
```

## 📄 Licence

Ce projet est sous licence MIT.

---

<div align="center">
  Fait avec ❤️ pour une expérience de transcription fluide
</div>
