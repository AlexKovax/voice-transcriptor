"""
Provider de transcription OpenAI (GPT-4o Transcribe)
"""

import logging
from pathlib import Path

import openai

from .base import TranscriptionProvider


logger = logging.getLogger(__name__)


class OpenAIProvider(TranscriptionProvider):
    """Provider de transcription utilisant l'API OpenAI"""

    MODEL = "gpt-4o-transcribe"
    MAX_FILE_SIZE_MB = 25.0

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.initialize()

    def initialize(self) -> None:
        """Initialise le client OpenAI"""
        openai.api_key = self.api_key
        self.client = openai

    @classmethod
    def from_config(cls, config) -> "OpenAIProvider":
        return cls(api_key=config.OPENAI_API_KEY)

    def transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio avec OpenAI

        Args:
            audio_file_path: Chemin vers le fichier audio (MP3 recommandé)

        Returns:
            Texte transcrit
        """
        is_valid, warning = self.check_file_size(audio_file_path, self.MAX_FILE_SIZE_MB)
        if not is_valid:
            logger.warning(warning)

        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.MODEL, file=audio_file
            )

        return response.text

    @property
    def name(self) -> str:
        return f"OpenAI ({self.MODEL})"
