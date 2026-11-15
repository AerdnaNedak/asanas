#!/usr/bin/env python3
"""Einmaliger Umzug (15.11.2026): aus den bisherigen App-Daten (gebaut aus dem Notion-Export)
wird eine Markdown-Datei pro Pose in Dropbox/03 Apps/Yoga/posen/. Ab dann sind diese Dateien das Original.
Bestehende Dateien werden nicht überschrieben."""
import json, os, shutil

YOGA = os.path.expanduser("~/Library/CloudStorage/Dropbox/03 Apps/Yoga")
SRC = os.path.join(YOGA, "app-daten")
DST = os.path.join(YOGA, "posen")
os.makedirs(os.path.join(DST, "bilder"), exist_ok=True)

data = json.load(open(os.path.join(SRC, "asanas.json"), encoding="utf-8"))
n = 0
for p in data["poses"]:
    path = os.path.join(DST, p["id"] + ".md")
    if os.path.exists(path):
        continue
    imgs = []
    for i, name in enumerate(p["images"], 1):
        dst_name = f"{p['id']}-{i}.jpg"
        shutil.copyfile(os.path.join(SRC, "img", name), os.path.join(DST, "bilder", dst_name))
        imgs.append(dst_name)
    head = [
        "---",
        "en: " + p["en"],
        "de: " + p["de"],
        "sa: " + p["sa"],
        "types: " + ", ".join(p["types"]),
        "targets: " + ", ".join(p["targets"]),
        "phases: " + ", ".join(p["phases"]),
        "chair: " + ("yes" if p["chair"] else "no"),
        "images: " + ", ".join(imgs),
        "text: " + ("Notion (Andrea)" if p["full"] else ""),
        "---",
        "",
    ]
    body = []
    for s in p["sections"]:
        body.append("## " + s["title"])
        body.append("")
        body += s["text"]
        if s["text"] and s["items"]:
            body.append("")
        numbered = s["key"] in ("steps", "cue")
        body += [(f"{i}. " if numbered else "- ") + x for i, x in enumerate(s["items"], 1)]
        body.append("")
    open(path, "w", encoding="utf-8").write("\n".join(head + body).rstrip() + "\n")
    n += 1
print(f"{n} Posen-Dateien angelegt in {DST}")
