#!/usr/bin/env python3
"""Baut aus dem Notion-Export die Daten für die App.

Liest:   Dropbox/03 Apps/Yoga/notion-export/   (Notion: Markdown & CSV)
         Dropbox/03 Apps/Yoga/Vorschlag Flow Phase und Target.xlsx  (Spalten F und G)
Schreibt: Dropbox/03 Apps/Yoga/app-daten/asanas.json und app-daten/img/*.jpg

Aufruf:  python3 tools/daten-bauen.py
"""
import csv, glob, hashlib, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
from datetime import datetime
from urllib.parse import unquote

YOGA = os.path.expanduser("~/Library/CloudStorage/Dropbox/03 Apps/Yoga")
EXPORT = os.path.join(YOGA, "notion-export", "Asanas Overview")
XLSX = os.path.join(YOGA, "Vorschlag Flow Phase und Target.xlsx")
OUT = os.path.join(YOGA, "app-daten")
SKIP = {"Tadasana"}  # doppelt (= Mountain Pose) und leer

PHASES = ["Warm-up", "Build-up", "Peak", "Cool-down", "Relaxation"]

# Überschrift (klein, ohne Zeichen) -> (Schlüssel, Anzeigetitel)
SECTIONS = [
    ("description", "description", "Description"),
    ("sanskrit name", "sanskrit", "Sanskrit name"),
    ("step-by-step", "steps", "Step-by-step"),
    ("contraindication", "cautions", "Contraindications and cautions"),
    ("benefit", "benefits", "Benefits"),
    ("deepen", "deepen", "Deepen the pose"),
    ("beginner", "beginner", "Beginner’s tip"),
    ("teacher", "teacher", "Teacher tip"),
    ("preparatory", "preparatory", "Preparatory poses"),
    ("counter", "counter", "Counter poses"),
    ("variation", "variations", "Variations"),
    ("follow-up", "followup", "Follow-up poses"),
    ("cue card", "cue", "Cue card"),
]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def clean(s):
    s = s.replace("**", "").replace("__", "").strip()
    return re.sub(r"\s+", " ", s)


