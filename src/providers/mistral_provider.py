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
    ):
        super().__init__(api_key)
        self.model = model
        self.language = language
        self.context_bias = context_bias
        self.initialize()

    def initialize(self) -> None:
        """Initialise le client Mistral"""
        self.client = Mistral(api_key=self.api_key)

    @classmethod
    def from_config(cls, config) -> "MistralProvider":
        return cls(
            api_key=config.MISTRAL_API_KEY,
            model=config.MISTRAL_MODEL,
            language=config.MISTRAL_LANGUAGE,
            context_bias=config.MISTRAL_CONTEXT_BIAS,
        )

    def transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio avec Mistral Voxtral

        Args:
            audio_file_path: Chemin vers le fichier audio

        Returns:
            Texte transcrit
        """
        is_valid, warning = self.check_file_size(audio_file_path, self.MAX_FILE_SIZE_MB)
        if not is_valid:
            logger.warning(warning)

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
