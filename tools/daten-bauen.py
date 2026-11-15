#!/usr/bin/env python3
"""Baut aus den Posen-Dateien die Daten für die App.

Original:  Dropbox/03 Apps/Yoga/posen/<id>.md   (eine Datei pro Pose, Kopf mit Feldern, Abschnitte mit ##)
           Dropbox/03 Apps/Yoga/posen/bilder/    (Zeichnungen, im Kopf unter „images“ genannt)
Ergebnis:  Dropbox/03 Apps/Yoga/app-daten/asanas.json und app-daten/img/*.jpg

Aufruf:  python3 tools/daten-bauen.py
"""
import glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from datetime import datetime

YOGA = os.path.expanduser("~/Library/CloudStorage/Dropbox/03 Apps/Yoga")
POSEN = os.path.join(YOGA, "posen")
OUT = os.path.join(YOGA, "app-daten")

PHASES = ["Warm-up", "Build-up", "Peak", "Cool-down", "Relaxation"]
SECTIONS = [  # Überschrift in der Datei -> Schlüssel
    ("Description", "description"), ("Sanskrit name", "sanskrit"), ("Step-by-step", "steps"),
    ("Contraindications and cautions", "cautions"), ("Benefits", "benefits"),
    ("Deepen the pose", "deepen"), ("Beginner’s tip", "beginner"), ("Teacher tip", "teacher"),
    ("Preparatory poses", "preparatory"), ("Counter poses", "counter"), ("Variations", "variations"),
    ("Follow-up poses", "followup"), ("Chair version", "chair"), ("Cue card", "cue"),
]
KEY = {t.lower().replace("'", "’"): k for t, k in SECTIONS}
TITLE = {k: t for t, k in SECTIONS}


def split_list(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def parse(path, warn):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    if not m:
        warn.append(f"{os.path.basename(path)}: Kopf fehlt")
        return None
    head = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            head[k.strip()] = v.strip()
    sections, cur = {}, None
    for line in m.group(2).splitlines():
        h = re.match(r"^##\s+(.*)$", line)
        if h:
            t = h.group(1).strip().lower().replace("'", "’")
            cur = KEY.get(t)
            if not cur:
                warn.append(f"{os.path.basename(path)}: unbekannte Überschrift „{h.group(1)}“")
            elif cur not in sections:
                sections[cur] = {"text": [], "items": []}
            continue
        s = line.strip()
        if not cur or not s:
            continue
        b = re.match(r"^(?:[-*•]|\d+[.)])\s+(.*)$", s)
        sections[cur]["items" if b else "text"].append(b.group(1) if b else s)
    return head, sections


def make_jpg(src, dst_dir, name):
    tmp = os.path.join(tempfile.gettempdir(), "asanas-tmp.jpg")
    subprocess.run(["sips", "-Z", "1100", "-s", "format", "jpeg", "-s", "formatOptions", "80",
                    src, "--out", tmp], check=True, capture_output=True)
    h = hashlib.sha1(open(tmp, "rb").read()).hexdigest()[:8]
    fn = f"{name}-{h}.jpg"
    shutil.copyfile(tmp, os.path.join(dst_dir, fn))
    return fn


def main():
    files = sorted(glob.glob(os.path.join(POSEN, "*.md")))
    if not files:
        sys.exit("Keine Posen-Dateien gefunden in " + POSEN)
    img_dir = os.path.join(OUT, "img")
    os.makedirs(img_dir, exist_ok=True)
    poses, used, warn = [], set(), []
    for path in files:
        r = parse(path, warn)
        if not r:
            continue
        head, sections = r
        pid = os.path.basename(path)[:-3]
        imgs = []
        for i, name in enumerate(split_list(head.get("images")), 1):
            src = os.path.join(POSEN, "bilder", name)
            if not os.path.isfile(src):
                warn.append(f"{pid}: Bild fehlt: {name}")
                continue
            fn = make_jpg(src, img_dir, f"{pid}-chair" if "-chair" in name else f"{pid}-{i}")
            used.add(fn)
            imgs.append(fn)
        phases = split_list(head.get("phases"))
        for x in phases:
            if x not in PHASES:
                warn.append(f"{pid}: unbekannte Phase „{x}“")
        secs = [{"key": k, "title": TITLE[k], **sections[k]} for _, k in SECTIONS
                if k in sections and (sections[k]["text"] or sections[k]["items"])]
        poses.append({
            "id": pid, "en": head.get("en", pid), "de": head.get("de", ""), "sa": head.get("sa", ""),
            "types": split_list(head.get("types")), "targets": split_list(head.get("targets")),
            "phases": [p for p in PHASES if p in phases],
            "chair": head.get("chair", "").lower() == "yes",
            "full": bool(secs), "sections": secs, "images": imgs,
            "text": head.get("text", ""),
        })
    for f in os.listdir(img_dir):
        if f not in used:
            os.remove(os.path.join(img_dir, f))
    poses.sort(key=lambda p: p["en"].lower())
    data = {
        "version": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "phases": PHASES,
        "types": sorted({t for p in poses for t in p["types"]}),
        "targets": sorted({t for p in poses for t in p["targets"]}),
        "proposal": True,
        "poses": poses,
    }
    with open(os.path.join(OUT, "asanas.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(os.path.join(img_dir, x)) for x in used)
    print(f"{len(poses)} Posen, {sum(p['full'] for p in poses)} mit Text, "
          f"{len(used)} Bilder ({size // 1024} KB) -> {OUT}")
    for w in warn:
        print("  Hinweis:", w)


if __name__ == "__main__":
    main()
