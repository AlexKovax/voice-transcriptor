"""
Factory pour créer les providers de transcription
"""

from .base import TranscriptionProvider
from .openai_provider import OpenAIProvider
from .mistral_provider import MistralProvider


# Mapping des providers disponibles
PROVIDERS = {
    "openai": OpenAIProvider,
    "mistral": MistralProvider,
}


def create_provider(config=None) -> TranscriptionProvider:
    """
    Crée et initialise un provider de transcription selon la configuration

    Args:
        config: Configuration de l'application (utilise Config par défaut)

    Returns:
        Instance de TranscriptionProvider initialisée

    Raises:
        ValueError: Si le provider n'est pas supporté
    """
    if config is None:
        from config import Config
        config = Config

    provider_name = config.TRANSCRIPTION_PROVIDER

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Provider non supporté: {provider_name}. "
            f"Providers disponibles: {', '.join(PROVIDERS.keys())}"
        )

    return PROVIDERS[provider_name].from_config(config)


def get_available_providers() -> list[str]:
    """Retourne la liste des providers disponibles"""
    return list(PROVIDERS.keys())
