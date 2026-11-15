# Asanas

Web-App (PWA) zum Lesen und Lernen von Yoga-Posen für Andreas Yogalehrer-Ausbildung (2027, vermutlich in Asien, auf Englisch). Läuft offline auf iPhone und iPad. Nur lesen und lernen, kein Bearbeiten in der App.

## Zusammenarbeit

- Deutsch, per du, ohne Fachjargon.
- Erst Anforderungen und Optionen besprechen, dann bauen. Bei größeren Änderungen auf ihr „Jetzt umsetzen“ warten. Kleine Wünsche direkt umsetzen.
- Andrea ordnet Posen fachlich noch nicht selbst ein. Flow Phase und Target sind Claudes Vorschläge (in der App so gekennzeichnet). Was in der Ausbildung anders gelehrt wird, wird korrigiert.

## Aufbau

- Online über GitHub Pages: https://aerdnanedak.github.io/asanas/ (Repo `AerdnaNedak/asanas`, öffentlich). Ein `git push` auf `main` veröffentlicht.
- `index.html`: die ganze App (CSS und JS inline). `sw.js`: Offline-Cache für die App. `manifest.webmanifest` und Icons.
- **Bei jeder App-Änderung** `CACHE` in `sw.js` und `VERSION` in `index.html` hochzählen.
- Die Inhalte liegen **nicht** im Repo, sondern privat in der Dropbox. Ein Teil der Texte stammt ursprünglich von Yoga Journal und darf nie in dieses (öffentliche) Repo.
  - **Original (seit 15.11.2026):** `Dropbox/03 Apps/Yoga/posen/<id>.md`, eine Datei pro Pose. Kopf zwischen `---` mit `en, de, sa, types, targets, phases, chair, images, text`; danach Abschnitte mit `##` in fester Reihenfolge: Description, Sanskrit name, Step-by-step, Contraindications and cautions, Benefits, Deepen the pose, Beginner’s tip, Teacher tip, Preparatory poses, Counter poses, Variations, Follow-up poses, Cue card. Zeichnungen in `posen/bilder/`.
  - `text:` sagt, woher der Text stammt: „Notion (Andrea)“ oder „Claude (Entwurf …, noch nicht geprüft)“. Die App weist Claude-Entwürfe aus.
  - Neue Texte schreibt Claude in Andreas Stil (kurze Stichpunkte, Cue Card höchstens 10 Zeilen), **in eigenen Worten**, nie von Yoga Journal übernommen.
  - Notion und `notion-export/` sind nur noch Archiv. `tools/umziehen.py` war der einmalige Umzug.
  - App-Daten: `Dropbox/03 Apps/Yoga/app-daten/asanas.json` und `app-daten/img/*.jpg`
- `tools/daten-bauen.py` baut aus `posen/` die App-Daten (Bilder verkleinern, Namen mit Prüfsumme). Danach lädt die App die neuen Daten beim nächsten Öffnen.
- Die App liest über die Dropbox-API (dieselbe Dropbox-App und derselbe Schlüssel wie das Moderationsdeck, Code wird manuell eingefügt). Daten und Bilder liegen im Cache `asanas-daten`, die Bilder als Blob-URLs.
- Lernen: Karten „English → Deutsch“, „Deutsch → English“, „Bild → Name“, optional „Sanskrit → Name“. Stufen 1–5 wie bei Karteikästen, Lernstand in `localStorage` (`as.learn`), nur auf dem jeweiligen Gerät.

## Prüfen

- Lokal: `dev-daten/` ist eine Kopie von `app-daten` (gitignored). Vorher aktualisieren mit `rsync -a ~/Library/CloudStorage/Dropbox/"03 Apps/Yoga/app-daten/" dev-daten/`. Auf localhost lädt die App die Daten von dort statt aus der Dropbox. Ein Symlink geht nicht, der lokale Server darf nicht in die Dropbox.
- Server: `python3 -m http.server 8765`, dann iPhone-Größe (375×812) und iPad-Größe prüfen, hell und dunkel.
- Die echte Dropbox-Verbindung kann nur Andrea testen.

## Design

„Ozean & Koralle“: hell #EEF3F4, Text #1E3440, Akzent Koralle #E06C5A, dunkel #132630. Phasenfarben: Warm-up #F2B45C, Build-up #E06C5A, Peak #B23A48, Cool-down #3F8F8A, Relaxation #5A6FA8. Posennamen in Fraunces (Serif), sonst Systemschrift. Bewusst anders als das Moderationsdeck (Tannengrün, Space Grotesk).

## Offen

- 48 Posen haben nur Grunddaten. Texte in Runden ergänzen: Build-up erledigt (Runde 1, 15.11.2026), danach Warm-up, Cool-down, Relaxation, Peak.
- Alle 92 Posen haben seit 15.11.2026 eine Zeichnung. Neue oder misslungene Zeichnungen: `python3 tools/zeichnen.py <id>` (Skill codex-bild, nacheinander, nie parallel; Beschreibung pro Pose in `POSES`). Ein paar Zusatzbilder sind noch Fotos (Extended Puppy, Extended Side Angle, Extended Triangle, Extended Hand-to-Big-Toe, Eight-Angle Nr. 2).
- Dropbox-Anmeldung auf iPhone/iPad durch Andrea testen.
