"""
Utilitaires pour l'application Voice Transcriptor
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional


def setup_logging(logs_dir: Optional[Path] = None) -> logging.Logger:
    """
    Configure le logging pour l'application

    Args:
        logs_dir: Répertoire pour les fichiers de log (défaut: ~/VoiceRecordings)

    Returns:
        Logger configuré
    """
    if logs_dir is None:
        logs_dir = Path.home() / "VoiceRecordings"

    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "voice_transcriptor.log"

    # Configurer le logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


def format_duration(seconds: int) -> str:
    """Formate une durée en secondes au format MM:SS"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def get_recordings_dir() -> Path:
    """Retourne le répertoire de sauvegarde des enregistrements"""
    recordings_dir = Path.home() / "VoiceRecordings"
    recordings_dir.mkdir(exist_ok=True)
    return recordings_dir


def get_unique_path(path: Path) -> Path:
    """
    Retourne un chemin de fichier unique : si le fichier existe déjà
    (deux enregistrements dans la même seconde, par exemple), ajoute
    un suffixe _1, _2... avant l'extension.
    """
    if not path.exists():
        return path
    for i in range(1, 1000):
        candidate = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not candidate.exists():
            return candidate
    # Filet de sécurité quasi impossible à atteindre
    return path.with_name(f"{path.stem}_{int(time.time())}{path.suffix}")
