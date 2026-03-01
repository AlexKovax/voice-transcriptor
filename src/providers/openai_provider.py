"""
Provider de transcription OpenAI (GPT-4o Transcribe)
"""

from pathlib import Path
import openai
from .base import TranscriptionProvider


class OpenAIProvider(TranscriptionProvider):
    """Provider de transcription utilisant l'API OpenAI"""

    MODEL = "gpt-4o-transcribe"
    MAX_FILE_SIZE_MB = 25.0

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def initialize(self) -> None:
        """Initialise le client OpenAI"""
        openai.api_key = self.api_key
        self.client = openai

    def transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio avec OpenAI

        Args:
            audio_file_path: Chemin vers le fichier audio (MP3 recommandé)

        Returns:
            Texte transcrit
        """
        # Vérifier la taille du fichier
        is_valid, warning = self.check_file_size(audio_file_path, self.MAX_FILE_SIZE_MB)
        if not is_valid:
            # On continue mais on log l'avertissement
            print(warning)

        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.MODEL, file=audio_file
            )

        return response.text

    @property
    def name(self) -> str:
        return f"OpenAI ({self.MODEL})"
