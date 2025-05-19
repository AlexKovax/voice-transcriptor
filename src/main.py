import sys
import os
import tempfile
import time
import json
import datetime
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QLabel, QMessageBox,
                           QHBoxLayout, QProgressBar, QSizePolicy)
from PyQt6.QtCore import QTimer, Qt, QSize, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QMovie, QFont
import openai
import pyperclip

class AudioRecorder(QMainWindow):
    # Définir des signaux personnalisés
    show_success_signal = pyqtSignal(str)
    show_error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enregistreur Vocal")
        self.setFixedSize(400, 250)  # Augmenté pour accommoder le chemin du fichier
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
        """)
        
        # Configuration audio
        self.sample_rate = 44100
        self.channels = 1
        self.recording = False
        self.audio_frames = []
        self.start_time = 0
        
        # Dossier de sauvegarde des enregistrements
        self.recordings_dir = Path.home() / "VoiceRecordings"
        self.recordings_dir.mkdir(exist_ok=True)
        
        # Chemin du fichier d'enregistrement actuel
        self.current_recording_path = None
        
        # Configuration de l'interface
        self.setup_ui()
        
        # Configuration du timer pour le chronomètre
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Configuration d'OpenAI (à remplacer par votre clé API)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            QMessageBox.critical(
                self, 
                "Erreur", 
                "La clé API OpenAI n'a pas été trouvée. Veuillez définir la variable d'environnement OPENAI_API_KEY."
            )
            sys.exit(1)
    
    def setup_ui(self):
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Conteneur pour le contenu principal (sera remplacé pendant le chargement)
        self.content_widget = QWidget()
        self.main_layout.addWidget(self.content_widget)
        
        # Layout pour le contenu principal
        layout = QVBoxLayout(self.content_widget)
        
        # Affichage du temps
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Conteneur pour les boutons
        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # Boutons
        self.finish_btn = QPushButton("Terminer")
        self.finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #a5d6a7;
            }
        """)
        self.finish_btn.clicked.connect(self.finish_recording)
        
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #ef9a9a;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_recording)
        
        # Ajout des boutons au layout
        button_layout.addWidget(self.finish_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Label pour afficher le chemin du fichier
        self.file_path_label = QLabel()
        self.file_path_label.setObjectName("filePathLabel")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Ajout des widgets au layout principal
        layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.file_path_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Widget de chargement (caché par défaut)
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
        
        loading_layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(self.progress_bar)
        
        # Ajouter le widget de chargement au layout principal
        self.main_layout.addWidget(self.loading_widget)
        self.loading_widget.hide()
        
        # Définir le layout principal
        main_widget.setLayout(self.main_layout)
    
    def start_recording(self):
        """Démarre l'enregistrement audio"""
        self.recording = True
        self.audio_frames = []
        self.start_time = time.time()
        
        # Créer un nom de fichier basé sur la date et l'heure
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_recording_path = self.recordings_dir / f"recording_{timestamp}.wav"
        self.file_path_label.setText(f"Enregistrement en cours : {self.current_recording_path}")
        
        # Démarrer le flux audio
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Démarrer le timer
        self.timer.start(100)  # Mise à jour toutes les 100ms
        self.update_timer()
    
    def audio_callback(self, indata, frames, time, status):
        """Callback appelé à chaque nouveau bloc audio"""
        if self.recording:
            self.audio_frames.append(indata.copy())
    
    def update_timer(self):
        """Met à jour l'affichage du chronomètre"""
        if self.recording:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def show_loading(self, message):
        """Affiche l'écran de chargement avec un message"""
        self.content_widget.hide()
        self.loading_label.setText(message)
        self.loading_label.setStyleSheet("font-size: 14px; color: #555;")
        self.progress_bar.show()
        self.loading_widget.show()
    
    def show_success(self, message, close_delay=1000):
        """Affiche un message de succès et ferme l'application après un délai"""
        self.loading_label.setText(message)
        self.loading_label.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        self.progress_bar.hide()
        QTimer.singleShot(close_delay, self.close)
    
    def finish_recording(self):
        """Termine l'enregistrement et envoie à l'API OpenAI"""
        if not self.recording:
            return
            
        self.stop_recording()
        
        # Désactiver les boutons et afficher le chargement
        self.finish_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.show_loading("Transcription en cours...")
        
        # Utiliser un thread séparé pour éviter de bloquer l'interface
        from threading import Thread
        
        def process_audio():
            tmp_file = None
            try:
                # Sauvegarder dans un fichier temporaire pour l'API
                tmp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                audio_data = np.concatenate(self.audio_frames, axis=0)
                
                # Sauvegarder dans le fichier temporaire pour l'API
                sf.write(tmp_file.name, audio_data, self.sample_rate)
                
                # Sauvegarder une copie dans le dossier des enregistrements
                if self.current_recording_path:
                    try:
                        sf.write(str(self.current_recording_path), audio_data, self.sample_rate)
                        self.file_path_label.setText(f"Enregistrement sauvegardé :\n{self.current_recording_path}")
                    except Exception as e:
                        print(f"Erreur lors de la sauvegarde de l'enregistrement : {e}")
                        self.file_path_label.setText(f"Erreur de sauvegarde, vérifiez les permissions :\n{self.recordings_dir}")
                
                # Envoyer à l'API OpenAI
                with open(tmp_file.name, "rb") as audio_file:
                    response = openai.audio.transcriptions.create(
                        model="gpt-4o-transcribe",
                        file=audio_file
                    )
                
                # Copier le texte dans le presse-papier
                transcription = response.text
                pyperclip.copy(transcription)
                
                # Afficher le message de succès dans le thread principal
                success_msg = "Transcription terminée !"
                if self.current_recording_path:
                    success_msg += f"\nL'audio est sauvegardé ici :\n{self.current_recording_path}"
                self.show_success_signal.emit(success_msg)
                
            except Exception as e:
                error_msg = f"Erreur lors de la transcription : {str(e)}"
                if self.current_recording_path:
                    error_msg += f"\n\nL'enregistrement audio a été sauvegardé ici :\n{self.current_recording_path}"
                self.show_error_signal.emit(error_msg)
            finally:
                # Nettoyer le fichier temporaire
                if tmp_file and os.path.exists(tmp_file.name):
                    try:
                        os.unlink(tmp_file.name)
                    except Exception as e:
                        print(f"Erreur lors de la suppression du fichier temporaire : {e}")
        
        # Démarrer le traitement dans un thread séparé
        self.worker_thread = Thread(target=process_audio, daemon=True)
        self.worker_thread.start()
        
        # Connecter les signaux si ce n'est pas déjà fait
        if not hasattr(self, '_signals_connected'):
            self.show_success_signal.connect(self.show_success)
            self.show_error_signal.connect(self.show_error)
            self._signals_connected = True
    def show_error(self, error_message):
        """Affiche un message d'erreur et ferme l'application"""
        self.loading_label.setText(error_message)
        self.loading_label.setStyleSheet("color: #f44336; font-size: 16px; font-weight: bold;")
        self.progress_bar.hide()
        QTimer.singleShot(1000, self.close)
                
    def cancel_recording(self):
        """Annule l'enregistrement et quitte l'application"""
        if self.recording:
            self.stop_recording()
        self.close()
    
    def stop_recording(self):
        """Arrête l'enregistrement audio"""
        if hasattr(self, 'stream') and self.stream.active:
            self.stream.stop()
            self.stream.close()
        self.recording = False
        self.timer.stop()
    
    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre"""
        self.stop_recording()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Vérifier si une clé API est définie
    if not os.getenv("OPENAI_API_KEY"):
        QMessageBox.critical(
            None,
            "Erreur de configuration",
            "Veuillez définir la variable d'environnement OPENAI_API_KEY avec votre clé API OpenAI."
        )
        sys.exit(1)
    
    # Démarrer l'application
    recorder = AudioRecorder()
    recorder.show()
    recorder.start_recording()  # Démarrer l'enregistrement immédiatement
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
