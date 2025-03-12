
class Parallelo:

    def __init__(self, movimenti):

        self.servo_occupati = set()

        self.movimenti = []

        for movimento in movimenti:

            if movimento:

                if self & movimento != set(): raise Exception("motion composition is invalid!")

                self.servo_occupati = self | movimento

                self.movimenti.append(movimento)

        self.running = False

    def restart(self, durata=None, **kwargs):

        if not self.running:

            for movimento in self.movimenti: movimento.restart(durata, **kwargs)

            self.durata_movimento = max(self.movimenti, key = lambda x: x.durata_movimento).durata_movimento

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

            self.running = False

            for movimento in self.movimenti:

                if movimento.is_running(): next(movimento)

                self.running = movimento.is_running() or self.running
