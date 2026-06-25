<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIMAP GL PRO - Ersatzteil-Suche</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        .image-section {
            flex: 1 1 500px;
            padding: 20px;
            border-right: 2px solid #eee;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #fafafa;
        }
        .image-section img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .search-section {
            flex: 1 1 400px;
            padding: 40px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="number"] {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 12px 20px;
            font-size: 16px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result-card {
            display: none;
            padding: 20px;
            background-color: #ecf0f1;
            border-left: 5px solid #3498db;
            border-radius: 4px;
            margin-top: 20px;
        }
        .result-card h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .result-item {
            margin: 8px 0;
            font-size: 15px;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            margin-top: 20px;
            display: none;
        }
    </style>
</head>
<body>

    <h1>FIMAP GL PRO Ersatzteilkatalog</h1>

    <div class="container">
        <div class="image-section">
            <img src="zeichung-seite8.jpg" alt="Explosionszeichnung GRUPPO BASAMENTO">
        </div>

        <div class="search-section">
            <h2>Ersatzteil suchen</h2>
            <p>Gib die Positionsnummer (POS) aus der Zeichnung ein, um die Details zu sehen.</p>
            
            <div class="search-box">
                <input type="number" id="posInput" placeholder="Z.B. 1, 2, 3..." min="1">
                <button onclick="sucheErsatzteil()">Suchen</button>
            </div>

            <div id="errorMessage" class="error">
                Teil nicht gefunden. Bitte überprüfe die Nummer.
            </div>

            <div id="resultCard" class="result-card">
                <h3>Teil Details</h3>
                <div class="result-item"><strong>POS:</strong> <span id="resPos"></span></div>
                <div class="result-item"><strong>Artikelnummer:</strong> <span id="resCodice"></span></div>
                <div class="result-item"><strong>Menge (QTÀ):</strong> <span id="resQta"></span></div>
                <div class="result-item"><strong>Beschreibung (IT):</strong> <span id="resDescIT"></span></div>
                <div class="result-item"><strong>Beschreibung (DE):</strong> <span id="resDescDE"></span></div>
            </div>
        </div>
    </div>

    <script>
        // Hier ist die Datenbank-Simulation (JSON). 
        // Diese Daten stammen aus "CR-01 GRUPPO BASAMENTO"
        const ersatzteile = {
            "1": { codice: "451400", qta: "2", descIT: "ANELLO PTFE ØEst=150 ØInt=120 S=2", descDE: "RING" },
            "2": { codice: "451405", qta: "1", descIT: "ATTACCO TERGI 14\" EVO-GL ZINC", descDE: "KUPPLUNG HINTERE" },
            "3": { codice: "409819", qta: "1", descIT: "BASETTA TC 142 PER FASCETTE", descDE: "STUTZPLATTE" },
            "4": { codice: "451545", qta: "2", descIT: "BOCCOLA D=12 d=8,5 L=22,5 OT", descDE: "BUCHSE" },
            "5": { codice: "451546", qta: "2", descIT: "BOCCOLA Q=18 D=12 M8 L=23 (20-3) OT", descDE: "BUCHSE" },
            "6": { codice: "451366", qta: "1", descIT: "CARTER BASAMENTO 14\" EVO-GL", descDE: "ABDECKUNG" },
            "7": { codice: "451403", qta: "1", descIT: "LEVA ATTACCO TERGI 14\" EVO-GL SILVER", descDE: "KUPPLUNG VORDERE" },
            "8": { codice: "451391", qta: "1", descIT: "RALLA SUPP. CARTER BASAM. EVO-GL (LAV)", descDE: "BASISSTÜTZRAD" },
            "9": { codice: "409151", qta: "4", descIT: "ROSETTA 5,5x15x1.5 UNI 6593 ZINC", descDE: "UNTERLAGSCHEIBE" },
            "10": { codice: "409177", qta: "4", descIT: "ROSETTA 8x17x1.6 UNI 6592 A2", descDE: "SCHEIBE" }
        };

        function sucheErsatzteil() {
            const inputVal = document.getElementById('posInput').value;
            const resultCard = document.getElementById('resultCard');
            const errorMessage = document.getElementById('errorMessage');

            // Setze Ansicht zurück
            resultCard.style.display = 'none';
            errorMessage.style.display = 'none';

            if(ersatzteile[inputVal]) {
                // Teil gefunden
                const teil = ersatzteile[inputVal];
                document.getElementById('resPos').textContent = inputVal;
                document.getElementById('resCodice').textContent = teil.codice;
                document.getElementById('resQta').textContent = teil.qta;
                document.getElementById('resDescIT').textContent = teil.descIT;
                document.getElementById('resDescDE').textContent = teil.descDE;
                
                resultCard.style.display = 'block';
            } else {
                // Teil nicht gefunden
                errorMessage.style.display = 'block';
            }
        }
    </script>
</body>
</html>
