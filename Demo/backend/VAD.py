import numpy as np
import wave
import pyaudio
from webrtcvad import Vad
from threading import Event

vad=Vad()
audio_chunk_size = 2560

vad_size = 320

vocal_activity_lenght = audio_chunk_size//vad_size
record_duration_seconds = 10

record_pause_seconds = 1
frame_rate=16000

min_record_duration_seconds = 2
record_duration = int(frame_rate / audio_chunk_size * record_duration_seconds)
min_record_duration = int(frame_rate / audio_chunk_size * min_record_duration_seconds)
record_pause = int(frame_rate / audio_chunk_size * record_pause_seconds)

def save_audio_to_file(audio_data, sample_rate, filename):
    """Salva i dati audio in un file WAV."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit per campione
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())  # Scrive i dati audio

async def record_audio_until_silence(client, event, sample_rate=16000, channels=1,):
    """Registra audio dal microfono fino a quando non c'è più parlato."""

    p = pyaudio.PyAudio()
    event.clear()

    try:

        # Apre una connessione websocket con il server animarobot per il servizio di asr

        websocket = await client.connect("/api/asr")

        # Apre lo streaming audio

        print("record")

        # Configura il flusso audio
        stream = p.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=audio_chunk_size)

        i, j = 0, 0
        
        while i < record_duration and j < record_pause:
            # Legge il flusso audio
            frame = stream.read(audio_chunk_size)

            await websocket.send(frame)

            voice = sum([vad.is_speech(frame[j*vad_size:(j+1)*vad_size],frame_rate) for j in range(vocal_activity_lenght)]) == vocal_activity_lenght

            i += 1

            if i > min_record_duration: j = 0 if voice else j+1

        print("stop asr")

        await websocket.send("/end")
        # Ferma la registrazione
        stream.stop_stream()
        stream.close()
        p.terminate()

        results = await websocket.recv()
        event.set()
        return results, event

    except Exception as e:
        print("Errore nell'esecuzione di asyncio:", e)
        return ""
