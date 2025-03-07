from threading import Thread, Event
import os
import random
import asyncio
import re
from backend.AudioPlayer import play_audio
from backend.VAD import record_audio_until_silence
from frontend.GUI import App
from backend.Utils import read_file, create_dict_number_sorted
from backend.AnimaRobotClient import AnimaRobotClient
import warnings
warnings.filterwarnings("ignore")



AUDIO_FOLDER ="./Demo/backend/Audio"
IMAGES_PATH = "./Demo/Images"
OUTPUT_FILE = "./Demo/backend/output.txt"

class Controller:

    def __init__(self):

        self.click_event = Event()
        self.app = App(f"{IMAGES_PATH}", self.click_event)
        self.running=False
        _, self.file_lines=create_dict_number_sorted(read_file("./Demo/backend/sentence.txt"))
        self.line_pattern = '^\d+(?:\.\d*)?\s*'
        self.client = AnimaRobotClient("localhost:9000")
        print(self.client.init())

    def loop(self):

    # Avvia un thread per controllare il click_event senza bloccare la GUI
        thread = Thread(target=self.check_click_event, daemon=True)
        thread.start()

        self.app.mainloop()  # Avvia la GUI nel thread principale


    async def run_logic(self):

            self.running=True
            all_files = os.listdir(AUDIO_FOLDER)
            # Filtra solo i file .mp3 (ignorando maiuscole/minuscole)
            keys, mp3_files = create_dict_number_sorted([f for f in all_files if f.lower().endswith(".mp3")])
            for num in keys:
                variants = mp3_files[num]
                num_versions = len(variants)
                # Genera un indice casuale nel range delle versioni disponibili
                version_index = random.randint(0, num_versions - 1)
                # Seleziona il file corrispondente a questo indice
                chosen_file = variants[version_index]
                self.app.update_center_image(f"{IMAGES_PATH}/homepage.png", True)
                audio_file = os.path.join(AUDIO_FOLDER, chosen_file)

                if not os.path.exists(audio_file):
                    print(f"File {audio_file} non trovato. Saltato.")
                    continue
                
                if "image" in chosen_file:
                    rand=random.randint(1,2)
                    self.app.update_center_image(f"{IMAGES_PATH}/combined_{rand}.png", False)

                print(f"Riproduzione del file: {audio_file}")
                self.app.update_conversation(re.sub(self.line_pattern, '', self.file_lines[num][version_index]), True)
                play_audio(audio_file)
                
                if "_" not in chosen_file:
                    continue

                transcription = await record_audio_until_silence(client=self.client)

                with open(OUTPUT_FILE, "a") as f:
                    f.write(f"Risposta relativa alla domanda {chosen_file}: {transcription}\n")

                # Stampa la trascrizione
                self.app.update_conversation(transcription, False)

                # Opzionale: Salva la trascrizione in un file di output
                self.running=False

    def check_click_event(self):
        """Controlla periodicamente se il pulsante è stato premuto e avvia process_click()."""
        while True:
            self.click_event.wait()  # Aspetta finché l'utente non preme il pulsante
            self.click_event.clear()  # Resetta l'evento

            if self.running:
                continue

            print("⚡ Il pulsante è stato premuto! Avvio process_click()...")

            # Avvia il thread per eseguire process_click() senza bloccare il controllo dell'evento
            asyncio.run(self.run_logic())
    
