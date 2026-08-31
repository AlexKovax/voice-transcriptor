"""
Provider de transcription OpenAI (GPT-4o Transcribe)
"""

import logging
from pathlib import Path

from openai import OpenAI

from .base import TranscriptionProvider


logger = logging.getLogger(__name__)


class OpenAIProvider(TranscriptionProvider):
    """Provider de transcription utilisant l'API OpenAI"""

    MODEL = "gpt-4o-transcribe"
    MAX_FILE_SIZE_MB = 25.0

    def __init__(self, api_key: str, timeout: float = 120.0):
        super().__init__(api_key)
        self.timeout = timeout
        self.initialize()

    def initialize(self) -> None:
        """
        Initialise le client OpenAI.

        max_retries=0 : les retries sont gérés de manière uniforme dans
        TranscriptionProvider.transcribe() (backoff commun aux providers).
        """
        self.client = OpenAI(
            api_key=self.api_key, timeout=self.timeout, max_retries=0
        )

    @classmethod
    def from_config(cls, config) -> "OpenAIProvider":
        return cls(
            api_key=config.OPENAI_API_KEY, timeout=config.TRANSCRIPTION_TIMEOUT
        )

    def _transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio avec OpenAI

        Args:
            audio_file_path: Chemin vers le fichier audio (MP3 recommandé)

        Returns:
            Texte transcrit
        """
        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.MODEL, file=audio_file
            )

        return response.text

    @property
    def name(self) -> str:
        return f"OpenAI ({self.MODEL})"
