import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class ErsatzteilApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIMAP Ersatzteil-Katalog - GL PRO")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f4f4f9")

        # --- DATENBANK (Aus deinem 2. Bild ausgelesen) ---
        self.datenbank = {
            "1": {"codice": "451400", "qta": "2", "desc_it": "ANELLO PTFE ØEst=150 ØInt=120 S=2", "desc_de": "RING"},
            "2": {"codice": "451405", "qta": "1", "desc_it": "ATTACCO TERGI 14\" EVO-GL ZINC", "desc_de": "KUPPLUNG HINTERE"},
            "3": {"codice": "409819", "qta": "1", "desc_it": "BASETTA TC 142 PER FASCETTE", "desc_de": "STÜTZPLATTE"},
            "4": {"codice": "451545", "qta": "2", "desc_it": "BOCCOLA D=12 d=8,5 L=22,5 OT", "desc_de": "BUCHSE"},
            "5": {"codice": "451546", "qta": "2", "desc_it": "BOCCOLA Q=18 D=12 M8 L=23 (20-3) OT", "desc_de": "BUCHSE"},
            "6": {"codice": "451366", "qta": "1", "desc_it": "CARTER BASAMENTO 14\" EVO-GL", "desc_de": "ABDECKUNG"},
            "7": {"codice": "451403", "qta": "1", "desc_it": "LEVA ATTACCO TERGI 14\" EVO-GL SILVER", "desc_de": "KUPPLUNG VORDERE"},
            "8": {"codice": "451391", "qta": "1", "desc_it": "RALLA SUPP. CARTER BASAM. EVO-GL (LAV)", "desc_de": "BASISSTÜTZRAD"},
            "9": {"codice": "409151", "qta": "4", "desc_it": "ROSETTA 5,5x15x1.5 UNI 6593 ZINC", "desc_de": "UNTERLAGSCHEIBE"},
            "10": {"codice": "409177", "qta": "4", "desc_it": "ROSETTA 8x17x1.6 UNI 6592 A2", "desc_de": "SCHEIBE"},
            "11": {"codice": "409154", "qta": "4", "desc_it": "ROSETTA GROWER 5x1,6 ZINC", "desc_de": "UNTERLAGSCHEIBE"},
            "12": {"codice": "409187", "qta": "4", "desc_it": "ROSETTA GROWER 8x13x2,2 A2", "desc_de": "UNTERLAGSCHEIBE"},
            "13": {"codice": "451402", "qta": "1", "desc_it": "SUPPORTO RALLA BASAMENTO EVO-GL(LAV)", "desc_de": "HALTERUNG"},
            "14": {"codice": "451972", "qta": "1", "desc_it": "VELCRO DOUBLE 9/10MM COLORE NERO L=19CM", "desc_de": "VELCRO DOUBLE"},
            "15": {"codice": "442958", "qta": "7", "desc_it": "VITE M4x8/8 ISO 7380-2 A2", "desc_de": "SCHRAUBE"},
            "16": {"codice": "408848", "qta": "1", "desc_it": "VITE M5X10 TCTC UNI 7687 A2", "desc_de": "SCHRAUBE"},
            "17": {"codice": "407645", "qta": "4", "desc_it": "VITE M5X16 TE UNI 5739 ZINC", "desc_de": "SCHRAUBE"},
            "18": {"codice": "428350", "qta": "2", "desc_it": "VITE M8x25 TCBEI ISO 7380 A2", "desc_de": "SCHRAUBE"},
            "19": {"codice": "452154", "qta": "2", "desc_it": "VITE M8x45 TBEI ISO 7380 A2", "desc_de": "SCHRAUBE"}
        }

        # --- UI LAYOUT ---
        # Linker Frame für das Bild
        self.left_frame = tk.Frame(root, bg="white", bd=2, relief="groove")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Rechter Frame für die Sucheingabe
        self.right_frame = tk.Frame(root, bg="#f4f4f9", width=350)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # --- BILD ANZEIGEN ---
        self.bild_label = tk.Label(self.left_frame, bg="white")
        self.bild_label.pack(expand=True)
        self.lade_bild("zeichnung.png") # Hier muss dein erstes Bild liegen!

        # --- SUCHE BEREICH ---
        tk.Label(self.right_frame, text="Ersatzteil Suche", font=("Segoe UI", 18, "bold"), bg="#f4f4f9").pack(pady=(0, 20))
        
        tk.Label(self.right_frame, text="Positionsnummer (POS):", font=("Segoe UI", 12), bg="#f4f4f9").pack(anchor="w")
        
        # Eingabefeld
        self.eingabe_pos = tk.Entry(self.right_frame, font=("Segoe UI", 14), width=15)
        self.eingabe_pos.pack(pady=5, anchor="w")
        self.eingabe_pos.bind('<Return>', lambda event: self.suche_teil()) # Suche auch per Enter-Taste

        # Such-Button
        self.btn_suche = tk.Button(self.right_frame, text="Suchen", font=("Segoe UI", 12, "bold"), 
                                   bg="#3498db", fg="white", command=self.suche_teil)
        self.btn_suche.pack(pady=10, anchor="w")

        # --- ERGEBNIS BEREICH ---
        self.result_frame = tk.Frame(self.right_frame, bg="#ecf0f1", bd=2, relief="ridge")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        # Anfangs verstecken, bis gesucht wird
        self.result_frame.pack_forget() 

        # Labels für die Ergebnisse
        self.lbl_pos = tk.Label(self.result_frame, font=("Segoe UI", 11), bg="#ecf0f1", anchor="w")
        self.lbl_pos.pack(fill=tk.X, padx=10, pady=(10, 2))
        
        self.lbl_code = tk.Label(self.result_frame, font=("Segoe UI", 11, "bold"), bg="#ecf0f1", anchor="w")
        self.lbl_code.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_qta = tk.Label(self.result_frame, font=("Segoe UI", 11), bg="#ecf0f1", anchor="w")
        self.lbl_qta.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_desc_de = tk.Label(self.result_frame, font=("Segoe UI", 11), bg="#ecf0f1", anchor="w", wraplength=300, justify="left")
        self.lbl_desc_de.pack(fill=tk.X, padx=10, pady=2)
        
        self.lbl_desc_it = tk.Label(self.result_frame, font=("Segoe UI", 10, "italic"), fg="#555", bg="#ecf0f1", anchor="w", wraplength=300, justify="left")
        self.lbl_desc_it.pack(fill=tk.X, padx=10, pady=(2, 10))


    def lade_bild(self, dateiname):
        """Lädt das Bild in den linken Frame und passt die Größe an."""
        if os.path.exists(dateiname):
            try:
                img = Image.open(dateiname)
                img.thumbnail((600, 600)) # Skaliert das Bild passend zum Fenster
                self.photo = ImageTk.PhotoImage(img)
                self.bild_label.config(image=self.photo, text="")
            except Exception as e:
                self.bild_label.config(text=f"Fehler beim Laden des Bildes:\n{e}", fg="red")
        else:
            self.bild_label.config(text=f"Bitte speichere dein Bild als '{dateiname}'\nim selben Ordner wie dieses Skript.", 
                                   fg="red", font=("Segoe UI", 12))

    def suche_teil(self):
        """Durchsucht das Dictionary nach der eingegebenen Nummer."""
        pos = self.eingabe_pos.get().strip()
        
        if not pos:
            return

        if pos in self.datenbank:
            teil = self.datenbank[pos]
            
            # Text der Labels aktualisieren
            self.lbl_pos.config(text=f"POS: {pos}")
            self.lbl_code.config(text=f"Art.-Nr.: {teil['codice']}")
            self.lbl_qta.config(text=f"Menge: {teil['qta']} Stück")
            self.lbl_desc_de.config(text=f"DE: {teil['desc_de']}")
            self.lbl_desc_it.config(text=f"IT: {teil['desc_it']}")
            
            # Ergebnis-Frame einblenden
            self.result_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        else:
            # Ergebnis-Frame ausblenden und Fehlermeldung zeigen
            self.result_frame.pack_forget()
            messagebox.showwarning("Nicht gefunden", f"Die Position '{pos}' existiert in dieser Zeichnung nicht.")


if __name__ == "__main__":
    fenster = tk.Tk()
    app = ErsatzteilApp(fenster)
    fenster.mainloop()
