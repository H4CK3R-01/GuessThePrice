# GuessThePrice
Telegram Bot, der täglich neue verrückte Produkte von Amazon postet, User müssen den Preis im Laufe des Tages erraten. Am Ende des Tages bekommt der User der am besten geraten hat Punkte, über den Lauf der Zeit kann man Punkte sammeln und in der Rangliste aufsteigen.

# Kriterien
Bewertungskriterien: 95% = 1,0 --- 50% = 4,0

(25%) - Dokumentation des vorhandenen Codes --- Modulbeschreibung, Funktionsbeschreibung, Klassenbeschreibung

(15%) - Testbeschreibung --- vollständig und sinnvoll (Testvarianz)

(20%) - Python Spezifika --- Verwendung von Python spezifische Programmierfunktionalitäten und Modulen

(20%) - Reaktion und Performance der Applikation

(20%) - UI Frontend und Usability Bedienbarkeit der APP Ausgabe

(05%) - Bonus für besondere Kreativität

Umsetzung:
- freies Thema angemeldet beim Dozenten und genehmigt (oder genehmigt mit Auflage)
- Datenspeicherung
- Datenvisualisierung
- klare Trennung der Aufgaben in Skripten (z.B. Klassen aufgabenspezifisch)
- bei Bots: Anleitung zur Implementierung und Tests
- Logfile mit sinvollen Ausgaben um Programmablauf nachvollziehen zu können
- externe Quellen eindeutig Kennzeichnen als solche an Code und Stelle

Oberthema:
"Data is the new oil"

# Deployment
## With docker
1. Das Dockerfile aus dem `source`-Ordner in das Root-Verzeichnis kopieren `cp source/Dockerfile .`
2. Das Docker Image erstellen `docker build . -t guesstheprice`
3. Die `source/.env.example`-Datei in das Root-Verzeichnis kopieren und zu `.env` umbenennen `cp source/.env.example .env`
4. Die `.env`-Datei so anpassen, das die Variablen die richtigen Werte haben
6. Den Container starten `docker run -d --name guesstheprice --env-file=.env guesstheprice`

## Without docker
### Windows
1. Virtuelles Environment erstellen `python -m venv venv`
2. venv starten: `.\venv\Scripts\activate`
3. Abhängigkeiten installieren `pip install -r requirements.txt`
4. Umgebungsvariablen setzen
   1. Erstelle die `.env`-Datei anhand der `.env.example`
   2. Alternativ die Variablen mit dem `set` Befehl setzen.
5. Bot Skripte starten `python source/bot.py & python source/daily_challenge.py`

### Linux / MacOS
1. Virtuelles Environment erstellen `python -m venv venv`
2. venv starten: `source venv/bin/activate`
3. Abhängigkeiten installieren `pip install -r requirements.txt`
4. Umgebungsvariablen setzen
   1. Erstelle das `.env`-file anhand der `.env.example`
   2. Alternativ die Variablen mit dem `export` Befehl setzen.
5. Bot Skripte starten `python source/bot.py & python source/daily_challenge.py`
