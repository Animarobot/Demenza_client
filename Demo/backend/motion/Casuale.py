
from random import randint

class Casuale:

    def __init__(self, movimenti):

        self.servo_occupati = set()

        self.movimenti = []

        for movimento in movimenti:

            if movimento:

                self.servo_occupati = self | movimento

                self.movimenti.append(movimento)

        self.running = False

    def restart(self, durata=None, **kwargs):

        if not self.running:

            self.movimento_corrente = randint(0,len(self.movimenti)-1)

            self.movimenti[self.movimento_corrente].restart(durata, **kwargs)

            self.durata_movimento = self.movimenti[self.movimento_corrente].durata_movimento

            self.running = True

    def __and__(self, other):

        return self.servo_occupati & other.servo_occupati

    def __or__(self, other):

        return self.servo_occupati | other.servo_occupati

    def is_running(self):

        return self.running

    def __iter__(self):

        return self

    def __next__(self):
        
        if self.running:

            if self.movimenti[self.movimento_corrente].is_running(): next(self.movimenti[self.movimento_corrente])
            else: self.running = False
