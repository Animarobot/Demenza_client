from board import SCL, SDA
import busio

from adafruit_motor.servo import Servo
from adafruit_pca9685 import PCA9685

from time import monotonic

from json import load

from backend.motion.Oscillazione import Oscillazione
from backend.motion.Parallelo import Parallelo
from backend.motion.Sequenza import Sequenza
from backend.motion.Casuale import Casuale
from backend.motion.Alternativa import Alternativa
from backend.motion.Vai import Vai
from backend.motion.Personalizzato import Personalizzato

class ServoController:

    def __init__(self):

        i2c = busio.I2C(SCL, SDA)

        self.pca = PCA9685(i2c)

        self.pca.frequency = 50

        self.servo = self.read_json("servo")
        movimenti = self.read_json("movimenti")

        
        for nome_servo in self.servo.keys():

            self.servo[nome_servo]["controller"] = Servo(self.pca.channels[self.servo[nome_servo]["canale"]])

            if self.servo[nome_servo]["posizione_minima"] <= self.servo[nome_servo]["posizione_iniziale"] <= self.servo[nome_servo]["posizione_massima"]:
                self.servo[nome_servo]["controller"].angle = self.servo[nome_servo]["posizione_iniziale"]
            else: raise Exception("servo position is invalid!")


        self.movimento = self.parse("start",movimenti)
        self.listening = self.parse("listening",movimenti)

        for nome_servo in self.servo.keys(): print(nome_servo+":",self.servo[nome_servo]["controller"].angle)

        print("")


    def parse(self, nome_movimento, movimenti):

        if nome_movimento:

            movimento = movimenti[nome_movimento].copy()

            if movimento["tipo_movimento"] == "oscillazione":

                del movimento["tipo_movimento"]

                return Oscillazione(self.servo[movimento["nome_servo"]], **movimento)

            if movimento["tipo_movimento"] == "vai":

                del movimento["tipo_movimento"]

                return Vai(self.servo[movimento["nome_servo"]], **movimento)

            if movimento["tipo_movimento"] == "personalizzato":

                del movimento["tipo_movimento"]

                return Personalizzato(self.servo[movimento["nome_servo"]], **movimento)

            if movimento["tipo_movimento"] == "parallelo":

                del movimento["tipo_movimento"]

                return Parallelo([self.parse(sotto_movimento, movimenti) for sotto_movimento in movimento["movimenti"]])

            if movimento["tipo_movimento"] == "sequenza":

                del movimento["tipo_movimento"]

                return Sequenza([self.parse(sotto_movimento, movimenti) for sotto_movimento in movimento["movimenti"]])

            if movimento["tipo_movimento"] == "casuale":

                del movimento["tipo_movimento"]

                return Casuale([self.parse(sotto_movimento, movimenti) for sotto_movimento in movimento["movimenti"]])

            if movimento["tipo_movimento"] == "alternativa":

                del movimento["tipo_movimento"]

                return Alternativa(movimento["chiave"], {parametro: self.parse(movimento["movimenti"][parametro], movimenti) for parametro in movimento["movimenti"]})
            
        else: return None


    def read_json(self, nome_file):

        try:

            file = open(nome_file+".json")

            data = load(file)

        except: return None

        finally: file.close()

        return data

    
    def run(self, tono, durata):
        
        start = monotonic()

        self.movimento.restart(durata, tono=tono)

        while self.movimento.is_running(): next(self.movimento)

        print("\nDurata effettiva:",int((monotonic()-start)*100)/100)

    def run_listening(self, durata=None):

        if self.listening.is_running(): next(self.listening)
        else: self.listening.restart(durata)
    
    def deinit(self):

        self.pca.deinit()