"""
Classe abstraite pour les providers de transcription

Fournit :
- le contrat (_transcribe) que chaque provider doit implémenter ;
- la boucle publique transcribe() avec retries sur les erreurs transitoires ;
- la conversion des erreurs brutes en messages compréhensibles.
"""

import logging
import math
import os
import random
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Erreur de transcription avec un message adapté à l'utilisateur"""


# Messages associés aux codes d'erreur HTTP courants
_STATUS_MESSAGES = {
    400: "Requête invalide (fichier audio corrompu ou format non supporté ?)",
    401: "Clé API invalide ou expirée. Vérifiez votre fichier .env.",
    403: "Accès refusé. Votre clé API n'a pas les droits nécessaires.",
    404: "Modèle ou ressource introuvable. Vérifiez le nom du modèle dans .env.",
    413: "Fichier audio trop volumineux pour l'API.",
    422: "Requête refusée par l'API (paramètres invalides ?).",
    429: "Limite de requêtes atteinte (rate limit). Réessayez dans quelques instants.",
}


def _get_status_code(error: Exception) -> Optional[int]:
    """
    Extrait le code HTTP d'une exception, quel que soit le SDK.

    - openai.APIStatusError expose .status_code
    - mistralai SDKError expose .raw_response.status_code
    """
    status_code = getattr(error, "status_code", None)
    if isinstance(status_code, int):
        return status_code
    response = getattr(error, "response", None) or getattr(error, "raw_response", None)
    status = getattr(response, "status_code", None)
    if isinstance(status, int):
        return status
    return None


def _is_transient_error(error: Exception) -> bool:
    """Détermine si l'erreur est transitoire et mérite un nouvel essai"""
    import httpx

    # Erreurs réseau / timeouts / connexion interrompue
    if isinstance(
        error,
        (httpx.TimeoutException, httpx.TransportError, ConnectionError, TimeoutError),
    ):
        return True

    status = _get_status_code(error)
    # 408 (requête expirée), 429 (rate limit), 5xx (erreurs serveur)
    return status is not None and (status == 408 or status == 429 or status >= 500)


def _friendly_message(error: Exception) -> str:
    """Convertit une exception brute en message compréhensible pour l'utilisateur"""
    status = _get_status_code(error)
    if status is not None:
        base_msg = _STATUS_MESSAGES.get(status)
        if base_msg:
            return f"{base_msg} (erreur HTTP {status})"
        if status >= 500:
            return f"Erreur du serveur de transcription (HTTP {status})."
        return f"Erreur de l'API de transcription (HTTP {status}): {error}"
    return f"Erreur lors de la transcription: {error}"


