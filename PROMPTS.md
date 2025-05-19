# Prompts pour réaliser cette application avec Windsurf

## Prompt 1

Nous démarrons un nouveau projet python. Tu es un expert et tu vas me proposer un plan pour réaliser ce que je souhaite. J'aimerais un petit programme très simple qui quand il est lancé démarre immédiatement à enregistrer l'entrée audio par défaut. Il doit également afficher une interface graphique très simple qui affiche le temps écoulé et 2 boutons : pour terminer l'enregistrement et un pour l'annuler.
Quand le bouton terminer est appuyé, le fichier audio enregistré doit être envoyé à l'API de transcription d'openai. Voici le nom du modèle à utiliser : gpt-4o-transcribe. L'API doit renvoyer le texte. Celui-ci doit être ajouté au presse papier et l'application doit se terminer.
Je précise que ce programme doit être utilisé sur ubuntu.
Je veux que tu me proposes un plan détaillé de ce que tu vas faire. N'écris pas encore de code.

## Prompt 2

Oui implémente le plan

## Prompt 3


J'ai eu cette erreur en lançant l'application : 

```
(venv) alex@Nano:~/Dev/voice-transcriptor$ python src/main.py
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: offscreen, vkkhrdisplay, wayland-egl, eglfs, linuxfb, minimalegl, xcb, vnc, minimal, wayland.

Abandon (core dumped)
(venv)
```

## Prompt 4

J'ai cette erreur : 

```
Veuillez définir la variable d'environnement OPENAI_API_KEY avec votre clé API OpenAI.

```

## Prompt 5

Super cela fonctionne bien. Quand la transcription est effectuée, j'aimerais que tu affiches un message de confirmation dans la fenetre principale avec les boutons puis que tu fermes l'application. Pas besoin de modale de confirmation, cela ajoute un clic en plus

## Prompt 6


Cela fonctionne mais je n'ai pas eu de message de confirmation.
Je te propose le fonctionnement suivant.
Une fois le bouton terminé appuyé, j'aimerais que les boutons disparaissent et qu'un loader apparaisse avec un message "transcription en cours".
Puis quand la transcription est récupée, on affiche "Transcription terminée". Puis au bout de 2 secondes, l'application se ferme.

## Prompt 7

C'est parfait. Réduit à 1 seconde le délai avant la fermeture de l'application

## Prompt 8

J'aimerais que tu améliores la documentation dans le fichier README

