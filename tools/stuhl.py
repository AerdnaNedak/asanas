#!/usr/bin/env python3
"""Stuhl-Yoga: schreibt den Abschnitt „## Chair version“ in die Posen-Dateien, setzt „chair: yes“
und lässt fehlende Stuhl-Zeichnungen über codex-bild erzeugen (Datei <id>-chair.png, wird an „images“ angehängt).

Aufruf:  python3 tools/stuhl.py texte
         python3 tools/stuhl.py bilder [id ...]
Danach:  python3 tools/daten-bauen.py
"""
import os, re, subprocess, sys, time

POSEN = os.path.expanduser("~/Library/CloudStorage/Dropbox/03 Apps/Yoga/posen")
SKRIPT = os.path.expanduser("~/.claude/skills/codex-bild/scripts/codex-bild.sh")
sys.path.insert(0, os.path.dirname(__file__))
from zeichnen import STIL_VORN  # gleicher Stil wie die übrigen Zeichnungen

STIL_HINTEN = ("\n\nA simple wooden chair without armrests is used as a prop; if she stands, it is placed on or next to "
               "a light blue yoga mat. Soft, even lighting, gentle shading, smooth semi-realistic illustration style like a "
               "modern instruction manual. Anatomically correct, safe alignment for older beginners. Whole body and chair "
               "visible, centered, with some space around.")

