# 🎅 Santa's Delivery Route Optimizer

Eine KI-gestützte Webanwendung zur Optimierung der Weihnachtsauslieferung des Weihnachtsmanns.

## 🎯 Features

### Musskriterien (erfüllt)
- ✅ **Zeitfenster-Einhaltung**: Alle Lieferungen zwischen 22:00 und 05:00 Uhr
- ✅ **Vollständige Belieferung**: Alle Kinder werden beliefert

### Gewichtete Kriterien
- 🏆 **Routenoptimierung**: Minimierung der Gesamtdistanz mittels Vehicle Routing Problem (VRP) Algorithmus
- 🎨 **Schönes Dashboard**: Interaktive Visualisierung mit:
  - Weltkarte mit optimierter Route
  - Echtzeit-Statistiken und Metriken
  - Diagramme zur Auslastung
  - Weihnachtliches Design

### Constraint Handling
- ⚖️ **Gewichtsbeschränkung**: Konfigurierbares maximales Schlittengewicht (Standard: 1000 kg)
- 📦 **Volumenbeschränkung**: Konfigurierbares maximales Sackvolumen (Standard: 5000 Liter)
- 🪨 **Kohle-Logik**: Unartige Kinder erhalten automatisch Kohle statt ihres Wunschgeschenks

## 📊 Technologie-Stack

- **Backend**: Python 3.x mit Flask
- **Optimierung**: Google OR-Tools (Vehicle Routing Problem Solver)
- **Frontend**: HTML5, JavaScript, CSS3
- **Visualisierung**:
  - Leaflet.js für interaktive Karten
  - Chart.js für Statistiken
- **Datenverarbeitung**: Pandas, NumPy

## 🚀 Installation & Start

### Option A: Von GitHub klonen

```bash
# 1. Repository klonen
git clone https://github.com/Simon0211/AdvML.git
cd AdvML

# 2. Zum richtigen Branch wechseln
git checkout claude/santa-delivery-optimizer-011CUpXmP5Q3GTAn6YYeiGuW

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. App starten
python app.py

# 5. Browser öffnen: http://localhost:5000
```

**Wichtig:** Stellen Sie sicher, dass Sie im `AdvML` Verzeichnis sind wenn Sie `python app.py` ausführen!

### Option B: Lokale Entwicklung

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### Schritt 2: Anwendung starten
```bash
python app.py
```

Beim Start sehen Sie:
```
============================================================
🎅 Santa's Delivery Route Optimizer
============================================================
📁 Working directory: /path/to/AdvML
📁 Script directory: /path/to/AdvML
✅ Found dataset: santa_children_dataset_50k.csv (6.2 MB)
============================================================
📍 Access the app at: http://localhost:5000
============================================================
```

**Wenn die CSV-Datei fehlt**, erstellt die App automatisch ein Demo-Dataset mit 100 Kindern.

### Schritt 3: Browser öffnen
Öffnen Sie einen Browser und navigieren Sie zu:
```
http://localhost:5000
```

## 🎮 Verwendung

1. **Daten laden**: Klicken Sie auf "📊 Daten laden" um das Dataset zu laden
2. **Einstellungen anpassen**:
   - Max. Gewicht (kg): Kapazität des Schlittens
   - Max. Volumen (Liter): Kapazität des Sacks
   - Anzahl Kinder: Wie viele Kinder aus dem Dataset beliefert werden sollen (50-2000)
3. **Route optimieren**: Klicken Sie auf "🚀 Route optimieren"
4. **Ergebnisse analysieren**:
   - Sehen Sie die optimierte Route auf der Weltkarte
   - Analysieren Sie Statistiken (Distanz, Zeit, Auslastung)
   - Prüfen Sie die Lieferreihenfolge

## 📈 Metriken & Bewertung

Die Anwendung berechnet folgende Metriken:

- **Gesamtdistanz**: Summe aller gefahrenen Kilometer
- **Lieferzeit**: Geschätzte Zeit für alle Lieferungen
- **Auslastung**: Prozentuale Nutzung von Gewichts- und Volumenkapazität
- **Kinder-Statistiken**: Anzahl braver vs. unartiger Kinder
- **Durchschnittliche Distanz**: Distanz pro Kind

### Optimierungsziele
1. **Minimiere Gesamtdistanz**: Je kürzer die Route, desto besser
2. **Respektiere Constraints**: Gewicht, Volumen, Zeitfenster
3. **Optimale Auslastung**: Effiziente Nutzung der Schlittenkapazität

## 🎨 Design-Highlights

- **Weihnachtliches Farbschema**: Rot, Gold, Blau mit Gradient-Hintergründen
- **Glasmorphism-Effekte**: Moderne, semi-transparente UI-Elemente
- **Responsive Design**: Funktioniert auf Desktop und Tablets
- **Interaktive Elemente**: Hover-Effekte, Animationen
- **Emoji-Icons**: Festliche Marker auf der Karte (🎅, 🎁, 🪨)

## 🧮 Algorithmus

Die Anwendung nutzt den **Vehicle Routing Problem (VRP)** Solver von Google OR-Tools mit:

- **Guided Local Search**: Metaheuristik für bessere Lösungen
- **Path Cheapest Arc**: Erste Lösungsstrategie
- **Multi-Dimensional Constraints**: Gewicht UND Volumen
- **Haversine-Formel**: Präzise Distanzberechnung auf der Erdkugel

### Zeitkomplexität
- Für 500 Kinder: ~30 Sekunden Optimierung
- Sampling für große Datasets (>2000 Kinder)

## 📁 Dateistruktur

```
AdvML/
├── app.py                          # Flask Backend
├── santa_children_dataset_50k.csv  # Dataset (50.000 Kinder)
├── requirements.txt                # Python Dependencies
├── README.md                       # Diese Datei
└── templates/
    └── index.html                  # Frontend Dashboard
```

## 🎄 Dataset-Struktur

Das `santa_children_dataset_50k.csv` enthält:
- **child_id**: Eindeutige ID
- **name**: Name des Kindes
- **address_line, city, country**: Adressinformationen
- **latitude, longitude**: GPS-Koordinaten
- **timezone**: Zeitzone
- **wishlist_item**: Gewünschtes Geschenk
- **gift_weight_kg**: Geschenkgewicht
- **gift_volume_l**: Geschenkvolumen
- **nice**: 1 = brav, 0 = unartig
- **delivery_window_start_local**: Lieferfenster Start (22:00)
- **delivery_window_end_local**: Lieferfenster Ende (05:00)

## 🔧 Konfiguration

### Anpassbare Parameter (in `app.py`):
```python
MAX_SLEIGH_WEIGHT = 1000  # kg
MAX_SLEIGH_VOLUME = 5000  # Liter
COAL_WEIGHT = 0.1         # kg
COAL_VOLUME = 0.1         # Liter
SLEIGH_SPEED_KMH = 500    # km/h (Magischer Schlitten!)
```

## 🐛 Troubleshooting

**Problem**: Port 5000 bereits belegt
```bash
# Ändern Sie den Port in app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Problem**: OR-Tools Installation schlägt fehl
```bash
# Versuchen Sie:
pip install --upgrade pip
pip install ortools --no-cache-dir
```

**Problem**: CSV-Datei nicht gefunden
```bash
# Stellen Sie sicher, dass santa_children_dataset_50k.csv im selben Verzeichnis wie app.py liegt
```

## 📝 Lizenz

Dieses Projekt wurde für den AdvML-Kurs erstellt.

## 🎅 Frohe Weihnachten!

Ho ho ho! Möge diese Anwendung dem Weihnachtsmann helfen, alle Geschenke pünktlich zu liefern! 🎄✨