def split_list(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def section_key(title):
    t = re.sub(r"[^\w\s’'-]", " ", title.lower())
    t = re.sub(r"\s+", " ", t).strip()
    if t.startswith("step 1") or t.startswith("step 2"):
        return "start"          # ab hier kommt die ausführliche Fassung
    if t.startswith("step 3"):
        return "stop"           # Stichwort-Fassung: überspringen
    for needle, key, _ in SECTIONS:
        if (needle in t) if key == "cue" else t.startswith(needle):
            return key
    return None


def parse_md(path):
    sections, order, images = {}, [], []
    cur, skipping = None, False
    base = os.path.dirname(path)
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        m = re.match(r"^!\[[^\]]*\]\((.+)\)\s*$", line.strip())
        if m:
            if m.group(1).startswith("http"):
                continue  # fremde Fotos aus dem Web: nicht übernehmen
            p = unicodedata.normalize("NFC", os.path.join(base, unquote(m.group(1))))
            if not os.path.isfile(p):
                p = unicodedata.normalize("NFD", p)
            if os.path.isfile(p):
                if p not in images:
                    images.append(p)
            else:
                print("  Bild nicht gefunden:", m.group(1))
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        bold = re.match(r"^\*\*([^*]+?):?\*\*:?\s*$", line.strip())
        if not h and bold and section_key(clean(bold.group(1))) not in (None, "start", "stop", "sanskrit"):
            h = re.match(r"^(#)\s+(.*)$", "# " + bold.group(1))
        if h:
            key = section_key(clean(h.group(2)))
            if key == "start":
                skipping, cur = False, (None if "description" in sections else "description")
            elif key == "stop":
                skipping, cur = True, None
            elif key == "cue":
                skipping, cur = False, key
            elif key and not skipping:
                cur = None if key in sections else key  # nur die erste Fassung
            else:
                cur = None
            if cur and cur not in sections:
                sections[cur] = {"items": [], "text": []}
                order.append(cur)
            continue
        if not cur or skipping:
            continue
        s = line.strip()
        if not s or s == "---":
            continue
        b = re.match(r"^(?:[-*•]|\d+[.)])\s+(.*)$", s)
        if b:
            sections[cur]["items"].append(clean(b.group(1)))
        else:
            sections[cur]["text"].append(clean(s))
    return sections, order, images


def read_xlsx():
    try:
        from openpyxl import load_workbook
    except ImportError:
        sys.exit("openpyxl fehlt: pip3 install openpyxl")
    ws = load_workbook(XLSX)["Vorschlag"]
    out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[1]:
            out[r[1].strip()] = (split_list(r[5]), split_list(r[6]))
    return out


def make_jpg(src, dst_dir, name):
    tmp = os.path.join(tempfile.gettempdir(), "asanas-tmp.jpg")
    subprocess.run(["sips", "-Z", "1100", "-s", "format", "jpeg", "-s", "formatOptions", "78",
                    src, "--out", tmp], check=True, capture_output=True)
    h = hashlib.sha1(open(tmp, "rb").read()).hexdigest()[:8]
    fn = f"{name}-{h}.jpg"
    shutil.copyfile(tmp, os.path.join(dst_dir, fn))
    return fn


def main():
    csvs = glob.glob(os.path.join(EXPORT, "Overview *_all.csv"))
    if not csvs:
        sys.exit("Kein Notion-Export gefunden in " + EXPORT)
    rows = [{k.strip(): (v or "").strip() for k, v in r.items()}
            for r in csv.DictReader(open(csvs[0], encoding="utf-8-sig"))]
    proposal = read_xlsx()
    mds = {}
    for p in glob.glob(os.path.join(EXPORT, "Overview", "*.md")):
        name = os.path.basename(p).rsplit(" ", 1)[0].strip()
        mds[unicodedata.normalize("NFC", name)] = p

    img_dir = os.path.join(OUT, "img")
    os.makedirs(img_dir, exist_ok=True)
    used, poses, warn = set(), [], []
    for r in rows:
        en = r["Englischer Name"]
        if not en or en in SKIP:
            continue
        pid = slug(en)
        md = mds.get(unicodedata.normalize("NFC", en))
        sections, order, images = parse_md(md) if md else ({}, [], [])
        if not md:
            warn.append(f"keine Seite: {en}")
        targets, phases = proposal.get(en, (split_list(r.get("Target")), split_list(r.get("Flow phase"))))
        if en not in proposal:
            warn.append(f"nicht in der Vorschlagstabelle: {en}")
        imgs = []
        for i, src in enumerate(images, 1):
            fn = make_jpg(src, img_dir, f"{pid}-{i}")
            used.add(fn)
            imgs.append(fn)
        sa = r.get("Sanskrit", "")
        secs = []
        for key in order:
            title = next(t for _, k, t in SECTIONS if k == key)
            s = sections[key]
            if s["items"] or s["text"]:
                secs.append({"key": key, "title": title, "text": s["text"], "items": s["items"]})
        poses.append({
            "id": pid, "en": en, "de": r.get("Deutscher Name", ""), "sa": sa,
            "types": split_list(r.get("Pose Type")), "targets": targets,
            "phases": [p for p in PHASES if p.lower() in [x.lower().replace("warm up", "warm-up").replace("cool down", "cool-down") for x in phases]],
            "chair": r.get("Chair friendly", "").lower() == "yes",
            "full": bool(secs), "sections": secs, "images": imgs,
            "link": r.get("Pose Link", ""),
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
    print(f"{len(poses)} Posen, {sum(p['full'] for p in poses)} ausführlich, "
          f"{len(used)} Bilder ({size // 1024} KB) -> {OUT}")
    for w in warn:
        print("  Hinweis:", w)


if __name__ == "__main__":
    main()