# id: (Anleitung, Bildbeschreibung oder None, wenn es schon eine Stuhl-Zeichnung gibt)
CHAIR = {
 # Warm-up
 "mountain-pose": (["Sit on the front half of the chair","Feet flat, hip-width, knees over ankles","Hands rest on the thighs","Lengthen the spine, crown reaches up","Shoulders relax, breathe calmly"],
   "Seated Mountain Pose: sitting upright on the front half of the chair, feet flat and hip-width, hands resting on the thighs, spine tall, seen from the side."),
 "upward-salute": (["Sit tall on the front of the chair","Feet flat, hip-width","Inhale, sweep the arms up","Palms face each other, shoulders soft","Exhale, lower the arms"],
   "Seated Upward Salute: sitting tall on the chair, feet flat, both arms raised straight overhead, palms facing each other, seen from the front."),
 "standing-forward-bend": (["Sit on the front of the chair, feet hip-width","Inhale, lengthen the spine","Exhale, fold forward over the thighs","Let the arms and head hang toward the floor","Roll up slowly, head last"],
   "Seated Forward Bend on a chair: sitting on the front of the chair, folded forward over the thighs, arms and head hanging relaxed toward the floor, seen from the side."),
 "standing-half-forward-bend": (["Stand facing the chair back","Hands on the top of the chair back","Walk the feet back until the torso is horizontal","Hips over the heels, back long and flat","Walk back in to come up"],
   "Half Forward Bend with chair: standing, hands resting on the top of the chair back, feet walked back so the torso is horizontal with a long flat back, seen from the side."),
 "garland-pose": (["Sit on the front of the chair, feet wide, toes out","Knees open wide","Palms together at the heart","Elbows press gently into the inner knees","Spine long, breathe"],
   "Chair Garland Pose: sitting on the front edge of the chair, feet wide with toes turned out, knees wide, palms together at the heart, elbows against the inner knees, seen from the front."),
 "gate-pose": (["Sit sideways near the front of the chair","Extend the right leg out to the side, foot flat","Left hand on the chair seat","Inhale, raise the left arm","Exhale, bend over the right leg, switch sides"],
   "Chair Gate Pose: sitting on the chair, right leg extended out to the side with the foot flat, left arm arching over the head toward the right in a side bend, seen from the front."),
 "low-lunge": (["Sit sideways on the chair, right thigh on the seat","Left leg extends back, knee toward the floor","Hold the chair back for support","Lengthen the spine, open the front of the left hip","Switch sides"],
   "Chair Low Lunge: sitting sideways on the chair with the right thigh on the seat, left leg reaching back behind the chair with the knee lowered toward the floor, right hand holding the chair back, torso upright, seen from the side."),
 "cat-pose": (["Sit on the front of the chair, hands on the knees","Exhale, round the back","Tuck the chin, draw the belly in","Shoulders forward","Inhale, return to upright"],
   "Seated Cat Pose on a chair: sitting on the front of the chair, hands on the knees, back rounded, chin tucked, belly drawn in, seen from the side."),
 "childs-pose": (["Sit on the front of the chair, feet wide","Fold forward, belly rests on the thighs","Arms hang or rest on the floor","Head relaxed","Breathe into the back, rise slowly"],
   "Chair Child’s Pose: sitting on the chair with feet wide, folded forward so the belly rests on the thighs, arms hanging toward the floor, head relaxed, seen from the side."),
 "plank-pose": (["Hands on the front edge of a stable chair seat","Walk the feet back, body in one line","Press the seat away, belly in","Hold several breaths","Walk the feet in to come up"],
   "Incline Plank with chair: hands on the front edge of a chair seat, chair stable against a wall, arms straight, feet walked back so the body forms a straight diagonal line, seen from the side."),
 "extended-puppy-pose": (["Stand facing the chair back, a step away","Hands on the top of the chair back","Walk the feet back, hips over the heels","Let the chest sink toward the floor","Arms long, breathe into the shoulders"],
   "Extended Puppy with chair: standing, hands on the top of the chair back, feet walked back, hips over the heels, chest and head sinking between the arms, arms long, seen from the side."),
 "cobra-pose": (["Sit on the front of the chair, hands on the seat behind the hips","Inhale, lift the chest","Draw the shoulder blades together","Gaze forward or slightly up","Exhale, return"],
   "Seated chest opener on a chair (chair Cobra): sitting on the front of the chair, hands holding the back edge of the seat behind the hips, chest lifted and open, shoulder blades together, gaze forward, seen from the side."),
 # Build-up
 "boat-pose": (["Sit on the front half of the chair, hold the sides of the seat","Lean back slightly, spine long","Lift one foot, then the other","Shins parallel to the floor","Hold several breaths, lower slowly"],
   "Chair Boat Pose: sitting on the front half of the chair, hands holding the sides of the seat, leaning back slightly with a long spine, both feet lifted with the shins parallel to the floor, seen from the side."),
 "chair-pose": (["Sit on the front of the chair, feet hip-width","Arms reach forward","Lean forward and lift the hips just off the seat","Hover a few breaths","Sit down slowly"],
   "Chair Pose with chair: the hips hovering just above the seat of a chair, knees bent over the ankles, torso leaning slightly forward, arms reaching forward and up, seen from the side."),
 "half-moon-pose": (["Stand with the chair in front of the right foot","Right hand on the chair seat","Shift weight onto the right leg","Lift the left leg to hip height","Open the chest and left arm up, switch sides"],
   "Half Moon Pose with chair: standing on the straight right leg, right hand resting on the seat of a chair in front, left leg lifted to hip height, left arm up, chest open, seen from the front."),
 "high-lunge": (["Sit sideways on the chair, right thigh on the seat","Left leg extends straight back, heel lifted","Torso upright","Raise the arms overhead","Switch sides"],
   "Chair High Lunge: sitting sideways on the chair, right thigh on the seat, left leg extended straight back behind the chair on the ball of the foot, torso upright, both arms raised overhead, seen from the side."),
 "high-lunge-crescent-variation": (["Sit sideways on the chair, right thigh on the seat","Left leg long behind","Raise the arms overhead","Lift the chest, gentle upper back arch","Switch sides"],
   'Chair Crescent Lunge: sitting sideways on the chair, right thigh on the seat, left leg extended back behind the chair, arms raised overhead and slightly back, chest lifted in a gentle upper back arch, seen from the side.'),
 "intense-side-stretch-pose": (["Stand facing the chair, right foot forward, left foot back","Hands on the chair seat","Hips square","Fold forward with a long back","Switch sides"],
   "Pyramid Pose with chair: right foot forward and left foot back, both legs straight, folding forward with a long flat back, hands resting on the seat of a chair in front, seen from the side."),
 "revolved-side-angle-pose": (["Sit sideways on the chair, right thigh on the seat","Left leg extends back","Palms together at the heart","Twist toward the right, elbow outside the right knee","Switch sides"],
   "Chair Revolved Side Angle: sitting sideways on the chair, right thigh on the seat, left leg extended back, palms together at the chest, torso twisted to the right with the left elbow outside the right knee, seen from the front."),
 "revolved-triangle-pose": (["Stand with the right foot forward, chair inside the right foot","Left hand on the chair seat","Twist the chest to the right","Right arm reaches up","Switch sides"],
   "Revolved Triangle with chair: right foot forward, both legs straight, left hand resting on the seat of a chair placed inside the front foot, torso twisted to the right, right arm reaching up, seen from the front."),
 "side-plank-pose": (["Right hand on a stable chair seat","Step the feet out to the left, stack them or stagger","Lift the hips, body in one line","Left arm up","Switch sides"],
   "Incline Side Plank with chair: right hand on the seat of a stable chair, body sideways in a straight diagonal line, feet staggered on the floor, left arm reaching up, seen from the front."),
 "standing-split": (["Stand facing the chair, hands on the seat","Shift weight onto the right leg","Lift the left leg back","Fold the chest toward the seat","Switch sides"],
   "Standing Split with chair: folded forward, both hands on the seat of a chair, standing on the straight right leg, left leg lifted back and up, seen from the side."),
 "tree-pose": (["Stand beside the chair, hand on the chair back","Weight on the left foot","Right sole on the calf or thigh, never the knee","Other hand at the heart","Switch sides"],
   "Tree Pose with chair: standing on the left leg beside a chair, left hand resting on the chair back, right sole against the inner left calf, right hand at the heart, seen from the front."),
 "warrior-i-pose": (["Sit sideways on the chair, right thigh on the seat","Left leg extends back, foot turned out, heel down","Torso upright","Arms reach overhead","Switch sides"],
   "Chair Warrior I: sitting sideways on the chair, right thigh on the seat and right knee over the ankle, left leg extended back with the heel down and foot turned out, torso upright, arms raised overhead, seen from the side."),
 "warrior-ii-pose": (["Sit sideways on the chair, right thigh on the seat","Left leg extends out to the left, foot flat","Arms out at shoulder height","Gaze over the right hand","Switch sides"],
   "Chair Warrior II: sitting on the chair with the right thigh on the seat and right knee bent over the ankle, left leg extended straight out to the side with the foot flat, arms stretched out at shoulder height, gazing over the right hand, seen from the front."),
 "warrior-iii-pose": (["Stand facing the chair back, hands on top","Step back, weight on the right leg","Lean forward, lift the left leg back","Body from hands to heel in one line","Switch sides"],
   "Warrior III with chair: hands resting on the top of a chair back, torso leaning forward horizontal, standing on the straight right leg, left leg lifted straight back to hip height, seen from the side."),
 "wide-legged-forward-bend": (["Sit on the front of the chair, feet wide","Hands on the thighs","Inhale, lengthen","Exhale, fold forward between the knees","Roll up slowly"],
   "Chair wide-legged forward bend: sitting on the front of the chair with the feet wide apart, folded forward between the knees, hands toward the floor, seen from the front."),
 "extended-hand-to-big-toe-pose": (["Stand beside the chair, hand on the chair back","Lift the right knee, hold it or use a strap","Extend the leg forward as far as is comfortable","Stand tall","Switch sides"],
   "Extended Hand-to-Big-Toe Pose with chair: standing tall on the left leg, left hand on the back of a chair beside her, right leg lifted forward with a strap around the foot held in the right hand, seen from the side."),
 # Cool-down
 "bharadvajas-twist": (["Sit sideways on the chair, right side to the chair back","Hands on the chair back","Inhale, lengthen","Exhale, twist toward the chair back","Switch sides"],
   "Chair Bharadvaja’s Twist: sitting sideways on the chair with the right side toward the chair back, both hands holding the chair back, torso twisting toward it, spine tall, seen from the front."),
 "fire-log-pose": (["Sit tall on the chair","Right ankle on the left knee","Flex the right foot","Optional: fold forward with a long back","Switch sides"],
   "Chair Fire Log / Figure Four: sitting tall on the chair, right ankle resting on the left knee, right foot flexed, hands on the shin, seen from the front."),
 "pigeon-pose": (["Sit tall on the chair","Right ankle on the left knee, foot flexed","Hands on the shin","Lean forward with a long back","Switch sides"],
   'Chair Pigeon / Figure Four: sitting on the chair, right ankle resting on the left knee with the foot flexed, leaning forward with a long back, hands on the right shin, seen from the side.'),
 "half-lord-of-the-fishes-pose": (["Sit tall on the chair, feet flat","Right hand on the chair back behind you","Left hand on the right knee","Inhale, lengthen; exhale, twist right","Switch sides"],
   "Chair Seated Twist: sitting tall on the chair, feet flat, twisting to the right, right hand on the chair back behind her, left hand on the right knee, seen from the front."),
 "marichis-pose": (["Sit tall on the chair, feet flat","Right foot on a block or the chair rung, knee higher","Twist toward the right knee","Left elbow outside the right knee","Switch sides"],
   'Chair Marichi twist: sitting tall on the chair, right foot raised on a yoga block so the right knee is higher, torso twisted to the right, left elbow outside the right knee, right hand on the chair back, seen from the front.'),
 "head-to-knee-pose": (["Sit on the front of the chair","Extend the left leg, heel down, toes up","Right foot flat","Fold forward over the left leg","Switch sides"],
   "Chair Head-to-Knee: sitting on the front of the chair, left leg extended forward with the heel on the floor and toes up, right foot flat, folding forward with a long back over the left leg, hands on the left shin, seen from the side."),
 "revolved-head-to-knee-pose": (["Sit on the front of the chair","Extend the left leg out to the side","Left forearm on the left thigh","Right arm reaches over the head to the left","Switch sides"],
   "Chair Revolved Head-to-Knee: sitting on the front of the chair, left leg extended out to the side, left forearm resting on the left thigh, right arm reaching over the head toward the left, side body stretched, seen from the front."),
 "seated-forward-bend": (["Sit on the front of the chair","Extend both legs, heels down","Inhale, lengthen","Exhale, fold forward with a long back","Hands on the shins"],
   "Chair Seated Forward Bend: sitting on the front of the chair, both legs extended straight forward with the heels on the floor, folding forward with a long back, hands on the shins, seen from the side."),
 "staff-pose": (["Sit on the front of the chair","Extend both legs, heels down, feet flexed","Hands on the seat beside the hips","Spine long","Breathe"],
   "Chair Staff Pose: sitting tall on the front of the chair, both legs extended straight forward, heels on the floor, feet flexed, hands on the seat beside the hips, seen from the side."),
 "wide-angle-seated-forward-bend": (["Sit on the front of the chair","Extend the legs wide, heels down","Inhale, lengthen","Exhale, fold forward between the legs","Roll up slowly"],
   'Chair Wide-Angle Forward Bend: sitting on the front of the chair, both legs extended wide apart with the heels on the floor, folding forward between the legs with a long back, hands toward the floor, seen from the front.'),
 "camel-pose": (["Sit on the front of the chair","Hands on the back of the seat or the chair back","Inhale, lift the chest","Gentle upper back arch","Neck long, return slowly"],
   'Chair Camel: sitting on the front of the chair, hands holding the chair back behind her, chest lifted and opened in a gentle backbend, neck long, gaze slightly up, seen from the side.'),
 "lord-of-the-dance-pose": (["Stand beside the chair, left hand on the chair back","Bend the right knee, hold the foot or a strap","Kick gently into the hand","Chest forward a little","Switch sides"],
   "Lord of the Dance with chair: standing on the left leg, left hand on the back of a chair in front, right knee bent with the right hand holding the right foot behind, gentle kick back, chest slightly forward, seen from the side."),
 "legs-up-the-wall-pose": (["Lie on the back in front of the chair","Rest the calves on the chair seat","Knees bent at about 90 degrees","Arms relaxed, palms up","Stay several minutes"],
   "Legs on a chair (restorative): lying on her back on the mat, calves resting on the seat of a chair, knees bent at 90 degrees, arms relaxed with palms up, eyes closed, seen from the side."),
 "reclining-hand-to-big-toe-pose": (["Sit on the front of the chair","Strap around the right foot","Lift and straighten the right leg as far as is comfortable","Sit tall","Switch sides"],
   'Chair Hand-to-Big-Toe: sitting tall on the chair, a strap around the right foot held with both hands, right leg lifted and extended forward, left foot flat, seen from the side.'),
 "bound-angle-pose": (["Sit on the front of the chair","Place the feet wide, soles turned in slightly","Let the knees open","Hands on the thighs","Spine long"],
   'Chair Bound Angle: sitting on the front of the chair, feet wide apart with the soles turned slightly inward, knees falling open, hands on the thighs, spine long, seen from the front.'),
}
# Vorhandene Stuhl-Zeichnungen (Notion): nur Text ergänzen
for k in ["easy-pose", "cow-pose", "cow-face-pose", "eagle-pose", "dolphin-pose", "dolphin-plank-pose",
          "downward-facing-dog", "extended-triangle-pose", "extended-side-angle-pose", "corpse-pose"]:
    CHAIR.setdefault(k, None)
