
from time import monotonic

class Personalizzato:

    def __init__(self, servo, nome_servo, segnale):

        self.servo = servo["controller"]
        self.min_angle = servo["posizione_minima"]
        self.max_angle = servo["posizione_massima"]

        prec = segnale[0][0]

        for posizione, attesa in segnale:

            if abs(posizione - prec) > 1: raise Exception("step is too high!")
            else: prec = posizione
            if posizione < self.min_angle or posizione > self.max_angle: raise Exception("position is invalid!")
            if attesa < 0.005: raise Exception("delta time is too low!")

        self.segnale = segnale
        self.servo_occupati = {nome_servo}

        self.soglia = 30

        self.running = False

        self.clock = monotonic()

    def restart(self, durata=None, **kwargs):

        if not self.running:

            self.running = True

            self.durata_movimento = 0

            self.indice = 0

            for posizione, attesa in self.segnale: self.durata_movimento += attesa

            self.last_position = round(self.servo.angle)

            self.clock = monotonic()

    def is_running(self):

        return self.running

    def __iter__(self):

        return self

    def __and__(self, other):

        return self.servo_occupati & other.servo_occupati

    def __or__(self, other):

        return self.servo_occupati | other.servo_occupati

    def __next__(self):
        
        if self.running:

            now = monotonic()

            if now > self.clock:

                if self.indice < len(self.segnale):
                    
                    new_position, wait = self.segnale[self.indice]

                    self.indice += 1

                    distanza = new_position - self.last_position

                    if abs(distanza) > self.soglia:

                        new_position = self.last_position + (- self.soglia if distanza < 0 else self.soglia)
                        
                    self.servo.angle = new_position
                    self.last_position = new_position

                    self.clock = now + wait

                else: self.running = False