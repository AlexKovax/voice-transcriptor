"""
Interface graphique pour l'enregistreur audio
"""

import os
import tempfile
import time
import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from threading import Thread
from pydub import AudioSegment

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QHBoxLayout,
    QProgressBar,
    QSizePolicy,
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont

from providers.base import TranscriptionProvider
from utils import format_duration, get_recordings_dir
import pyperclip
import logging


logger = logging.getLogger(__name__)


class AudioRecorder(QMainWindow):
    """Application d'enregistrement et transcription audio"""

    # Signaux personnalisés
    show_success_signal = pyqtSignal(str)
    show_error_signal = pyqtSignal(str)

    def __init__(
        self,
        provider: TranscriptionProvider,
        sample_rate: int = 44100,
        channels: int = 1,
    ):
        super().__init__()

        self.provider = provider
        self.sample_rate = sample_rate
        self.channels = channels

        # État de l'enregistrement
        self.recording = False
        self.audio_frames = []
        self.start_time = 0
        self.current_recording_path: Path = None
        self.stream = None
        self.worker_thread: Thread = None

        # Configuration de l'interface
        self._setup_window()
        self._setup_ui()
        self._setup_timers()

        logger.info(f"AudioRecorder initialisé avec le provider: {provider.name}")

    def _setup_window(self):
        """Configure la fenêtre principale"""
        self.setWindowTitle("Enregistreur Vocal")
        self.setFixedSize(400, 280)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            #filePathLabel {
                font-size: 10px;
                color: #666;
                background-color: #f0f0f0;
                padding: 4px;
                border-radius: 3px;
                margin-top: 10px;
            }
            #providerLabel {
                font-size: 9px;
                color: #888;
                margin-bottom: 5px;
            }
        """)

    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Conteneur pour le contenu principal
        self.content_widget = QWidget()
        self.main_layout.addWidget(self.content_widget)

        layout = QVBoxLayout(self.content_widget)

        # Label du provider
        self.provider_label = QLabel(f"Provider: {self.provider.name}")
        self.provider_label.setObjectName("providerLabel")
        self.provider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.provider_label)

        # Affichage du temps
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.time_label)

        # Conteneur pour les boutons
        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # Bouton Terminer
        self.finish_btn = QPushButton("Terminer")
        self.finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #a5d6a7;
            }
        """)
        self.finish_btn.clicked.connect(self.finish_recording)

        # Bouton Annuler
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #ef9a9a;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_recording)

        button_layout.addWidget(self.finish_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addWidget(self.button_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label pour afficher le chemin du fichier
        self.file_path_label = QLabel()
        self.file_path_label.setObjectName("filePathLabel")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.file_path_label)

        # Widget de chargement (caché par défaut)
        self._setup_loading_widget()

        # Définir le layout principal
        main_widget.setLayout(self.main_layout)

        # Connecter les signaux
        self.show_success_signal.connect(self._show_success_message)
        self.show_error_signal.connect(self._show_error_message)

    def _setup_loading_widget(self):
        """Configure le widget de chargement"""
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setContentsMargins(0, 0, 0, 0)
        loading_layout.setSpacing(15)

        # Indicateur de chargement
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 14px; color: #555;")

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e0e0e0;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)

        loading_layout.addWidget(
            self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter
        )
        loading_layout.addWidget(self.progress_bar)

        self.main_layout.addWidget(self.loading_widget)
        self.loading_widget.hide()

    def _setup_timers(self):
        """Configure les timers"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer_display)

    def start_recording(self):
        """Démarre l'enregistrement audio"""
        try:
            self.recording = True
            self.audio_frames = []
            self.start_time = time.time()

            # Créer un nom de fichier
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            recordings_dir = get_recordings_dir()
            self.current_recording_path = recordings_dir / f"recording_{timestamp}.wav"
            self.file_path_label.setText(
                f"Enregistrement en cours...\n{self.current_recording_path.name}"
            )

            # Démarrer le flux audio
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
            )
            self.stream.start()

            # Démarrer le timer
            self.timer.start(100)  # Mise à jour toutes les 100ms
            self._update_timer_display()

            logger.info(f"Enregistrement démarré: {self.current_recording_path}")

        except Exception as e:
            logger.error(f"Erreur au démarrage de l'enregistrement: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Erreur", f"Impossible de démarrer l'enregistrement:\n{str(e)}"
            )
            self.close()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback appelé à chaque bloc audio"""
        if self.recording:
            self.audio_frames.append(indata.copy())

    def _update_timer_display(self):
        """Met à jour l'affichage du chronomètre"""
        if self.recording:
            elapsed = int(time.time() - self.start_time)
            self.time_label.setText(format_duration(elapsed))

    def stop_recording(self):
        """Arrête l'enregistrement audio"""
        if self.stream and self.stream.active:
            self.stream.stop()
            self.stream.close()
        self.recording = False
        self.timer.stop()
        logger.info("Enregistrement arrêté")

    def finish_recording(self):
        """Termine l'enregistrement et lance la transcription"""
        if not self.recording:
            return

        self.stop_recording()

        # Désactiver les boutons et afficher le chargement
        self.finish_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self._show_loading("Transcription en cours...")

        # Lancer le traitement dans un thread séparé
        self.worker_thread = Thread(target=self._process_audio, daemon=True)
        self.worker_thread.start()

    def _process_audio(self):
        """Traite l'audio et lance la transcription (dans un thread séparé)"""
        tmp_wav_file = None
        tmp_mp3_file = None

        try:
            # Concaténer les frames audio
            audio_data = np.concatenate(self.audio_frames, axis=0)

            # Sauvegarder dans un fichier temporaire WAV
            tmp_wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(tmp_wav_file.name, audio_data, self.sample_rate)

            # Sauvegarder une copie dans le dossier des enregistrements
            if self.current_recording_path:
                try:
                    sf.write(
                        str(self.current_recording_path), audio_data, self.sample_rate
                    )
                    logger.info(f"Audio sauvegardé: {self.current_recording_path}")
                except Exception as e:
                    logger.error(f"Erreur de sauvegarde: {e}")

            # Convertir en MP3 pour la transcription
            tmp_mp3_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            audio = AudioSegment.from_wav(tmp_wav_file.name)
            audio.export(tmp_mp3_file.name, format="mp3", bitrate="128k")

            # Vérifier la taille du fichier
            mp3_path = Path(tmp_mp3_file.name)
            is_valid, warning = self.provider.check_file_size(mp3_path)
            if not is_valid:
                logger.warning(warning)

            # Transcrire avec le provider
            logger.info(f"Démarrage de la transcription avec {self.provider.name}")
            transcription = self.provider.transcribe(mp3_path)

            # Copier dans le presse-papier
            pyperclip.copy(transcription)

            # Préparer le message de succès
            success_msg = "✓ Transcription terminée !"
            if not is_valid:
                success_msg += f"\n{warning}"
            success_msg += f"\n\nTexte copié dans le presse-papier"
            success_msg += f"\n({len(transcription)} caractères)"

            if self.current_recording_path:
                success_msg += f"\n\nAudio sauvegardé:\n{self.current_recording_path}"

            logger.info(f"Transcription réussie: {len(transcription)} caractères")
            self.show_success_signal.emit(success_msg)

        except Exception as e:
            error_msg = f"✗ Erreur lors de la transcription:\n{str(e)}"
            if self.current_recording_path:
                error_msg += (
                    f"\n\nL'audio a été sauvegardé:\n{self.current_recording_path}"
                )

            logger.error(f"Erreur de transcription: {e}", exc_info=True)
            self.show_error_signal.emit(error_msg)

        finally:
            # Nettoyer les fichiers temporaires
            for temp_file in [tmp_wav_file, tmp_mp3_file]:
                if temp_file and os.path.exists(temp_file.name):
                    try:
                        os.unlink(temp_file.name)
                    except Exception as e:
                        logger.error(f"Erreur suppression fichier temporaire: {e}")

    def _show_loading(self, message: str):
        """Affiche l'écran de chargement"""
        self.content_widget.hide()
        self.loading_label.setText(message)
        self.loading_label.setStyleSheet("font-size: 14px; color: #555;")
        self.progress_bar.show()
        self.loading_widget.show()

    def _show_success_message(self, message: str):
        """Affiche un message de succès"""
        self.loading_label.setText(message)
        self.loading_label.setStyleSheet(
            "color: #4CAF50; font-size: 14px; font-weight: bold;"
        )
        self.progress_bar.hide()
        QTimer.singleShot(2000, self.close)  # Fermer après 2 secondes

    def _show_error_message(self, message: str):
        """Affiche un message d'erreur"""
        self.loading_label.setText(message)
        self.loading_label.setStyleSheet(
            "color: #f44336; font-size: 14px; font-weight: bold;"
        )
        self.progress_bar.hide()
        QTimer.singleShot(3000, self.close)  # Fermer après 3 secondes

    def cancel_recording(self):
        """Annule l'enregistrement"""
        if self.recording:
            self.stop_recording()
        logger.info("Enregistrement annulé par l'utilisateur")
        self.close()

    def closeEvent(self, a0):
        """Gère la fermeture de la fenêtre"""
        self.stop_recording()
        logger.info("Application fermée")
        a0.accept()
