import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import os

class ErsatzteilApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIMAP Ersatzteil-Katalog - GL PRO")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f4f4f9")

        # --- ZUORDNUNG: BAUGRUPPE -> BILDDATEI ---
        self.baugruppen_bilder = {
            "Basamento (Seite 8)": "Fimap_GL_Pro_01.jpg",
            "Motoriduttore (Seite 10)": "zeichnung_motor.png"
        }

        # --- SQL-DATENBANK INITIALISIEREN ---
        self.init_datenbank()

        # --- UI LAYOUT ---
        # Oberer Bereich für Dropdown
        self.top_frame = tk.Frame(root, bg="#f4f4f9")
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)

        self.main_frame = tk.Frame(root, bg="#f4f4f9")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief="groove")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.right_frame = tk.Frame(self.main_frame, bg="#f4f4f9", width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, pady=10, expand=True)

        # --- BAUGRUPPEN AUSWAHL (Dropdown) ---
        tk.Label(self.top_frame, text="Baugruppe wählen:", font=("Segoe UI", 12, "bold"), bg="#f4f4f9").pack(side=tk.LEFT, padx=(0, 10))
        
        self.combo_baugruppe = ttk.Combobox(self.top_frame, values=list(self.baugruppen_bilder.keys()), font=("Segoe UI", 12), state="readonly", width=30)
        self.combo_baugruppe.pack(side=tk.LEFT)
        self.combo_baugruppe.current(0) # Wählt das erste Element standardmäßig aus
        self.combo_baugruppe.bind("<<ComboboxSelected>>", self.baugruppe_gewechselt)

        # --- BILD ANZEIGEN ---
        self.bild_label = tk.Label(self.left_frame, bg="white")
        self.bild_label.pack(expand=True)
        self.lade_bild(self.baugruppen_bilder[self.combo_baugruppe.get()])

        # --- SUCHE BEREICH ---
        tk.Label(self.right_frame, text="Positionsnummern (mit Komma trennen):", font=("Segoe UI", 11), bg="#f4f4f9").pack(anchor="w")
        
        self.eingabe_pos = tk.Entry(self.right_frame, font=("Segoe UI", 14), width=30)
        self.eingabe_pos.pack(pady=5, anchor="w")
        self.eingabe_pos.bind('<Return>', lambda event: self.suche_teil())

        self.btn_suche = tk.Button(self.right_frame, text="Suchen", font=("Segoe UI", 12, "bold"), 
                                   bg="#3498db", fg="white", command=self.suche_teil)
        self.btn_suche.pack(pady=10, anchor="w")

        # --- ERGEBNIS BEREICH (Tabelle) ---
        self.result_frame = tk.Frame(self.right_frame, bg="#f4f4f9")
        
        scroll_y = tk.Scrollbar(self.result_frame, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(self.result_frame, columns=("pos", "code", "qta", "de", "it"), 
                                 show="headings", yscrollcommand=scroll_y.set, height=15)
        scroll_y.config(command=self.tree.yview)
        
        self.tree.heading("pos", text="POS")
        self.tree.heading("code", text="Art.-Nr.")
        self.tree.heading("qta", text="Menge")
        self.tree.heading("de", text="Beschreibung (DE)")
        self.tree.heading("it", text="Beschreibung (IT)")
        
        self.tree.column("pos", width=40, anchor="center")
        self.tree.column("code", width=80, anchor="center")
        self.tree.column("qta", width=50, anchor="center")
        self.tree.column("de", width=150, anchor="w")
        self.tree.column("it", width=200, anchor="w")

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def init_datenbank(self):
        """Erstellt die SQL-Datenbank mit der neuen Spalte 'baugruppe'."""
        self.conn = sqlite3.connect("ersatzteile.db")
        self.cursor = self.conn.cursor()

        # Tabelle erstellen: Die Kombination aus 'baugruppe' und 'pos' muss einzigartig sein
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teile (
                baugruppe TEXT,
                pos TEXT,
                codice TEXT,
                qta TEXT,
                desc_de TEXT,
                desc_it TEXT,
                PRIMARY KEY (baugruppe, pos)
            )
        ''')

        # Prüfen, ob Tabelle leer ist. Wenn ja, Testdaten für ZWEI verschiedene Gruppen einfügen.
        self.cursor.execute("SELECT COUNT(*) FROM teile")
        if self.cursor.fetchone()[0] == 0:
            start_daten = [
                # Daten für Basamento
                ("Basamento (Seite 8)", "1", "451400", "2", "RING", "ANELLO PTFE"),
                ("Basamento (Seite 8)", "2", "451405", "1", "KUPPLUNG HINTERE", "ATTACCO TERGI 14\" EVO-GL"),
                ("Basamento (Seite 8)", "3", "409819", "1", "STÜTZPLATTE", "BASETTA TC 142 PER FASCETTE"),
                
                # Daten für Motor (Hier wiederholt sich z.B. die POS 1 und 2!)
                ("Motoriduttore (Seite 10)", "1", "451549", "1", "GEWINDEWELLE", "ALBERO CH=27"),
                ("Motoriduttore (Seite 10)", "2", "439931", "2", "BUCHSE", "BOCCOLA D=15-10"),
                ("Motoriduttore (Seite 10)", "3", "415901", "2", "MUTTER", "DADO M6 AUTOBL.")
            ]
            self.cursor.executemany("INSERT INTO teile (baugruppe, pos, codice, qta, desc_de, desc_it) VALUES (?, ?, ?, ?, ?, ?)", start_daten)
            self.conn.commit()

    def baugruppe_gewechselt(self, event):
        """Wird aufgerufen, wenn im Dropdown eine andere Baugruppe gewählt wird."""
        auswahl = self.combo_baugruppe.get()
        bild_datei = self.baugruppen_bilder[auswahl]
        self.lade_bild(bild_datei)
        
        # Tabelle und Eingabefeld leeren, da wir jetzt bei einer neuen Zeichnung sind
        self.eingabe_pos.delete(0, tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_frame.pack_forget()

    def lade_bild(self, dateiname):
        """Lädt das Bild in den linken Frame."""
        if os.path.exists(dateiname):
            try:
                img = Image.open(dateiname)
                img.thumbnail((650, 650))
                self.photo = ImageTk.PhotoImage(img)
                self.bild_label.config(image=self.photo, text="")
            except Exception as e:
                self.bild_label.config(text=f"Fehler beim Laden:\n{e}", fg="red")
        else:
            self.bild_label.config(text=f"Bild '{dateiname}' nicht gefunden.", fg="red", font=("Segoe UI", 12))

    def suche_teil(self):
        """Durchsucht die SQL-Datenbank nach POS und der aktuellen Baugruppe."""
        eingabe = self.eingabe_pos.get().strip()
        aktuelle_baugruppe = self.combo_baugruppe.get()
        
        if not eingabe:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        such_nummern = [num.strip() for num in eingabe.split(",")]
        treffer_gefunden = False
        nicht_gefunden = []

        for pos in such_nummern:
            if pos == "":
                continue
            
            # WICHTIG: Hier suchen wir jetzt nach 'pos' UND 'baugruppe'
            self.cursor.execute("SELECT codice, qta, desc_de, desc_it FROM teile WHERE pos = ? AND baugruppe = ?", (pos, aktuelle_baugruppe))
            ergebnis = self.cursor.fetchone()
            
            if ergebnis:
                self.tree.insert("", tk.END, values=(pos, ergebnis[0], ergebnis[1], ergebnis[2], ergebnis[3]))
                treffer_gefunden = True
            else:
                nicht_gefunden.append(pos)

        if treffer_gefunden:
            self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        else:
            self.result_frame.pack_forget()

        if nicht_gefunden:
            messagebox.showwarning("Hinweis", f"Folgende Positionen gibt es in '{aktuelle_baugruppe}' nicht:\n{', '.join(nicht_gefunden)}")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    fenster = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    app = ErsatzteilApp(fenster)
    fenster.mainloop()