"""
Configuration de l'application Voice Transcriptor.
Charge les variables depuis le fichier .env

Les valeurs numériques sont parsées de manière défensive : une valeur
malformée ne fait pas planter l'application, elle génère une erreur de
validation affichée à l'utilisateur (via Config.validate()).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Erreurs de parsing collectées au chargement (valeurs .env malformées).
# Défini au niveau module car une classe ne peut pas se référencer
# elle-même dans son propre corps de définition.
_parse_errors: list[str] = []

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
    TRANSCRIPTION_PROVIDER = os.getenv("TRANSCRIPTION_PROVIDER", "openai").lower().strip()

    # Clés API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    # Configuration Mistral
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "voxtral-mini-latest")
    MISTRAL_LANGUAGE = os.getenv("MISTRAL_LANGUAGE")
    MISTRAL_CONTEXT_BIAS = os.getenv("MISTRAL_CONTEXT_BIAS")

    @staticmethod
    def _get_int(name: str, default: int, min_value: int, max_value: int) -> int:
        """
        Lit une variable d'environnement entière de manière défensive.

        En cas de valeur malformée ou hors limites, enregistre une erreur
        de validation et retourne la valeur par défaut.
        """
        raw = os.getenv(name)
        if raw is None or not raw.strip():
            return default
        try:
            value = int(raw.strip())
        except ValueError:
            _parse_errors.append(f'{name} invalide: "{raw}" (nombre entier attendu)')
            return default
        if not (min_value <= value <= max_value):
            _parse_errors.append(
                f"{name}={value} hors des limites acceptées [{min_value}, {max_value}]"
            )
            return default
        return value

    SAMPLE_RATE = _get_int("SAMPLE_RATE", 44100, 8000, 192000)
    CHANNELS = _get_int("CHANNELS", 1, 1, 2)
    TRANSCRIPTION_TIMEOUT = _get_int("TRANSCRIPTION_TIMEOUT", 120, 5, 600)

    # Durée maximale d'enregistrement en secondes (0 = illimité).
    # Protège la mémoire et la taille des fichiers API.
    MAX_RECORDING_SECONDS = _get_int("MAX_RECORDING_SECONDS", 1800, 0, 14400)

    # Valeurs de clés API manifestement non configurées (placeholder du .env.example)
    _PLACEHOLDER_KEYS = {"your_openai_api_key_here", "your_mistral_api_key_here"}

    # Validation
    @classmethod
    def validate(cls) -> tuple[bool, str]:
        """
        Valide la configuration et retourne (is_valid, error_message).

        Agrège toutes les erreurs trouvées (parsing + cohérence) au lieu
        de s'arrêter à la première.
        """
        errors: list[str] = list(_parse_errors)

        if cls.TRANSCRIPTION_PROVIDER not in ["openai", "mistral"]:
            errors.append(
                f"Provider invalide: {cls.TRANSCRIPTION_PROVIDER}. "
                "Utilisez 'openai' ou 'mistral'"
            )
        elif cls.TRANSCRIPTION_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY in cls._PLACEHOLDER_KEYS:
                errors.append(
                    "OPENAI_API_KEY non définie. Veuillez la définir dans le fichier .env"
                )
        else:  # mistral
            if not cls.MISTRAL_API_KEY or cls.MISTRAL_API_KEY in cls._PLACEHOLDER_KEYS:
                errors.append(
                    "MISTRAL_API_KEY non définie. Veuillez la définir dans le fichier .env"
                )

        if errors:
            return False, "\n".join(f"- {e}" for e in errors)
        return True, ""

    @classmethod
    def get_api_key(cls) -> str:
        """Retourne la clé API appropriée selon le provider"""
        if cls.TRANSCRIPTION_PROVIDER == "openai":
            return cls.OPENAI_API_KEY or ""
        return cls.MISTRAL_API_KEY or ""
