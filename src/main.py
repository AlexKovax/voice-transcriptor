"""
Voice Transcriptor - Application d'enregistrement et transcription audio

Cette application permet d'enregistrer de l'audio et de le transcrire
en utilisant différents providers (OpenAI GPT-4o ou Mistral Voxtral).

Configuration via le fichier .env
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QMessageBox

from config import Config
from providers import create_provider
from audio_recorder import AudioRecorder
from utils import setup_logging


def main():
    """Point d'entrée principal de l'application"""

    # Créer l'application Qt en premier (une seule instance)
    app = QApplication(sys.argv)

    # Initialiser le logging
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Démarrage de Voice Transcriptor")

    # Valider la configuration
    is_valid, error_message = Config.validate()
    if not is_valid:
        logger.error(f"Configuration invalide: {error_message}")
        QMessageBox.critical(
            None,
            "Erreur de configuration",
            f"{error_message}\n\n"
            "Veuillez créer un fichier .env à partir de .env.example\n"
            "et configurer vos clés API.",
        )
        sys.exit(1)

    logger.info(f"Provider sélectionné: {Config.TRANSCRIPTION_PROVIDER}")
    logger.info(f"Sample rate: {Config.SAMPLE_RATE} Hz")
    logger.info(f"Channels: {Config.CHANNELS}")

    try:
        # Créer le provider de transcription
        provider = create_provider()
        logger.info(f"Provider initialisé: {provider.name}")

        # Créer et afficher l'enregistreur
        recorder = AudioRecorder(
            provider=provider, sample_rate=Config.SAMPLE_RATE, channels=Config.CHANNELS
        )
        recorder.show()
        recorder.start_recording()

        logger.info("Application prête - démarrage de l'enregistrement")

        # Lancer la boucle principale
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        QMessageBox.critical(None, "Erreur", f"Une erreur est survenue:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