TEXT_VORHANDEN = {
 "easy-pose": ["Sit tall on the chair, feet flat or ankles crossed","Hands rest on the knees","Spine long, shoulders soft","Close the eyes, breathe"],
 "cow-pose": ["Sit on the front of the chair, hands on the knees","Inhale, lift the chest","Arch the back gently","Gaze slightly up","Alternate with Cat"],
 "cow-face-pose": ["Sit tall on the chair, feet grounded","One arm lifts, bends behind the head","Other arm reaches up the back","Use a strap if the hands don’t meet","Switch sides"],
 "eagle-pose": ["Sit tall on the chair","Cross the right thigh over the left","Wrap the arms, right under left","Lift the elbows","Switch sides"],
 "dolphin-pose": ["Forearms on the chair seat","Walk the feet back","Lift the hips, back long","Head between the arms","Breathe, walk in"],
 "dolphin-plank-pose": ["Forearms on the chair seat","Walk the feet back, body in one line","Belly in","Hold several breaths","Walk in to come up"],
 "downward-facing-dog": ["Hands on the chair seat or back","Walk the feet back","Hips lift, spine long","Head between the arms","Walk in to come up"],
 "extended-triangle-pose": ["Wide stance, chair beside the front foot","Front hand on the chair seat","Top arm reaches up","Chest opens","Switch sides"],
 "extended-side-angle-pose": ["Sit sideways on the chair, front thigh on the seat","Back leg extends long","Forearm on the front thigh","Top arm reaches over","Switch sides"],
 "corpse-pose": ["Sit back in the chair, feet flat","Hands rest on the thighs, palms up","Close the eyes","Let the body be heavy","Breathe naturally"],
}


