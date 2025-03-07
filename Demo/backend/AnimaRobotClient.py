
from requests import get, post
from pickle import loads
from websockets import connect

# La classe implementa il client animarobot
# Gestisce il meccanismo di autenticazione necessario per
# accedere ai servizi forniti dal server
# I servizi consistono in asr, analisi video, sintesi vocale, sintesi dei movimenti, chatbot

# Nel caso ci si connetta ad un host locale (localhost)
# sostituire le sigle https e wss con http e ws
# I protocolli di default usati per i server locali sono infatti http e ws

class AnimaRobotClient:

    def __init__(self, host):

        # Indirizzo del server (senza specificare il protocollo usato)
        # Può essere l'indirizzo di un server online o un indirizzo della rete locale
        
        self.host = host

    # Autenticazione client
    # Date le credenziali specificate come parametri
    # viene richiesta l'autenticazione al server
    # Se le credenziali sono corrette, il server restituisce un token di autenticazione (JWT token)
    # Il token viene allegato ad ogni richiesta HTTP (POST, GET, ...) e websocket
    # Vedere la documentazione del server per maggiori informazioni

    # Download dei dati necessari al funzionamento dell'applicazione
    # Questi dati consistono nella posizione iniziale dei servomotori e nelle immagini usate per la grafica
    # I dati possono differire per ogni utente

    def init(self):
            
        response = get("http://"+self.host+"/api/start")
        print("aiuto")
        if response.status_code != 200: raise Exception
        return loads(response.text.encode("latin-1"))

    # Connessione autenticata con JWT token ad un canale websocket

    async def connect(self, path):

        return await connect("ws://"+self.host+path)

    