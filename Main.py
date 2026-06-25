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
            "Basamento (CR-01)": "Fimap_GL_Pro_01.jpg",
            "Motoriduttore (CR-01A)": "Fimap_GL_Pro_01A.jpg",
            "Tergipavimento (CR-03)": "Fimap_GL_Pro_03.jpg",
            "Name Baugruppe 4 (CR-04)": "Fimap_GL_Pro_04.jpg",
            "Name Baugruppe 5 (CR-05)": "Fimap_GL_Pro_05.jpg",
            "Name Baugruppe 6 (CR-06)": "Fimap_GL_Pro_06.jpg",
            "Name Baugruppe 7 (CR-07)": "Fimap_GL_Pro_07.jpg",
            "Name Baugruppe 8 (CR-08)": "Fimap_GL_Pro_08.jpg",
            "Name Baugruppe 9 (CR-09)": "Fimap_GL_Pro_09.jpg",
            "Name Baugruppe 10 (CR-10)": "Fimap_GL_Pro_10.jpg",
            "Name Baugruppe 11 (CR-11)": "Fimap_GL_Pro_11.jpg",
            "Name Baugruppe 12 (CR-12)": "Fimap_GL_Pro_12.jpg",
            "Name Baugruppe 13 (CR-13)": "Fimap_GL_Pro_13.jpg",
            "Name Baugruppe 14 (CR-14)": "Fimap_GL_Pro_14.jpg",
            "Name Baugruppe 15 (CR-15)": "Fimap_GL_Pro_15.jpg",
            "Name Baugruppe 16 (CR-16)": "Fimap_GL_Pro_16.jpg",
            "Name Baugruppe 17 (CR-17)": "Fimap_GL_Pro_17.jpg",
            "Name Baugruppe 18 (CR-18)": "Fimap_GL_Pro_18.jpg"
        }

        # Liste der Baugruppen-Namen für die Navigation und aktueller Index
        self.baugruppen_namen = list(self.baugruppen_bilder.keys())
        self.aktuelle_baugruppe_index = 0

        # --- SQL-DATENBANK INITIALISIEREN ---
        self.init_datenbank()

        # --- UI LAYOUT ---
        # Oberer Bereich für Navigation (Vor/Zurück)
        self.top_frame = tk.Frame(root, bg="#f4f4f9")
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)

        self.main_frame = tk.Frame(root, bg="#f4f4f9")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg="white", bd=2, relief="groove")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.right_frame = tk.Frame(self.main_frame, bg="#f4f4f9", width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=20, pady=10, expand=True)

        # --- NAVIGATION ---
        self.btn_zurueck = tk.Button(self.top_frame, text="<< Zurück", font=("Segoe UI", 12, "bold"), 
                                     bg="#bdc3c7", fg="#2c3e50", width=12, command=self.vorherige_baugruppe)
        self.btn_zurueck.pack(side=tk.LEFT)

        self.lbl_baugruppe_name = tk.Label(self.top_frame, text=self.baugruppen_namen[self.aktuelle_baugruppe_index], 
                                           font=("Segoe UI", 16, "bold"), bg="#f4f4f9", fg="#2980b9")
        self.lbl_baugruppe_name.pack(side=tk.LEFT, expand=True)

        self.btn_vor = tk.Button(self.top_frame, text="Vor >>", font=("Segoe UI", 12, "bold"), 
                                 bg="#bdc3c7", fg="#2c3e50", width=12, command=self.naechste_baugruppe)
        self.btn_vor.pack(side=tk.RIGHT)

        # --- BILD ANZEIGEN ---
        self.bild_label = tk.Label(self.left_frame, bg="white")
        self.bild_label.pack(expand=True)
        self.lade_bild(self.baugruppen_bilder[self.baugruppen_namen[self.aktuelle_baugruppe_index]])

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
        self.tree = ttk.Treeview(self.result_frame, columns=("pos", "code", "qta", "de"), 
                                 show="headings", yscrollcommand=scroll_y.set, height=15)
        scroll_y.config(command=self.tree.yview)
        
        self.tree.heading("pos", text="POS")
        self.tree.heading("code", text="Art.-Nr.")
        self.tree.heading("qta", text="Menge")
        self.tree.heading("de", text="Beschreibung (DE)")
        
        self.tree.column("pos", width=40, anchor="center")
        self.tree.column("code", width=80, anchor="center")
        self.tree.column("qta", width=50, anchor="center")
        self.tree.column("de", width=250, anchor="w")

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # UI initial auf den ersten Status setzen
        self.update_buttons()

    def init_datenbank(self):
        """Erstellt die SQL-Datenbank (desc_it wurde entfernt)."""
        self.conn = sqlite3.connect("ersatzteile.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teile (
                baugruppe TEXT,
                pos TEXT,
                codice TEXT,
                qta TEXT,
                desc_de TEXT,
                PRIMARY KEY (baugruppe, pos)
            )
        ''')

        # Start-Testdaten einfügen, falls die DB leer ist (optional)
        self.cursor.execute("SELECT COUNT(*) FROM teile")
        if self.cursor.fetchone()[0] == 0:
            start_daten = [
                ("Basamento (CR-01)", "1", "451400", "2", "RING"),
                ("Basamento (CR-01)", "2", "451405", "1", "KUPPLUNG HINTERE"),
                ("Basamento (CR-01)", "3", "409819", "1", "STÜTZPLATTE"),
                ("Motoriduttore (CR-01A)", "1", "451549", "1", "GEWINDEWELLE"),
                ("Motoriduttore (CR-01A)", "2", "439931", "2", "BUCHSE"),
                ("Motoriduttore (CR-01A)", "3", "415901", "2", "MUTTER")
            ]
            self.cursor.executemany("INSERT INTO teile (baugruppe, pos, codice, qta, desc_de) VALUES (?, ?, ?, ?, ?)", start_daten)
            self.conn.commit()

    def vorherige_baugruppe(self):
        """Wechselt zur vorherigen Baugruppe in der Liste."""
        if self.aktuelle_baugruppe_index > 0:
            self.aktuelle_baugruppe_index -= 1
            self.aktualisiere_ansicht()

    def naechste_baugruppe(self):
        """Wechselt zur nächsten Baugruppe in der Liste."""
        if self.aktuelle_baugruppe_index < len(self.baugruppen_namen) - 1:
            self.aktuelle_baugruppe_index += 1
            self.aktualisiere_ansicht()

    def update_buttons(self):
        """Deaktiviert die Buttons am Anfang oder Ende der Liste."""
        if self.aktuelle_baugruppe_index == 0:
            self.btn_zurueck.config(state=tk.DISABLED, bg="#ecf0f1")
        else:
            self.btn_zurueck.config(state=tk.NORMAL, bg="#bdc3c7")

        if self.aktuelle_baugruppe_index == len(self.baugruppen_namen) - 1:
            self.btn_vor.config(state=tk.DISABLED, bg="#ecf0f1")
        else:
            self.btn_vor.config(state=tk.NORMAL, bg="#bdc3c7")

    def aktualisiere_ansicht(self):
        """Aktualisiert Titel, Bild und leert die Suchergebnisse nach einem Wechsel."""
        aktuelle_baugruppe = self.baugruppen_namen[self.aktuelle_baugruppe_index]
        bild_datei = self.baugruppen_bilder[aktuelle_baugruppe]
        
        # UI aktualisieren
        self.lbl_baugruppe_name.config(text=aktuelle_baugruppe)
        self.lade_bild(bild_datei)
        self.update_buttons()
        
        # Suchfeld und Tabelle leeren
        self.eingabe_pos.delete(0, tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_frame.pack_forget()

    def lade_bild(self, dateiname):
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
        eingabe = self.eingabe_pos.get().strip()
        aktuelle_baugruppe = self.baugruppen_namen[self.aktuelle_baugruppe_index]
        
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
            
            # Holt codice, qta und desc_de für die aktuell angezeigte Baugruppe
            self.cursor.execute("SELECT codice, qta, desc_de FROM teile WHERE pos = ? AND baugruppe = ?", (pos, aktuelle_baugruppe))
            ergebnis = self.cursor.fetchone()
            
            if ergebnis:
                self.tree.insert("", tk.END, values=(pos, ergebnis[0], ergebnis[1], ergebnis[2]))
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