"""
Configuration de l'application Voice Transcriptor.
Charge les variables depuis le fichier .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Essayer de charger depuis le répertoire courant
    load_dotenv()


class Config:
    """Configuration de l'application"""

    # Provider de transcription
    TRANSCRIPTION_PROVIDER = os.getenv("TRANSCRIPTION_PROVIDER", "openai").lower()

    # Clés API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    # Configuration audio
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "44100"))
    CHANNELS = int(os.getenv("CHANNELS", "1"))

    # Configuration Mistral
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "voxtral-mini-latest")
    MISTRAL_LANGUAGE = os.getenv("MISTRAL_LANGUAGE")
    MISTRAL_CONTEXT_BIAS = os.getenv("MISTRAL_CONTEXT_BIAS")

    # Validation
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """
        Valide la configuration et retourne (is_valid, error_message)
        """
        if cls.TRANSCRIPTION_PROVIDER not in ["openai", "mistral"]:
            return (
                False,
                f"Provider invalide: {cls.TRANSCRIPTION_PROVIDER}. Utilisez 'openai' ou 'mistral'",
            )

        if cls.TRANSCRIPTION_PROVIDER == "openai":
            if (
                not cls.OPENAI_API_KEY
                or cls.OPENAI_API_KEY == "your_openai_api_key_here"
            ):
                return (
                    False,
                    "OPENAI_API_KEY non définie. Veuillez la définir dans le fichier .env",
                )

        elif cls.TRANSCRIPTION_PROVIDER == "mistral":
            if (
                not cls.MISTRAL_API_KEY
                or cls.MISTRAL_API_KEY == "your_mistral_api_key_here"
            ):
                return (
                    False,
                    "MISTRAL_API_KEY non définie. Veuillez la définir dans le fichier .env",
                )

        return True, ""

    @classmethod
    def get_api_key(cls) -> str:
        """Retourne la clé API appropriée selon le provider"""
        if cls.TRANSCRIPTION_PROVIDER == "openai":
            return cls.OPENAI_API_KEY or ""
        return cls.MISTRAL_API_KEY or ""
