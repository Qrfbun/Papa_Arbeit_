import tkinter as tk
from PIL import Image, ImageTk

class ErsatzteilKatalog:
    def __init__(self, root):
        self.root = root
        self.root.title("FIMAP Ersatzteil-Katalog")
        self.root.geometry("800x600")
        self.root.configure(bg="#f4f4f9")

        # --- DATENBANK ---
        # Hier trägst du deine Bilder und die dazugehörigen Titel ein
        self.seiten = [
            {"bild": "Fimap_GL_Pro_01.jpg", "titel": "GL PRO - Gruppo Basamento (Seite 8)"},
            {"bild": "Fimap_GL_Pro_01A.jpg", "titel": "GL PRO - Motor (Seite 10)"},
            {"bild": "Fimap_GL_Pro_03.jpg", "titel": "GL PRO - Squeegee (Seite 12)"}
        ]
        self.aktuelle_seite = 0

        # --- UI-ELEMENTE ERSTELLEN ---
        # Titel oben
        self.titel_label = tk.Label(root, text="", font=("Segoe UI", 18, "bold"), bg="#f4f4f9", fg="#2c3e50")
        self.titel_label.pack(pady=15)

        # Bereich für das Bild
        self.bild_label = tk.Label(root, bg="#ffffff", relief="solid", bd=1)
        self.bild_label.pack(expand=True, padx=20, pady=10)

        # Bereich für die Buttons unten
        btn_frame = tk.Frame(root, bg="#f4f4f9")
        btn_frame.pack(fill=tk.X, pady=20)

        # Zurück-Button
        self.btn_zurueck = tk.Button(btn_frame, text="<< Vorheriges Bild", font=("Segoe UI", 12), 
                                     bg="#3498db", fg="white", command=self.vorheriges_bild)
        self.btn_zurueck.pack(side=tk.LEFT, padx=50)

        # Weiter-Button
        self.btn_weiter = tk.Button(btn_frame, text="Nächstes Bild >>", font=("Segoe UI", 12), 
                                    bg="#3498db", fg="white", command=self.naechstes_bild)
        self.btn_weiter.pack(side=tk.RIGHT, padx=50)

        # Erstes Bild beim Start laden
        self.zeige_seite(self.aktuelle_seite)

    def zeige_seite(self, index):
        """Lädt das Bild und den Text für die aktuelle Seite."""
        daten = self.seiten[index]
        self.titel_label.config(text=daten["titel"])

        try:
            # Bild laden und an das Fenster anpassen
            img = Image.open(daten["bild"])
            img.thumbnail((700, 450))  # Maximalgröße, Proportionen bleiben erhalten
            self.photo = ImageTk.PhotoImage(img)
            self.bild_label.config(image=self.photo, text="")
        except FileNotFoundError:
            # Fehler abfangen, falls das Bild nicht im Ordner liegt
            self.bild_label.config(image="", text=f"Fehler: Bild '{daten['bild']}' nicht gefunden!", 
                                   font=("Arial", 14), fg="red", width=50, height=20)

        # Buttons deaktivieren, wenn wir am Anfang oder Ende der Liste sind
        self.btn_zurueck.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.btn_weiter.config(state=tk.NORMAL if index < len(self.seiten) - 1 else tk.DISABLED)

    def vorheriges_bild(self):
        """Wechselt zum vorherigen Bild."""
        if self.aktuelle_seite > 0:
            self.aktuelle_seite -= 1
            self.zeige_seite(self.aktuelle_seite)

    def naechstes_bild(self):
        """Wechselt zum nächsten Bild."""
        if self.aktuelle_seite < len(self.seiten) - 1:
            self.aktuelle_seite += 1
            self.zeige_seite(self.aktuelle_seite)

# --- PROGRAMM STARTEN ---
if __name__ == "__main__":
    fenster = tk.Tk()
    app = ErsatzteilKatalog(fenster)
    fenster.mainloop()
