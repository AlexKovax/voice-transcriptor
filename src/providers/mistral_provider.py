"""
Provider de transcription Mistral (Voxtral Mini Transcribe)
"""

from pathlib import Path
from typing import Optional
from mistralai import Mistral
from providers.base import TranscriptionProvider
from config import Config


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

    def initialize(self) -> None:
        """Initialise le client Mistral"""
        self.client = Mistral(api_key=self.api_key)

    def transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio avec Mistral Voxtral

        Args:
            audio_file_path: Chemin vers le fichier audio

        Returns:
            Texte transcrit
        """
        # Vérifier la taille du fichier
        is_valid, warning = self.check_file_size(audio_file_path, self.MAX_FILE_SIZE_MB)
        if not is_valid:
            print(warning)

        # Préparer les paramètres de la requête
        request_params = {
            "model": self.model,
            "file": {
                "content": open(audio_file_path, "rb"),
                "file_name": audio_file_path.name,
            },
        }

        # Ajouter la langue si spécifiée
        if self.language:
            request_params["language"] = self.language

        # Ajouter le context biasing si spécifié
        if self.context_bias:
            request_params["context_bias"] = self.context_bias

        try:
            response = self.client.audio.transcriptions.complete(**request_params)
            return response.text
        finally:
            # Fermer le fichier
            request_params["file"]["content"].close()

    @property
    def name(self) -> str:
        return f"Mistral ({self.model})"
