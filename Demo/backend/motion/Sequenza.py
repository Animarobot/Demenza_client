
class Sequenza:

    def __init__(self, movimenti):

        if len(movimenti) < 2: raise Exception("sequence is too short!")

        self.servo_occupati = set()
        self.movimenti = []
        self.movimento_corrente = 0

        for movimento in movimenti:

            if movimento:

                self.servo_occupati = self | movimento
                self.movimenti.append(movimento)

        self.running = False

    def restart(self, durata=None, **kwargs):

        if not self.running:

            self.durata_movimento = 0

            for movimento in self.movimenti:
                
                movimento.restart(**kwargs)
                self.durata_movimento += movimento.durata_movimento

            self.times = 1 if durata==None else durata//self.durata_movimento

            self.counter = 0

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

            if self.counter == self.times: self.running = False

            movimento = self.movimenti[self.movimento_corrente]

            if movimento.is_running(): next(movimento)

            else:
                
                self.movimento_corrente += 1
                if self.movimento_corrente == len(self.movimenti):
                    self.movimento_corrente = 0
                    self.counter += 1
                    for movimento in self.movimenti: movimento.restart()
