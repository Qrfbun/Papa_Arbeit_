import sqlite3

# =====================================================================
# HIER KOPIERST DU IN ZUKUNFT EINFACH DEN BLOCK REIN, DEN ICH DIR GEBE
# =====================================================================



# =====================================================================

def daten_importieren():
    """Importiert die Liste NEUE_DATEN in die SQLite-Datenbank."""
    try:
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect("ersatzteile.db")
        cursor = conn.cursor()
        
        # INSERT OR REPLACE: Wenn die Baugruppe + POS schon existiert, 
        # wird sie automatisch mit den neuen Daten überschrieben (Update).
        cursor.executemany('''
            INSERT OR REPLACE INTO teile (baugruppe, pos, codice, qta, desc_de) 
            VALUES (?, ?, ?, ?, ?)
        ''', NEUE_DATEN)
        
        conn.commit()
        print(f"✅ Erfolgreich {len(NEUE_DATEN)} Teile in die Datenbank importiert!")
        print("Du kannst die App jetzt starten und die neuen Teile suchen.")
        
    except sqlite3.Error as e:
        print(f"❌ Fehler bei der Datenbank-Verbindung: {e}")
    except Exception as e:
        print(f"❌ Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        # Verbindung sicher schließen
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    print("Starte Import...")
    daten_importieren()