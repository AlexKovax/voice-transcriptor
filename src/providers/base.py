"""
Classe abstraite pour les providers de transcription
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class TranscriptionProvider(ABC):
    """Classe abstraite pour les providers de transcription audio"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None

    @abstractmethod
    def initialize(self) -> None:
        """Initialise le client API"""
        pass

    @abstractmethod
    def transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio en texte

        Args:
            audio_file_path: Chemin vers le fichier audio

        Returns:
            Texte transcrit

        Raises:
            Exception: En cas d'erreur de transcription
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du provider"""
        pass

    def check_file_size(
        self, file_path: Path, max_size_mb: float = 25.0
    ) -> tuple[bool, str]:
        """
        Vérifie si le fichier ne dépasse pas la taille maximale

        Returns:
            Tuple (is_valid, warning_message)
        """
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return (
                False,
                f"⚠️ ATTENTION: Le fichier fait {file_size_mb:.1f} Mo et dépasse la limite de {max_size_mb} Mo",
            )
        return True, ""
