# 🔧 Troubleshooting Guide

## Problem: "❌ Optimierung fehlgeschlagen: Could not find a valid route"

### Ursachen und Lösungen:

### 0. 🎯 **Für GitHub-Benutzer - WICHTIG!**

**Symptom:** Sie haben das Repo geklont und die App startet nicht richtig.

**Lösung:**
```bash
# 1. Prüfen Sie, dass Sie auf dem richtigen Branch sind:
git branch
# Sollte zeigen: * claude/santa-delivery-optimizer-011CUpXmP5Q3GTAn6YYeiGuW

# 2. Falls nicht, wechseln Sie:
git checkout claude/santa-delivery-optimizer-011CUpXmP5Q3GTAn6YYeiGuW

# 3. Stellen Sie sicher, dass die CSV-Datei vorhanden ist:
ls -lh santa_children_dataset_50k.csv

# 4. Falls die CSV fehlt, prüfen Sie beim Start der App:
python app.py
# Sie sollten sehen:
# ✅ Found dataset: santa_children_dataset_50k.csv (6.2 MB)
# ODER
# ⚠️  Dataset not found - Will use demo dataset (100 children)
```

**Die App funktioniert auch OHNE die große CSV-Datei!** Sie erstellt automatisch ein Demo-Dataset mit 100 Kindern.

### 1. App wird nicht aus dem richtigen Verzeichnis gestartet

**Lösung:**
```bash
# Navigieren Sie zum AdvML-Verzeichnis
cd AdvML   # oder /home/user/AdvML

# Starten Sie die App
python app.py
```

### 2. CSV-Datei ist nicht vorhanden

**Prüfen Sie:**
```bash
ls -lh santa_children_dataset_50k.csv
```

**Lösung:** Stellen Sie sicher, dass `santa_children_dataset_50k.csv` im selben Verzeichnis wie `app.py` liegt.

### 3. Browser-Cache-Problem

**Lösung:**
- Drücken Sie `Strg+Shift+R` (oder `Cmd+Shift+R` auf Mac) um die Seite hart neu zu laden
- Oder öffnen Sie den Browser im Inkognito-Modus

### 4. Port bereits belegt

**Symptom:** App startet nicht oder Sie sehen "Address already in use"

**Lösung:**
```bash
# Finden Sie den Prozess auf Port 5000
lsof -i :5000

# Töten Sie den Prozess
kill <PID>

# Oder ändern Sie den Port in app.py (letzte Zeile):
# app.run(debug=True, host='0.0.0.0', port=5001)
```

## Debug-Modus aktivieren

Wenn Sie die App mit den detaillierten Logs starten wollen:

```bash
python app.py
```

Sie sehen dann Meldungen wie:
```
🎅 Optimization request: weight=1000kg, volume=5000L, children=500
📂 Loading dataset...
✅ Loaded 50000 children
🔄 Starting route optimization...
✅ Route optimized successfully: 416 stops, 112337.41 km
```

## Häufige Fehler und was sie bedeuten:

### "Dataset file not found"
- Die CSV-Datei fehlt
- Lösung: Laden Sie santa_children_dataset_50k.csv herunter und legen Sie sie neben app.py

### "Could not find a valid route - no children could be delivered"
- Die Constraints sind zu strikt (z.B. max_weight=10 kg ist zu wenig)
- Lösung: Erhöhen Sie das maximale Gewicht/Volumen in den Einstellungen

### "Connection refused"
- Die Flask-App läuft nicht
- Lösung: Starten Sie `python app.py`

## Test der API direkt

Sie können die API auch direkt testen:

```bash
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"max_weight": 1000, "max_volume": 5000, "sample_size": 100}'
```

Wenn das funktioniert, aber der Browser nicht, liegt es am Frontend/Browser.

## Empfohlene Einstellungen

Für beste Ergebnisse verwenden Sie:

- **Max. Gewicht**: 1000-2000 kg
- **Max. Volumen**: 5000-10000 Liter
- **Anzahl Kinder**: 50-500 (für schnelle Ergebnisse)

## Support

Wenn nichts davon hilft:
1. Schauen Sie in die Terminal-Logs wo `python app.py` läuft
2. Öffnen Sie die Browser-Entwicklertools (F12) und schauen Sie in die Console
3. Erstellen Sie ein Issue auf GitHub mit den Fehlermeldungen
