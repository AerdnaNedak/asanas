# Asanas

Yoga-Posen zum Stöbern und Lernen, offline auf iPhone und iPad. Englische und deutsche Namen, Sanskrit auf Wunsch, Filter nach Flow Phase, Pose Type und Target, Karteikarten mit Lernstand.

Die App enthält keine Inhalte. Sie liest die Posen nach einmaliger Anmeldung aus der eigenen Dropbox (`/03 Apps/Yoga/app-daten`) und speichert sie auf dem Gerät.

## Daten aktualisieren

1. Posen bearbeiten in `Dropbox/03 Apps/Yoga/posen/` (eine Markdown-Datei pro Pose, Zeichnungen in `posen/bilder/`).
2. `python3 tools/daten-bauen.py`
3. In der App: Einstellungen → „Jetzt aktualisieren“ (oder einfach neu öffnen).
