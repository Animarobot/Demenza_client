from tkinter import Tk, Canvas, Frame, Text, Scrollbar, Label
from PIL import Image, ImageTk
from threading import Event
from time import sleep
from setproctitle import setproctitle

setproctitle("Demo")

class App(Tk):

    # Istanzia una finestra

    def __init__(self, data, click_event):

        # Costruttore superclasse

        super().__init__()

        self.click_event = click_event

        self.homepage_path = f"{data}/homepage.png"  # Percorso dell'immagine principale
        self.logo_path = f"{data}/logo.png"            # Percorso del logo

        self.homepage_max_width=800
        self.homepage_max_height=800

        self.resizable(False, False)
        self.title("Demo")

        try:
            self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
            self.canvas_width = int(self.width * 0.75)  # Il canvas occupa il 75% della larghezza dello schermo

            # Creazione del canvas principale (75% dello schermo)
            self.canvas = Canvas(self, bg="white", width=self.canvas_width, height=self.height, bd=0, highlightthickness=0)
            self.canvas.place(x=0, y=0)

            # Impostazione della finestra
            self.geometry(f"{self.width}x{self.height}")

            # Calcolo del centro del canvas
            center_x = self.canvas_width // 2
            center_y = self.height // 2

            # Carica e ridimensiona l'immagine principale in modo che si adatti al canvas
            self.homepage_image = self.load_and_resize_image(self.homepage_path, self.homepage_max_width, self.homepage_max_height)
            self.homepage_image_id = self.canvas.create_image(center_x, center_y, image=self.homepage_image, anchor="center")

            # Carica e ridimensiona il logo (ad es. in una dimensione di 100x100)
            self.logo_image = self.load_and_resize_image(self.logo_path, 200, 200)
            self.canvas.create_image(10, 10, image=self.logo_image, anchor="nw")

            self.canvas.bind("<Button-1>", self.on_canvas_click)

            # Creazione dell'area conversazione sulla destra
            self.create_chat_area()

        except Exception as e:
            print(f"Errore durante l'inizializzazione della GUI: {e}")

    def create_chat_area(self):
        """Crea l'area per la conversazione con scrollbar funzionante."""
        self.chat_frame = Frame(self, bg="lightgray")
        self.chat_frame.place(x=self.canvas_width, y=0, width=self.width * 0.25, height=self.height-100)

        # Creazione del container per gestire lo scrolling
        container = Frame(self.chat_frame, bg="lightgray")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # Creazione della Canvas per lo scrolling
        self.chat_canvas = Canvas(container, bg="lightgray", highlightthickness=0)
        scrollbar = Scrollbar(container, orient="vertical", command=self.chat_canvas.yview)
        self.scrollable_frame = Frame(self.chat_canvas, bg="lightgray")

        # Configurazione dello scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")
            )
        )

        self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        # Layout della canvas e scrollbar
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Messaggio di benvenuto
        self.update_conversation("Conversazione avviata...", True)
        self.update_conversation("Benvenuto!", False)
    
    def update_conversation(self, new_text, sender):
        """Aggiunge un nuovo messaggio con una bolla di chat."""
        align = "left" if sender else "right"
        self.insert_message_bubble(new_text, sender)
    
    def insert_message_bubble(self, text, sender):
        """Inserisce una bolla di messaggio con dimensioni e padding ottimizzati."""
        # Calcola la larghezza massima considerando padding e scrollbar
        chat_width = int(self.width * 0.25)
        
        # Crea il contenitore principale per la bolla
        bubble_container = Frame(self.scrollable_frame, 
                            bg="lightgray",
                            width=chat_width - 20,
                            height=85)  # Altezza iniziale provvisoria
        bubble_container.pack_propagate(False)
        bubble_container.pack(fill="x", pady=2)
        
        # Crea la bolla con dimensioni dinamiche
        bubble = Label(
            bubble_container,
            text=text,
            bg="lightblue" if sender else "lightgreen",
            fg="black",
            font=("Arial", 12),
            padx=15,
            pady=8,
            wraplength=300,
            justify="left",
            borderwidth=0,
            highlightthickness=0
        )
        
        # Allineamento con ancoraggio e padding differenziato
        if sender:
            bubble.pack(side="left", padx=(10, chat_width//4), anchor="w")
        else:
            bubble.pack(side="right", padx=(chat_width//3, 10), anchor="e")
        
        # Aggiornamento dinamico del layout
        bubble.update_idletasks()
        bubble_height = bubble.winfo_reqheight() + 10  # Margine verticale
        bubble_container.config(height=bubble_height)
        
        # Scroll automatico
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)

    def on_canvas_click(self, event):
        """Gestisce il clic sulla finestra."""
        center_x, center_y = self.width // 2, self.height // 2
        tolerance = 200  

        if (center_x - tolerance <= event.x <= center_x + tolerance) and \
           (center_y - tolerance <= event.y <= center_y + tolerance):
            print("Clic al centro rilevato!")
            self.on_center_click()

    def on_center_click(self):
        """Funzione eseguita al clic al centro."""
        print("Azione attivata dal clic al centro!")
        self.click_event.set()  # Segnala al controller che il pulsante è stato premuto

    def update_center_image(self, new_image_path, use_homepage_size):
        """Aggiorna l'immagine centrale con una nuova immagine specificata."""
        if use_homepage_size:
            max_width = self.homepage_max_width
            max_height = self.homepage_max_height
        else:
            max_width = self.canvas_width
            max_height = self.height
        new_image = self.load_and_resize_image(new_image_path, max_width, max_height)
        if new_image:
            self.homepage_image = new_image  # Mantiene il riferimento per evitare il garbage collection
            self.canvas.itemconfig(self.homepage_image_id, image=new_image)
    
    def load_and_resize_image(self, image_path, max_width, max_height):
        """Carica e ridimensiona un'immagine mantenendo le proporzioni."""
        try:
            img = Image.open(image_path)

            # Calcola il rapporto dell'immagine e del canvas
            img_ratio = img.width / img.height
            canvas_ratio = max_width / max_height

            if img_ratio > canvas_ratio:
                # Se l'immagine è più larga del canvas, usa la larghezza massima
                new_width = max_width
                new_height = int(max_width / img_ratio)
            else:
                # Altrimenti usa l'altezza massima
                new_height = max_height
                new_width = int(max_height * img_ratio)

            # Ridimensiona l'immagine con un filtro di alta qualità
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)  # Converte l'immagine in un formato compatibile con Tkinter

        except Exception as e:
            print(f"Errore durante il caricamento dell'immagine: {e}")
            return None