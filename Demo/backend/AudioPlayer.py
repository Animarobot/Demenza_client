from pydub.playback import play
from pydub import AudioSegment


# Aggiungi uno stacco al file di output per ogni nuova esecuzione
"""Converte un file MP3 in WAV."""

# Itera sui file numerati da 1 a 22
def play_audio(audio_file):        
    # Carica il file MP3
    audio = AudioSegment.from_file(audio_file)

    # Riproduci l'audio
    play(audio)
