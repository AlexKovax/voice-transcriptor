# 🎤 Voice Transcriber

Une application légère et efficace pour enregistrer de l'audio et le transcrire en temps réel en utilisant l'API OpenAI. Parfaite pour les notes vocales, les interviews ou la dictée.


## 📚 Table des matières

- [Fonctionnalités ✨](#-fonctionnalités)
- [Prérequis 📋](#-prérequis)
- [Installation rapide 🚀](#-installation-rapide)
- [Utilisation 🎯](#-utilisation)
  - [Lancement manuel](#lancement-manuel)
  - [Configuration du raccourci clavier](#configuration-du-raccourci-clavier-ubuntu)
  - [Utilisation de l'application](#utilisation-de-lapplication)
  - [Options supplémentaires](#options-supplémentaires)
- [Configuration ⚙️](#%EF%B8%8F-configuration)
  - [Variables d'environnement](#variables-denvironnement)
  - [Options de personnalisation](#options-de-personnalisation)
- [Dépannage 🛠️](#-dépannage)
- [Sécurité 🔒](#-sécurité)
- [Contribution 🤝](#-contribution)
- [Licence 📄](#-licence)
- [Création de l'application](#création-de-lapplication)

## ✨ Fonctionnalités

- 🎙️ Enregistrement audio en un clic
- ⏱️ Affichage du temps d'enregistrement
- 🚀 Transcription via l'API OpenAI (modèle GPT-4o)
- 📋 Copie automatique dans le presse-papier
- 🎨 Interface utilisateur simple et intuitive
- ⚡ Fermeture automatique après transcription

## 📋 Prérequis

- Python 3.8 ou supérieur
- Compte [OpenAI](https://platform.openai.com/) avec clé API valide
- Système d'exploitation : Ubuntu (testé sur 20.04/22.04)
- Accès à un microphone fonctionnel
- Connexion Internet (pour l'API OpenAI)

## 🚀 Installation rapide

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/voice-transcriptor.git
   cd voice-transcriptor
   ```

2. **Créer et activer un environnement virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   .\venv\Scripts\activate  # Windows
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la clé API OpenAI** :
   ```bash
   # Pour la session actuelle
   export OPENAI_API_KEY='votre_cle_api_openai_ici'
   
   # Pour le rendre permanent (ajouter à ~/.bashrc ou ~/.bash_profile)
   echo "export OPENAI_API_KEY='votre_cle_api_openai_ici'" >> ~/.bashrc
   source ~/.bashrc
   ```

## 🎯 Utilisation

### Lancement manuel

```bash
python src/main.py
```

### Configuration du raccourci clavier (Ubuntu)

Pour un accès rapide, configurez un raccourci clavier :

1. **Rendre le script de lancement exécutable** :
   ```bash
   chmod +x bin/launch-voice-transcriptor.sh
   ```

2. **Créer un raccourci clavier personnalisé** :
   - Ouvrez les Paramètres système (Settings)
   - Allez dans "Clavier" (Keyboard)
   - Faites défiler vers le bas et cliquez sur "Raccourcis personnalisés" (Custom Shortcuts)
   - Cliquez sur le bouton "+" en bas
   - Remplissez les champs :
     - Nom : `Voice Transcriber`
     - Commande : `/chemin/vers/voice-transcriptor/bin/launch-voice-transcriptor.sh`
   - Cliquez sur "Appliquer" (Apply)
   - Cliquez sur "Désactivé" (Disabled) à droite du nouveau raccourci
   - Appuyez sur la combinaison de touches de votre choix (par exemple, `Ctrl+Alt+V`)

### Utilisation de l'application

1. **Démarrage** :
   - L'application démarre automatiquement l'enregistrement
   - Parlez clairement dans votre microphone

2. **Actions disponibles** :
   - 🟢 **Terminer** : Arrête l'enregistrement et lance la transcription
   - 🔴 **Annuler** : Annule l'enregistrement et quitte

3. **Après la transcription** :
   - Le texte est automatiquement copié dans le presse-papier
   - Un message de confirmation s'affiche
   - L'application se ferme automatiquement après 1 seconde

### Options supplémentaires

#### Créer un raccourci sur le bureau

```bash
cat > ~/Desktop/Voice-Transcriber.desktop << 'EOL'
[Desktop Entry]
Version=1.0
Type=Application
Name=Voice Transcriber
Comment=Lance l'application de transcription vocale
Exec=/chemin/vers/voice-transcriptor/bin/launch-voice-transcriptor.sh
Icon=audio-input-microphone
Terminal=false
Categories=Audio;Utility;
EOL

chmod +x ~/Desktop/Voice-Transcriber.desktop
```

#### Démarrer automatiquement au démarrage

1. Ouvrez "Applications au démarrage" (Startup Applications)
2. Cliquez sur "Ajouter" (Add)
3. Remplissez les champs :
   - Nom : `Voice Transcriber`
   - Commande : `/chemin/vers/voice-transcriptor/bin/launch-voice-transcriptor.sh`
   - Commentaire : "Application de transcription vocale"
4. Cliquez sur "Ajouter" (Add)

## ⚙️ Configuration

### Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | Votre clé API OpenAI | *Obligatoire* |

### Options avancées

Vous pouvez modifier les paramètres suivants dans le fichier `src/main.py` :

- `sample_rate` : Taux d'échantillonnage audio (par défaut : 44100 Hz)
- `channels` : Nombre de canaux audio (1 pour mono, 2 pour stéréo)
- Délai de fermeture après transcription

## 🛠️ Dépannage

### Problèmes courants

1. **Microphone non détecté** :
   ```bash
   sudo apt-get install portaudio19-dev python3-dev
   ```

2. **Erreur de clé API manquante** :
   - Vérifiez que la variable d'environnement est bien définie
   - Redémarrez votre terminal après l'avoir définie

3. **Erreurs de dépendances** :
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Problèmes d'interface graphique** :
   ```bash
   sudo apt-get install libxcb-cursor0
   ```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos modifications (`git commit -m 'Ajouter une fonctionnalité incroyable'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [OpenAI](https://openai.com/) pour leur API de transcription
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) pour l'interface graphique
- [SoundDevice](https://python-sounddevice.readthedocs.io/) pour la capture audio

---

<div align="center">
  Fait avec ❤️ pour une expérience de transcription fluide
</div>
## Utilisation

1. Lancez l'application :
   ```bash
   python src/main.py
   ```

2. L'application démarre immédiatement l'enregistrement audio.

3. Utilisez les boutons :
   - **Terminer** : Arrête l'enregistrement, envoie l'audio à l'API OpenAI et copie la transcription dans le presse-papier
   - **Annuler** : Annule l'enregistrement et quitte l'application

## Fonctionnalités

- Enregistrement audio en temps réel
- Interface graphique simple et intuitive
- Affichage du temps d'enregistrement
- Transcription via l'API OpenAI
- Copie automatique de la transcription dans le presse-papier

## Dépannage

### Problèmes d'enregistrement audio
- Vérifiez que votre microphone est correctement branché et configuré
- Assurez-vous que l'application a les permissions nécessaires pour accéder au microphone

### Erreurs d'API
- Vérifiez que votre clé API OpenAI est valide et correctement configurée
- Assurez-vous d'avoir un accès Internet

## Licence

Ce projet est sous licence MIT.

## Création de l'application

Cette application a été entièrement créée avec l'assistant AI Windsurf. Vous pouvez retrouvez les prompts dans PROMPTS.md