def datei(pid):
    return os.path.join(POSEN, pid + ".md")


def texte():
    for pid, val in CHAIR.items():
        schritte = TEXT_VORHANDEN.get(pid) if val is None and pid in TEXT_VORHANDEN else (val[0] if val else None)
        if not schritte:
            print("kein Text:", pid); continue
        s = open(datei(pid), encoding="utf-8").read()
        s = re.sub(r"^chair:.*$", "chair: yes", s, count=1, flags=re.M)
        block = "## Chair version\n\n" + "\n".join(f"{i}. {x}" for i, x in enumerate(schritte, 1)) + "\n\n"
        if "## Chair version" in s:
            s = re.sub(r"## Chair version\n.*?(?=\n## |\Z)", block.rstrip("\n") + "\n", s, flags=re.S)
        elif "## Cue card" in s:
            s = s.replace("## Cue card", block + "## Cue card", 1)
        else:
            s = s.rstrip() + "\n\n" + block
        open(datei(pid), "w", encoding="utf-8").write(s)
    print(len(CHAIR), "Posen mit Chair version")


def bilder(ids):
    ids = ids or [k for k, v in CHAIR.items() if v and v[1] and not os.path.exists(os.path.join(POSEN, "bilder", k + "-chair.png"))]
    print(len(ids), "Stuhl-Zeichnungen, nacheinander", flush=True)
    for i, pid in enumerate(ids, 1):
        ziel = os.path.join(POSEN, "bilder", pid + "-chair.png")
        t = time.time()
        r = subprocess.run(["zsh", SKRIPT, ziel], input=STIL_VORN + "Pose: " + CHAIR[pid][1] + STIL_HINTEN,
                           capture_output=True, text=True)
        pfad = (r.stdout.strip().splitlines() or [""])[-1]
        if r.returncode == 0 and os.path.isfile(pfad):
            name = os.path.basename(pfad)
            s = open(datei(pid), encoding="utf-8").read()
            m = re.search(r"^images:(.*)$", s, re.M)
            liste = [x.strip() for x in m.group(1).split(",") if x.strip() and "-chair" not in x]
            s = s[:m.start()] + "images: " + ", ".join(liste + [name]) + s[m.end():]
            open(datei(pid), "w", encoding="utf-8").write(s)
            print(f"[{i}/{len(ids)}] ok {pid} ({int(time.time() - t)} s)", flush=True)
        else:
            print(f"[{i}/{len(ids)}] FEHLER {pid}: {(r.stderr or r.stdout).strip()[-300:]}", flush=True)
    print("fertig", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["texte"]:
        texte()
    elif sys.argv[1:2] == ["bilder"]:
        bilder(sys.argv[2:])
    else:
        sys.exit(__doc__)
