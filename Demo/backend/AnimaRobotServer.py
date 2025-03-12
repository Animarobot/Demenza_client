
from asyncio import Future, run, sleep, gather, wait_for, create_task, TimeoutError

from threading import Event

#from .ServoController import ServoController


class AnimaRobotServer:

    def __init__(self, controller):
        
        self.controller= controller
        self.servo_controller = None

        print(self.controller.listening)
        self.in_attesa=True


    def muovi(self):

        try:
            while self.in_attesa:
                if self.controller.data_movimenti == "start":
                    self.in_attesa = False

            while True:

                if self.controller.data_movimenti == "listening":
                    self.servo_controller.run_listening()
                    self.controller.listening.wait()
                
                else:
                    # Verifica se ci sono più di due valori
                    values = self.controller.data_movimenti.split(";")
                    if len(values) > 2:
                        # Rimuovi il primo valore
                        values = values[1:]
                        print(f"Dati modificati: {values}")

                    try:
                        tono, durata = values
                        print(f"(T={durata}, V={tono})")
                        self.servo_controller.run(tono, float(durata))
                    except ValueError as e:
                        # Logga un errore se ancora non è nel formato corretto
                        print(f"Errore nel formato dei dati ricevuti: {self.controller.data_movimenti}")

        except Exception as e:
            print(f"Errore generale: {e}")
