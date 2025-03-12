
from time import monotonic

class Oscillazione:

    def __init__(self, servo, nome_servo, delta_time, direzione, ampiezza, attesa_fine_corsa, attesa_iniziale, oneside, inversione):

        if direzione != -1 and direzione != 1: raise Exception("direction is invalid!")

        if delta_time < 0.01: raise Exception("delta time is too low!")

        self.servo_occupati = {nome_servo}
        ampiezza_massima = servo["posizione_massima"]-servo["posizione_minima"]
        self.offset = int(min(max(ampiezza,0.1),1)*ampiezza_massima//2)

        self.servo = servo["controller"]
        self.delta_time = delta_time
        self.direzione = direzione
        self.oneside = oneside
        self.inversione = inversione

        self.attesa_fine_corsa = attesa_fine_corsa
        self.attesa_iniziale = attesa_iniziale

        self.real_min_angle = servo["posizione_minima"]
        self.real_max_angle = servo["posizione_massima"]

        self.running = False

    
    def restart(self, durata=None, **kwargs):

        if not self.running:

            self.start_position = int(self.servo.angle) + 1
            self.last_position = self.start_position

            if self.oneside: 
                
                if self.direzione > 0: self.min_angle = self.start_position
                else: self.max_angle = self.start_position


            if self.oneside:

                if self.direzione > 0:

                    new_max = self.last_position + self.offset
                    new_min = self.last_position
                else:
                    new_max = self.last_position
                    new_min = self.last_position - self.offset

            else:

                new_max = self.last_position + self.offset
                new_min = self.last_position - self.offset

            if new_max > self.real_max_angle:
                
                self.min_angle = new_min - (new_max-self.real_max_angle)
                self.max_angle = self.real_max_angle

            elif new_min < self.real_min_angle:
                
                self.min_angle = self.real_min_angle
                self.max_angle = new_max - (new_min-self.real_min_angle)

            else:
                
                self.min_angle = new_min
                self.max_angle = new_max
            
            numero_passi = self.max_angle-self.min_angle

            if self.min_angle < self.start_position < self.max_angle:

                self.durata_movimento = 2*(self.attesa_fine_corsa+self.delta_time*numero_passi) + self.attesa_iniziale

            else: self.durata_movimento = 2*(self.delta_time*numero_passi) + self.attesa_iniziale + self.attesa_fine_corsa

            self.times = 1 if durata==None else durata//self.durata_movimento

            self.counter = 0
            self.running = True
            self.on_start = True

        else: self.running = False

    def is_running(self):

        return self.running

    def __iter__(self):

        return self

    def __and__(self, other):

        return self.servo_occupati & other.servo_occupati

    def __or__(self, other):

        return self.servo_occupati | other.servo_occupati

    def __next__(self):

        if self.on_start:
            
            self.clock = monotonic() + self.attesa_iniziale
            self.on_start = False

        if self.running:

            if self.counter//2 == self.times: self.running = False

            now = monotonic()

            if now > self.clock:

                if self.min_angle < self.last_position < self.max_angle:

                    self.last_position += self.direzione
                    self.servo.angle = self.last_position
                    self.clock = now + self.delta_time
                    
                elif self.min_angle >= self.last_position:
                    
                    self.last_position = self.min_angle + 1
                    self.servo.angle = self.last_position
                    self.direzione = 1
                    self.clock = now + self.delta_time + (self.attesa_fine_corsa if self.min_angle < self.start_position else 0)
                
                elif self.max_angle <= self.last_position:

                    self.last_position = self.max_angle - 1
                    self.servo.angle = self.last_position
                    self.direzione = -1
                    self.clock = now + self.delta_time + (self.attesa_fine_corsa if self.max_angle > self.start_position else 0)
                
                if self.last_position == self.start_position:
                    
                    if self.counter > 0 and self.counter%2 == 0:

                        self.clock += self.attesa_iniziale
                        if self.inversione: self.direzione = -self.direzione

                    self.counter += (1 if self.min_angle < self.start_position < self.max_angle else 2)