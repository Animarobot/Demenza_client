
from time import monotonic

class Vai:

    def __init__(self, servo, nome_servo, delta_time, destinazione):

        self.servo = servo["controller"]
        self.servo_occupati = {nome_servo}
        if destinazione < servo["posizione_minima"]: destinazione = servo["posizione_minima"]
        elif destinazione > servo["posizione_massima"]: destinazione = servo["posizione_massima"]

        self.delta_time = delta_time
        
        self.start_position = round(servo["controller"].angle)
        self.last_position = self.start_position

        self.direzione = -1 if destinazione < self.last_position else 1

        self.destinazione = destinazione

        numero_passi = abs(destinazione-self.last_position)
        self.durata_movimento = self.delta_time*numero_passi

        self.running = False

    
    def restart(self, durata=None, **kwargs):

        if not self.running and self.last_position != self.destinazione:

            self.running = True

            self.clock = monotonic() + self.delta_time

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
                
                new_position = self.last_position + self.direzione

                self.servo.angle = new_position
                self.last_position = new_position
                self.clock = now + self.delta_time

                if self.last_position == self.destinazione: self.running = False