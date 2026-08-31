"""
Provider de transcription Mistral (Voxtral Mini Transcribe)
"""

import logging
from pathlib import Path
from typing import Optional

from mistralai import Mistral

from .base import TranscriptionProvider


logger = logging.getLogger(__name__)


class MistralProvider(TranscriptionProvider):
    """Provider de transcription utilisant l'API Mistral (Voxtral)"""

    MAX_FILE_SIZE_MB = 25.0

    def __init__(
        self,
        api_key: str,
        model: str = "voxtral-mini-latest",
        language: Optional[str] = None,
        context_bias: Optional[str] = None,
        timeout: float = 120.0,
    ):
        super().__init__(api_key)
        self.model = model
        self.language = language
        self.context_bias = context_bias
        self.timeout = timeout
        self.initialize()

    def initialize(self) -> None:
        """Initialise le client Mistral (timeout en millisecondes côté SDK)"""
        self.client = Mistral(api_key=self.api_key, timeout_ms=int(self.timeout * 1000))

    @classmethod
    def from_config(cls, config) -> "MistralProvider":
        return cls(
            api_key=config.MISTRAL_API_KEY,
            model=config.MISTRAL_MODEL,
            language=config.MISTRAL_LANGUAGE,
            context_bias=config.MISTRAL_CONTEXT_BIAS,
            timeout=config.TRANSCRIPTION_TIMEOUT,
        )

    def _transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio avec Mistral Voxtral

        Args:
            audio_file_path: Chemin vers le fichier audio

        Returns:
            Texte transcrit
        """
        request_params = {
            "model": self.model,
        }
        if self.language:
            request_params["language"] = self.language
        if self.context_bias:
            request_params["context_bias"] = self.context_bias

        with open(audio_file_path, "rb") as audio_file:
            request_params["file"] = {
                "content": audio_file,
                "file_name": audio_file_path.name,
            }
            response = self.client.audio.transcriptions.complete(**request_params)

        return response.text

    @property
    def name(self) -> str:
        return f"Mistral ({self.model})"
