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
        # Die Namen wurden an die Bezeichnungen im PDF (CR-Gruppen) angepasst
        self.baugruppen_bilder = {
            "Basamento (CR-01)": "Fimap_GL_Pro_01.jpg",
            "Motoriduttore (CR-01A)": "Fimap_GL_Pro_01A.jpg",
            "Tergipavimento (CR-03)": "Fimap_GL_Pro_03.jpg",
            "Telaio (CR-04/05)": "Fimap_GL_Pro_04.jpg",
            "Serbatoi (CR-06/07)": "Fimap_GL_Pro_06.jpg",
            "Serbatoi Antibatterico (CR-06/07)": "Fimap_GL_Pro_06_AB.jpg",
            "Aspirazione (CR-08)": "Fimap_GL_Pro_08.jpg",
            "Impianto Idrico (CR-09)": "Fimap_GL_Pro_09.jpg",
            "Impianto Elettrico (CR-10)": "Fimap_GL_Pro_10.jpg",
            "Manubrio (CR-11)": "Fimap_GL_Pro_11.jpg",
            "Caricabatterie (CR-13)": "Fimap_GL_Pro_13.jpg",
            "Flotta WiFi (CR-14)": "Fimap_GL_Pro_14_WiFi.jpg",
            "Flotta GSM EU (CR-14)": "Fimap_GL_Pro_14_EU.jpg",
            "Flotta GSM USA (CR-14)": "Fimap_GL_Pro_14_USA.jpg",
            "Flotta GSM JP-AUS (CR-14)": "Fimap_GL_Pro_14_JP.jpg",
            "Etichette (CR-16)": "Fimap_GL_Pro_16.jpg"
        }

        # Liste der Baugruppen-Namen für die Navigation und aktueller Index
        self.baugruppen_namen = list(self.baugruppen_bilder.keys())
        self.aktuelle_baugruppe_index = 0

        # --- SQL-DATENBANK INITIALISIEREN ---
        self.init_datenbank()

        # --- UI LAYOUT ---
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

        self.update_buttons()

    def init_datenbank(self):
        """Erstellt die SQL-Datenbank und füllt sie mit allen Daten aus dem PDF."""
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

        # Prüfen, ob die Datenbank frisch ist
        self.cursor.execute("SELECT COUNT(*) FROM teile")
        if self.cursor.fetchone()[0] == 0:
            print("Importiere PDF-Daten in die Datenbank...")
            # Komplette Liste der aus dem PDF extrahierten Teile
            start_daten = [
                # Basamento (CR-01)
                ("Basamento (CR-01)", "1", "451400", "2", "RING"),
                ("Basamento (CR-01)", "2", "451405", "1", "KUPPLUNG HINTERE"),
                ("Basamento (CR-01)", "3", "409819", "1", "STÜTZPLATTE"),
                ("Basamento (CR-01)", "4", "451545", "2", "BUCHSE"),
                ("Basamento (CR-01)", "5", "451546", "2", "BUCHSE"),
                ("Basamento (CR-01)", "6", "451366", "1", "ABDECKUNG"),
                ("Basamento (CR-01)", "7", "451403", "1", "KUPPLUNG VORDERE"),
                ("Basamento (CR-01)", "8", "451391", "1", "BASISSTÜTZRAD"),
                ("Basamento (CR-01)", "9", "409151", "4", "UNTERLAGSCHEIBE"),
                ("Basamento (CR-01)", "10", "409177", "4", "SCHEIBE"),
                ("Basamento (CR-01)", "11", "409154", "4", "UNTERLAGSCHEIBE"),
                ("Basamento (CR-01)", "12", "409187", "4", "UNTERLAGSCHEIBE"),
                ("Basamento (CR-01)", "13", "451402", "1", "HALTERUNG"),
                ("Basamento (CR-01)", "14", "451972", "1", "VELCRO DOUBLE"),
                ("Basamento (CR-01)", "15", "442958", "7", "SCHRAUBE"),
                ("Basamento (CR-01)", "16", "408848", "1", "SCHRAUBE"),
                ("Basamento (CR-01)", "17", "407645", "4", "SCHRAUBE"),
                ("Basamento (CR-01)", "18", "428350", "2", "SCHRAUBE"),
                ("Basamento (CR-01)", "19", "452154", "2", "SCHRAUBE"),

                # Motoriduttore (CR-01A)
                ("Motoriduttore (CR-01A)", "1", "451549", "1", "GEWINDEWELLE"),
                ("Motoriduttore (CR-01A)", "2", "439931", "2", "BUCHSE"),
                ("Motoriduttore (CR-01A)", "3", "415901", "2", "MUTTER"),
                ("Motoriduttore (CR-01A)", "4", "410277", "1", "BRIDE"),
                ("Motoriduttore (CR-01A)", "5", "451365", "1", "PINSELHALTERFLANSCH"),
                ("Motoriduttore (CR-01A)", "6", "451547", "1", "FEDER"),
                ("Motoriduttore (CR-01A)", "7", "408119", "1", "FEDER"),
                ("Motoriduttore (CR-01A)", "8", "229685", "1", "GETRIEBEMOTOR KOMPLETT"),
                ("Motoriduttore (CR-01A)", "9", "409161", "2", "SCHEIBE"),
                ("Motoriduttore (CR-01A)", "10", "451363", "1", "BÜRSTENMOTORHALTER"),
                ("Motoriduttore (CR-01A)", "11", "415780", "1", "SCHRAUBE"),
                ("Motoriduttore (CR-01A)", "12", "408966", "4", "SCHRAUBE"),
                ("Motoriduttore (CR-01A)", "13", "407667", "2", "SCHRAUBE"),
                ("Motoriduttore (CR-01A)", "14", "451751", "1", "BÜRSTE (PPL Ø0,35)"),
                ("Motoriduttore (CR-01A)", "15", "451752", "1", "BÜRSTE (PPL Ø0,6)"),
                ("Motoriduttore (CR-01A)", "16", "451753", "1", "BÜRSTE (PPL Ø0,9)"),
                ("Motoriduttore (CR-01A)", "17", "451754", "1", "BÜRSTE (SCHLEIFMITTEL)"),
                ("Motoriduttore (CR-01A)", "18", "451755", "1", "TREIBTELLERS"),

                # Tergipavimento (CR-03)
                ("Tergipavimento (CR-03)", "1", "451553", "8", "BUCHSE"),
                ("Tergipavimento (CR-03)", "2", "451558", "2", "BUCHSE"),
                ("Tergipavimento (CR-03)", "3", "451559", "2", "BUCHSE"),
                ("Tergipavimento (CR-03)", "4", "451557", "2", "GEWINDEBOLZEN"),
                ("Tergipavimento (CR-03)", "5", "451407", "1", "SAUGFUSS VORNE"),
                ("Tergipavimento (CR-03)", "6", "451409", "1", "SAUGFUSS VORNE"),
                ("Tergipavimento (CR-03)", "7", "408905", "2", "MADENSCHRAUBE"),
                ("Tergipavimento (CR-03)", "8", "442956", "2", "FEDER"),
                ("Tergipavimento (CR-03)", "9", "451556", "4", "BOLZEN"),
                ("Tergipavimento (CR-03)", "10", "410225", "2", "KUGELGRIF"),
                ("Tergipavimento (CR-03)", "11", "229809", "1", "LEISTE"),
                ("Tergipavimento (CR-03)", "12", "451561", "2", "POLYURETHANRAD"),
                ("Tergipavimento (CR-03)", "13", "451560", "4", "POLYURETHANRAD"),
                ("Tergipavimento (CR-03)", "14", "442958", "6", "SCHRAUBE"),
                ("Tergipavimento (CR-03)", "15", "428317", "2", "SCHRAUBE"),
                ("Tergipavimento (CR-03)", "16", "447887", "2", "HANDGRIFF"),
                ("Tergipavimento (CR-03)", "17", "229849", "1", "SAUGGUMMI SAUGFUSS KOMPLETT (PARA 33Sh)"),
                ("Tergipavimento (CR-03)", "18", "229850", "1", "SAUGGUMMI SAUGFUSS KOMPLETT (PARA 40Sh)"),
                ("Tergipavimento (CR-03)", "19", "229851", "1", "SAUGGUMMI SAUGFUSS KOMPLETT (PU 40Sh)"),
                
                # Telaio (CR-04/05)
                ("Telaio (CR-04/05)", "1", "451423", "2", "ARRETIERUNG"),
                ("Telaio (CR-04/05)", "2", "451581", "2", "BUCHSE"),
                ("Telaio (CR-04/05)", "3", "451899", "1", "KABEL"),
                ("Telaio (CR-04/05)", "4", "451593", "1", "SCHLIESSUNG"),
                ("Telaio (CR-04/05)", "5", "424822", "1", "RIEMEN"),
                ("Telaio (CR-04/05)", "6", "451399", "1", "DECKEL"),
                ("Telaio (CR-04/05)", "7", "409038", "1", "SICHERUNGSMUTTER"),
                ("Telaio (CR-04/05)", "8", "416781", "1", "SICHERUNGSMUTTER"),
                ("Telaio (CR-04/05)", "9", "409085", "4", "SICHERUNGSMUTTER"),
                ("Telaio (CR-04/05)", "10", "415906", "2", "STOPMUTTER"),
                ("Telaio (CR-04/05)", "11", "451582", "2", "DISTANZHÜLSE"),
                ("Telaio (CR-04/05)", "12", "452024", "1", "DISTANZHÜLSE"),
                ("Telaio (CR-04/05)", "13", "410277", "15", "BRIDE"),
                ("Telaio (CR-04/05)", "14", "451413", "1", "HAKEN"),
                ("Telaio (CR-04/05)", "15", "451923", "1", "GUMMIDCHTUNG"),
                ("Telaio (CR-04/05)", "16", "430184", "2", "MAGNET"),
                ("Telaio (CR-04/05)", "17", "451398", "1", "HANDGRIFF"),
                ("Telaio (CR-04/05)", "18", "439924", "1", "FEDER"),
                ("Telaio (CR-04/05)", "19", "230343", "1", "TAPE"),
                ("Telaio (CR-04/05)", "20", "451396", "1", "DECKEL"),
                ("Telaio (CR-04/05)", "21", "451591", "1", "KABELDURCHGANG"),
                ("Telaio (CR-04/05)", "22", "451411", "1", "PEDAL"),
                ("Telaio (CR-04/05)", "23", "441005", "2", "BOLZEN"),
                ("Telaio (CR-04/05)", "24", "451426", "2", "UNTERLAGSCHEIBE SPEZIAL"),
                ("Telaio (CR-04/05)", "25", "409151", "2", "UNTERLAGSCHEIBE"),
                ("Telaio (CR-04/05)", "26", "409177", "4", "SCHEIBE"),
                ("Telaio (CR-04/05)", "27", "451584", "1", "ROLLE"),
                ("Telaio (CR-04/05)", "28", "451573", "2", "RAD"),
                ("Telaio (CR-04/05)", "29", "408346", "1", "SEEGERRING"),
                ("Telaio (CR-04/05)", "30", "408355", "1", "SEEGERRING"),
                ("Telaio (CR-04/05)", "31", "451588", "2", "HALTERUNG"),
                ("Telaio (CR-04/05)", "32", "451708", "1", "RAHMEN"),
                ("Telaio (CR-04/05)", "33", "229861", "1", "ROHR"),
                ("Telaio (CR-04/05)", "34", "441077", "4", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "35", "438688", "2", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "36", "408833", "2", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "37", "423644", "5", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "38", "418309", "4", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "39", "418312", "2", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "40", "407645", "1", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "41", "407651", "1", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "42", "440337", "4", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "43", "451592", "2", "SCHRAUBE"),
                ("Telaio (CR-04/05)", "44", "451899", "1", "STROMKABEL"),
                ("Telaio (CR-04/05)", "45", "229862", "1", "BATTERIEGRUPPE (12V 33Ah)"),
                ("Telaio (CR-04/05)", "45.1", "451787", "2", "BATTERIE (12V 33Ah)"),
                ("Telaio (CR-04/05)", "45.2", "451900", "1", "BATTERIEKABEL"),
                ("Telaio (CR-04/05)", "45.3", "451901", "1", "BATTERIEBRÜCKENKABEL"),
                ("Telaio (CR-04/05)", "46", "229891", "1", "BATTERIEGRUPPE (12V 26Ah)"),
                ("Telaio (CR-04/05)", "46.1", "451790", "2", "BATTERIE (12V 26Ah Pb)"),
                ("Telaio (CR-04/05)", "46.2", "452535", "1", "BATTERIEKABEL"),
                ("Telaio (CR-04/05)", "46.3", "451976", "1", "BATTERIEBRÜCKENKABEL"),
                ("Telaio (CR-04/05)", "47", "229863", "1", "BATTERIEGRUPPE (12V 36Ah)"),
                ("Telaio (CR-04/05)", "47.1", "451788", "2", "BATTERIE (12V 36Ah Pb)"),
                ("Telaio (CR-04/05)", "47.2", "452535", "1", "BATTERIEKABEL"),
                ("Telaio (CR-04/05)", "47.3", "451976", "1", "BATTERIEBRÜCKENKABEL"),
                ("Telaio (CR-04/05)", "48", "230701", "1", "BATTERIEGRUPPE (24V 30Ah LITHIUM)"),
                ("Telaio (CR-04/05)", "48.1", "453782", "1", "BATTERIE (24V 30Ah)"),
                ("Telaio (CR-04/05)", "48.2", "452535", "1", "BATTERIEKABEL"),

                # Serbatoi (CR-06/07)
                ("Serbatoi (CR-06/07)", "1", "451379", "1", "DECKEL"),
                ("Serbatoi (CR-06/07)", "2", "451388", "1", "ABDECKUNG"),
                ("Serbatoi (CR-06/07)", "3", "451384", "1", "ABDECKUNG"),
                ("Serbatoi (CR-06/07)", "4", "451386", "1", "SCHARNIER"),
                ("Serbatoi (CR-06/07)", "5", "451377", "1", "DECKEL"),
                ("Serbatoi (CR-06/07)", "6", "451382", "1", "DECKEL"),
                ("Serbatoi (CR-06/07)", "7", "410277", "2", "ABRAZADERA"),
                ("Serbatoi (CR-06/07)", "8", "451429", "1", "FILTER"),
                ("Serbatoi (CR-06/07)", "9", "451594", "1", "FILTER"),
                ("Serbatoi (CR-06/07)", "10", "451595", "1", "FILTER"),
                ("Serbatoi (CR-06/07)", "11", "451703", "1", "FILTER"),
                ("Serbatoi (CR-06/07)", "12", "229773", "1", "DICHTUNG"),
                ("Serbatoi (CR-06/07)", "13", "428561", "2", "DICHTUNG"),
                ("Serbatoi (CR-06/07)", "14", "451605", "2", "DICHTUNG"),
                ("Serbatoi (CR-06/07)", "15", "421744", "1", "KUPPLUNG OHNE ZAPFEN"),
                ("Serbatoi (CR-06/07)", "16", "430184", "1", "MAGNET"),
                ("Serbatoi (CR-06/07)", "17", "451417", "1", "HANDGRIFF"),
                ("Serbatoi (CR-06/07)", "18", "451867", "1", "SCHALLDICHTUNG"),
                ("Serbatoi (CR-06/07)", "19", "451868", "1", "SCHALLDICHTUNG"),
                ("Serbatoi (CR-06/07)", "20", "451604", "2", "BOLZEN"),
                ("Serbatoi (CR-06/07)", "21", "451370", "1", "WINKELVERSCHRAUBUNG"),
                ("Serbatoi (CR-06/07)", "22", "451369", "1", "WINKELVERSCHRAUBUNG"),
                ("Serbatoi (CR-06/07)", "23", "428562", "2", "WINKELVERSCHRAUBUNG"),
                ("Serbatoi (CR-06/07)", "24", "452208", "2", "UNTERLAGSCHEIBE"),
                ("Serbatoi (CR-06/07)", "25", "451426", "1", "UNTERLAGSCHEIBE SPEZIAL"),
                ("Serbatoi (CR-06/07)", "26", "409141", "1", "UNTERLAGSCHEIBE"),
                ("Serbatoi (CR-06/07)", "27", "409151", "5", "UNTERLAGSCHEIBE"),
                ("Serbatoi (CR-06/07)", "28", "409154", "7", "UNTERLAGSCHEIBE"),
                ("Serbatoi (CR-06/07)", "29", "451869", "4", "UNTERLAGSCHEIBE"),
                ("Serbatoi (CR-06/07)", "30", "400250", "9", "UNTERLAGSCHEIBE SPEZIAL"),
                ("Serbatoi (CR-06/07)", "31", "451707", "1", "SCHMUTZWASSERTANK"),
                ("Serbatoi (CR-06/07)", "31.1", "451709", "1", "KAPPE MIT FEDER"),
                ("Serbatoi (CR-06/07)", "32", "451705", "1", "FRISCHWASSERTANK"),
                ("Serbatoi (CR-06/07)", "33", "451710", "1", "HALTERUNG"),
                ("Serbatoi (CR-06/07)", "34", "451375", "2", "HALTERUNG"),
                ("Serbatoi (CR-06/07)", "35", "451389", "1", "LADEKAPPE"),
                ("Serbatoi (CR-06/07)", "36", "451570", "1", "ROHR"),
                ("Serbatoi (CR-06/07)", "37", "451569", "1", "ROHR"),]