class TranscriptionProvider(ABC):
    """Classe abstraite pour les providers de transcription audio"""

    # Configuration des retries (appliqués uniquement aux erreurs transitoires)
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 1.5  # secondes, délai doublé à chaque tentative

    # Taille max des fichiers acceptée par les API de transcription (Mo)
    MAX_FILE_SIZE_MB = 25.0
    # Durée d'un chunk lors du découpage des longs enregistrements.
    # 10 min ≈ 9,4 Mo en MP3 128k, marge confortable sous la limite des API.
    CHUNK_DURATION_MS = 600_000

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None

    @abstractmethod
    def initialize(self) -> None:
        """Initialise le client API"""
        pass

    @abstractmethod
    def _transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio (appel API brut, sans retry)

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

    def transcribe(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio.

        Si le fichier dépasse la taille acceptée par l'API (MAX_FILE_SIZE_MB),
        il est automatiquement découpé en chunks MP3 transcrits séparément
        puis concaténés.

        Args:
            audio_file_path: Chemin vers le fichier audio

        Returns:
            Texte transcrit

        Raises:
            TranscriptionError: avec un message adapté à l'utilisateur
        """
        is_valid, warning = self.check_file_size(audio_file_path, self.MAX_FILE_SIZE_MB)
        if is_valid:
            return self._transcribe_with_retry(audio_file_path)

        logger.warning(warning)
        return self._transcribe_chunked(audio_file_path)

    def _transcribe_chunked(self, audio_file_path: Path) -> str:
        """
        Découpe un fichier audio trop volumineux en chunks et les transcrit
        séquentiellement. Les fichiers temporaires sont toujours nettoyés.
        """
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(str(audio_file_path))
        except Exception as e:
            # Découpage impossible (ffmpeg absent, fichier illisible...) :
            # tenter quand même le fichier complet, l'API refusera peut-être
            logger.error("Découpage impossible (%s), tentative sur le fichier complet", e)
            return self._transcribe_with_retry(audio_file_path)

        total_ms = len(audio)
        chunk_ms = self.CHUNK_DURATION_MS
        n_chunks = math.ceil(total_ms / chunk_ms)
        logger.info(
            "Fichier de %.1f min découpé en %d chunk(s) de %d min",
            total_ms / 60000,
            n_chunks,
            chunk_ms // 60000,
        )

        tmp_files: list[Path] = []
        texts: list[str] = []
        try:
            for i in range(n_chunks):
                chunk = audio[i * chunk_ms : (i + 1) * chunk_ms]
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tmp.close()
                tmp_files.append(Path(tmp.name))
                chunk.export(str(tmp.name), format="mp3", bitrate="128k")
                try:
                    texts.append(self._transcribe_with_retry(tmp_files[-1]).strip())
                except TranscriptionError as e:
                    raise TranscriptionError(
                        f"Échec de la transcription du chunk {i + 1}/{n_chunks}:\n{e}"
                    ) from e
                logger.info("Chunk %d/%d transcrit", i + 1, n_chunks)
            return " ".join(t for t in texts if t)
        finally:
            for tmp_file in tmp_files:
                try:
                    os.unlink(tmp_file)
                except OSError as e:
                    logger.error("Erreur suppression chunk temporaire: %s", e)

    def _transcribe_with_retry(self, audio_file_path: Path) -> str:
        """
        Transcrit un fichier audio, avec retries sur les erreurs transitoires.

        Effectue jusqu'à MAX_RETRIES tentatives avec backoff exponentiel
        en cas d'erreur réseau, de rate limit ou d'erreur serveur.
        Les erreurs définitives (401, 404, ...) échouent immédiatement.

        Args:
            audio_file_path: Chemin vers le fichier audio

        Returns:
            Texte transcrit

        Raises:
            TranscriptionError: avec un message adapté à l'utilisateur
        """
        last_error: Optional[Exception] = None
        attempt = 0

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return self._transcribe(audio_file_path)
            except Exception as e:
                last_error = e
                if attempt >= self.MAX_RETRIES or not _is_transient_error(e):
                    break
                wait = self.RETRY_BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(
                    0, 0.5
                )
                logger.warning(
                    "Tentative %d/%d échouée (%s), nouvel essai dans %.1fs",
                    attempt,
                    self.MAX_RETRIES,
                    e,
                    wait,
                )
                time.sleep(wait)

        logger.error(
            "Transcription échouée après %d tentative(s)", attempt, exc_info=last_error
        )
        raise TranscriptionError(_friendly_message(last_error)) from last_error

    def check_file_size(
        self, file_path: Path, max_size_mb: float = 25.0
    ) -> tuple[bool, str]:
        """
        Vérifie si le fichier ne dépasse pas la taille maximale

        Returns:
            Tuple (is_valid, warning_message)
        """
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
        except OSError as e:
            return False, f"⚠️ Impossible de lire le fichier audio: {e}"
        if file_size_mb > max_size_mb:
            return (
                False,
                f"⚠️ ATTENTION: Le fichier fait {file_size_mb:.1f} Mo et dépasse la limite de {max_size_mb} Mo",
            )
        return True, ""
