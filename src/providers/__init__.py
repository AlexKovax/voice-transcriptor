"""
Factory pour créer les providers de transcription
"""

from typing import Type
from ..config import Config
from .base import TranscriptionProvider
from .openai_provider import OpenAIProvider
from .mistral_provider import MistralProvider


# Mapping des providers disponibles
PROVIDERS = {
    "openai": OpenAIProvider,
    "mistral": MistralProvider,
}


def create_provider(config: Config = None) -> TranscriptionProvider:
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
        from ..config import Config

        config = Config()

    provider_name = config.TRANSCRIPTION_PROVIDER

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Provider non supporté: {provider_name}. "
            f"Providers disponibles: {', '.join(PROVIDERS.keys())}"
        )

    provider_class = PROVIDERS[provider_name]

    # Créer le provider avec les bons paramètres
    if provider_name == "openai":
        provider = provider_class(api_key=config.OPENAI_API_KEY)
    elif provider_name == "mistral":
        provider = provider_class(
            api_key=config.MISTRAL_API_KEY,
            model=config.MISTRAL_MODEL,
            language=config.MISTRAL_LANGUAGE,
            context_bias=config.MISTRAL_CONTEXT_BIAS,
        )
    else:
        raise ValueError(f"Provider non supporté: {provider_name}")

    # Initialiser le client
    provider.initialize()

    return provider


def get_available_providers() -> list[str]:
    """Retourne la liste des providers disponibles"""
    return list(PROVIDERS.keys())
