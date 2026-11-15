#!/usr/bin/env python3
"""Lässt fehlende Posen-Zeichnungen über den Skill codex-bild erzeugen, eine nach der anderen.

Stil wie die Boat-Pose-Zeichnung: Frau um die 60, kurze graue Haare, korallenfarbenes Shirt,
salbeigrüne Leggings, hellblaue Matte, cremeweißer Hintergrund.

Aufruf:  python3 tools/zeichnen.py [id ...]     (ohne ids: alle Posen ohne Bild, für die es eine Beschreibung gibt)
Danach:  python3 tools/daten-bauen.py
"""
import os, re, subprocess, sys, time

POSEN = os.path.expanduser("~/Library/CloudStorage/Dropbox/03 Apps/Yoga/posen")
SKRIPT = os.path.expanduser("~/.claude/skills/codex-bild/scripts/codex-bild.sh")

STIL_VORN = ("Clean, friendly digital illustration of a yoga pose for a yoga learning app. "
             "Landscape format 3:2, plain off-white background, no text, no logos.\n\n"
             "Person: a fit woman around 60 years old with very short grey pixie-cut hair, wearing a coral-pink "
             "short-sleeved t-shirt and sage-green leggings, barefoot. Natural, kind expression.\n\n")
STIL_HINTEN = ("\n\nShe is on a light blue yoga mat shown in slight perspective. Soft, even lighting, gentle shading, "
               "smooth semi-realistic illustration style like a modern instruction manual. Anatomically correct, "
               "correct yoga alignment. Whole body visible, centered, with some space around.")

# Reihenfolge = Reihenfolge beim Zeichnen (Build-up zuerst)
POSES = {
 # Build-up
 "four-limbed-staff-pose": "Four-Limbed Staff Pose (Chaturanga Dandasana), side view. Low plank: body in one straight line parallel to the floor, a hand's width above it, on hands and toes. Elbows bent 90 degrees, pointing straight back and hugging the ribs, shoulders at elbow height.",
 "half-moon-pose": "Half Moon Pose (Ardha Chandrasana), seen from the front. She balances on her straight right leg, right hand on a yoga block on the floor about a foot in front of the right foot. Torso horizontal and open to the side, left leg lifted straight back to hip height, parallel to the floor. Left arm extends straight up to the ceiling, hips stacked.",
 "high-lunge": "High Lunge, side view. Right foot forward, right knee bent directly over the ankle. Left leg straight back, on the ball of the left foot with the heel lifted. Torso upright over the hips, both arms raised straight overhead, palms facing each other.",
 "high-lunge-crescent-variation": "Crescent Lunge (Ashta Chandrasana), side view. Right foot forward, right knee bent over the ankle, left leg straight back on the ball of the foot, heel lifted. Arms raised overhead and slightly back, chest lifted with a gentle arch in the upper back, gaze slightly up.",
 "intense-side-stretch-pose": "Intense Side Stretch Pose / Pyramid Pose (Parsvottanasana), side view. Right foot forward, left foot back about one leg length and turned out 45 degrees, both legs straight, hips square. Torso folded forward over the front leg with a long flat back, hands resting on two yoga blocks on either side of the front foot.",
 "locust-pose": "Locust Pose (Salabhasana), side view. Lying on her belly. Head, chest, and both arms lifted off the floor, arms alongside the body with palms facing down. Both straight legs lifted off the floor too. Neck long, gaze down and forward.",
 "plank-pose": "Plank Pose, side view. Arms straight, hands directly under the shoulders, on her toes. Body in one straight line from head to heels, neck long.",
 "reverse-plank-pose": "Reverse Plank Pose (Purvottanasana), side view. Face up. Hands on the floor behind the hips, fingers pointing toward the feet, arms straight. Hips lifted so the body forms a straight inclined line from shoulders to feet, legs straight, soles pressing toward the floor, chest open.",
 "revolved-side-angle-pose": "Revolved Side Angle Pose (Parivrtta Parsvakonasana), three-quarter front view. Lunge with right foot forward, right knee bent over the ankle, left leg straight back, heel lifted. Torso twisted to the right, left elbow hooked outside the right knee, palms pressed together in prayer at the chest, chest turned up toward the ceiling.",
 "revolved-triangle-pose": "Revolved Triangle Pose (Parivrtta Trikonasana), three-quarter front view. Short stance, right foot forward, both legs straight. Torso folded forward and twisted to the right, left hand on a yoga block outside the right foot, right arm extended straight up toward the ceiling.",
 "side-plank-pose": "Side Plank Pose (Vasisthasana), seen from the front. Balancing on the straight right arm, hand under the shoulder, and the outer edge of the right foot, feet stacked. Body in one straight diagonal line, hips lifted, left arm extended straight up toward the ceiling.",
 "side-reclining-leg-lift": "Side-Reclining Leg Lift (Anantasana), seen from the front. Lying on her right side, head resting on the right hand with the elbow on the floor, bottom leg straight on the mat. Top leg raised straight up toward the ceiling, left hand holding the big toe of the raised foot.",
 "standing-split": "Standing Split (Urdhva Prasarita Eka Padasana), side view. Folded forward standing on the straight right leg, hands on the floor beside the right foot, chest toward the shin. Left leg lifted straight back and high up toward the ceiling.",
 "upward-facing-dog-pose": "Upward-Facing Dog (Urdhva Mukha Svanasana), side view. Arms straight, hands under the shoulders, chest lifted forward and up. Hips and thighs lifted off the floor, only the hands and the tops of the feet touch the mat. Shoulders down away from the ears, gaze forward.",
 "warrior-i-pose": "Warrior I (Virabhadrasana I), side view. Right foot forward, right knee bent over the ankle. Left leg straight back, left foot turned out 45 degrees with the heel down. Hips facing forward, torso upright, both arms raised overhead, palms facing each other.",
 "warrior-iii-pose": "Warrior III (Virabhadrasana III), side view. Balancing on the straight right leg. Torso and left leg horizontal, forming a T-shape with the standing leg. Arms extended forward parallel to the floor, body in one long line from fingertips to lifted heel.",
 "wide-legged-forward-bend": "Wide-Legged Forward Bend (Prasarita Padottanasana), seen from the front. Feet wide apart and parallel, legs straight. Folded forward from the hips, crown of the head toward the floor between the feet, hands flat on the floor under the shoulders, elbows bent back.",
 # Warm-up
 "garland-pose": "Garland Pose (Malasana), seen from the front. Deep squat, feet slightly wider than hips, heels down. Knees wide, elbows pressing against the inner knees, palms together in prayer at the heart, spine upright.",
 "gate-pose": "Gate Pose (Parighasana), seen from the front. Kneeling on the left knee, right leg extended straight out to the side, right foot flat. Right hand resting on the right leg, left arm arching over the head toward the right, long stretch along the left side of the body.",
 "low-lunge": "Low Lunge (Anjaneyasana), side view. Right foot forward, right knee bent over the ankle. Left knee and top of the left foot resting on the mat behind. Torso upright, arms raised overhead.",
 "mountain-pose": "Mountain Pose (Tadasana), seen from the front. Standing tall, feet together, weight even, arms alongside the body with palms facing forward, shoulders relaxed, calm upright posture.",
 "sphinx-pose": "Sphinx Pose (Salamba Bhujangasana), side view. Lying on her belly, forearms on the floor parallel to each other, elbows under the shoulders. Chest lifted, legs extended straight back, tops of the feet on the mat, gaze forward.",
 "standing-forward-bend": "Standing Forward Bend (Uttanasana), side view. Feet hip-width apart, legs straight with soft knees. Torso folded fully forward over the legs, hands on the floor beside the feet, head and neck relaxed.",
 "standing-half-forward-bend": "Standing Half Forward Bend (Ardha Uttanasana), side view. Legs straight, torso folded forward to horizontal with a long flat back, hands resting on the shins, gaze down and slightly forward.",
 "upward-salute": "Upward Salute (Urdhva Hastasana), seen from the front. Standing tall with feet together, both arms raised straight overhead, palms facing each other, gaze slightly up.",
 # Peak
 "feathered-peacock-pose": "Forearm Stand / Feathered Peacock Pose (Pincha Mayurasana), side view. Forearms on the floor, parallel, shoulder-width apart. Body upside down and vertical in one straight line, legs together pointing straight up, head off the floor, gaze between the hands.",
 "firefly-pose": "Firefly Pose (Tittibhasana), seen from the front. Balancing on both hands, arms straight. Legs straight and extended forward and wide, backs of the thighs resting high on the upper arms, feet off the floor.",
 "half-frog-pose": "Half Frog Pose (Ardha Bhekasana), side view. She lies face down on her belly, hips and thighs flat on the mat. Upper body propped up on the left forearm, elbow under the shoulder. Right knee bent so the right heel comes toward the right buttock; right hand reaches back and presses the top of the right foot down toward the floor beside the hip. Left leg straight on the mat. Chest lifted, gaze forward.",
 "handstand": "Handstand (Adho Mukha Vrksasana), side view. Balanced on both hands, arms straight, shoulders over the wrists. Body upside down, vertical and straight, legs together pointing up.",
 "lord-of-the-dance-pose": "Lord of the Dance Pose (Natarajasana), side view. Standing on the straight left leg. Right knee bent, right hand holding the inside of the right foot behind her, kicking the foot up and back. Chest leaning forward, left arm reaching forward and up.",
 "monkey-pose": "Monkey Pose / Front Splits (Hanumanasana), side view. Right leg extended straight forward, left leg extended straight back, hips lowered toward the floor with a yoga block under the right hamstring for support. Torso upright, hands on blocks on either side.",
 "one-legged-king-pigeon-pose": "One-Legged King Pigeon Pose (Eka Pada Rajakapotasana), side view. Pigeon base: right shin forward on the mat, left leg back. Left knee bent with the foot lifted toward the head, both hands reaching overhead to hold the left foot, deep backbend with chest lifted.",
 "one-legged-king-pigeon-pose-ii": "One-Legged King Pigeon Pose II, side view. From a low lunge: right foot forward, right knee bent over the ankle, left knee on the mat. Left knee bent, foot lifted toward the head, both hands holding the left foot overhead, chest lifted in a backbend.",
 "peacock-pose": "Peacock Pose (Mayurasana), side view. Balancing on both hands with the fingers pointing back toward the feet, elbows bent and pressing into the belly. Body horizontal and straight like a plank, legs extended back, feet off the floor.",
 "rope-pose": "Rope Pose (Pasasana), seen from the front. Deep squat with feet and knees together, heels down. Torso twisted to the right, left arm wrapped around the outside of both knees, hands binding behind the back.",
 "sage-koundinya-i": "Sage Koundinya I (Eka Pada Koundinyasana I), three-quarter view. Twisted arm balance on both hands, elbows bent 90 degrees. Torso horizontal and twisted, both legs extended straight out to one side, one above the other, feet off the floor.",
 "sage-koundinya-ii": "Sage Koundinya II (Eka Pada Koundinyasana II), side view. Arm balance on both hands, elbows bent 90 degrees, torso horizontal. Front leg extended straight forward, resting on the upper arm; back leg extended straight back; both feet off the floor.",
 "scale-pose": "Scale Pose (Tolasana), seen from the front. Seated with legs crossed in lotus, hands pressing into the floor beside the hips, arms straight, lifting the whole body including the crossed legs off the floor.",
 "shoulder-pressing-pose": "Shoulder-Pressing Pose (Bhujapidasana), seen from the front. Balancing on both hands, arms bent slightly. Legs wrapped over the upper arms, ankles crossed in front, feet off the floor.",
 "side-crane-crow-pose": "Side Crow (Parsva Bakasana), side view. Squatting with knees together, torso twisted, both hands on the floor. Outer right thigh resting on the left upper arm, elbows bent, feet lifted off the floor and stacked.",
 "supported-headstand": "Supported Headstand (Salamba Sirsasana), side view. Forearms on the floor, fingers interlaced and cradling the back of the head, crown of the head on the mat. Body upside down, vertical, legs straight and together pointing up.",
 "two-foot-staff-pose": "Two-Foot Inverted Staff Pose (Dwi Pada Viparita Dandasana), side view. Deep backbend: forearms on the floor, fingers interlaced behind the head, head resting on the mat. Chest open and lifted, legs extended straight, feet flat on the floor.",
 "upward-bow-pose": "Upward Bow / Wheel Pose (Urdhva Dhanurasana), side view. Full backbend with hands and feet on the floor, arms straight. Hips and chest lifted high so the body forms a round arch.",
 "wild-thing": "Wild Thing (Camatkarasana), three-quarter view. From side plank on the right hand: left foot stepped behind and landed, hips lifted high, chest open to the sky in a backbend, left arm reaching overhead.",
 # Cool-down
 "bharadvajas-twist": "Bharadvaja's Twist (Bharadvajasana I), seen from the front. Seated with both legs folded to the left side. Torso twisted to the right, left hand on the right knee, right hand on the floor behind her, spine upright.",
 "big-toe-pose": "Big Toe Pose (Padangusthasana), side view. Standing forward fold, legs straight. Index and middle fingers hooked around the big toes, torso long and folded over the legs.",
 "bound-angle-pose": "Bound Angle Pose (Baddha Konasana), seen from the front. Seated upright, soles of the feet together, knees open to the sides, hands holding the feet.",
 "fire-log-pose": "Fire Log Pose (Agnistambhasana), seen from the front. Seated upright, shins stacked parallel to the front edge of the mat, right shin on top of the left, right ankle over the left knee. Hands resting beside the hips.",
 "fish-pose": "Fish Pose (Matsyasana), side view. Lying on her back, legs straight. Upper back arched with the chest lifted, crown of the head resting lightly on the floor, forearms on the floor beside the body.",
 "half-lord-of-the-fishes-pose": "Half Lord of the Fishes Pose (Ardha Matsyendrasana), seen from the front. Seated. Left leg bent with the foot beside the right hip, right foot standing outside the left knee. Torso twisted to the right, left elbow outside the right knee, right hand on the floor behind.",
 "hero-pose": "Hero Pose (Virasana), three-quarter view. Kneeling with knees together, sitting on a yoga block between the heels, hands resting on the thighs, spine upright.",
 "happy-baby-pose": "Happy Baby Pose (Ananda Balasana), side view. Lying on her back, knees bent toward the armpits, shins vertical, hands holding the outer edges of the feet, soles facing the ceiling.",
 "heron-pose": "Heron Pose (Krounchasana), side view. Seated, left leg folded back beside the hip as in Hero Pose. Right leg lifted straight up toward the face, both hands holding the right foot, spine upright.",
 "head-to-knee-pose": "Head-to-Knee Pose (Janu Sirsasana), side view. Seated, left leg extended straight, right knee bent with the sole against the inner left thigh. Torso folded forward over the left leg, hands holding the left foot.",
 "legs-up-the-wall-pose": "Legs-Up-the-Wall Pose (Viparita Karani), side view. Lying on her back with the hips close to a light wall, legs straight up resting on the wall, arms relaxed beside the body, eyes closed.",
 "lotus-pose": "Lotus Pose (Padmasana), seen from the front. Seated cross-legged with each foot resting on the opposite thigh, hands resting on the knees, spine upright, eyes closed, peaceful.",
 "marichis-pose": "Marichi's Pose (Marichyasana III), seen from the front. Seated, left leg straight, right knee bent with the foot flat near the hip. Torso twisted to the right, left elbow outside the right knee, right hand on the floor behind.",
 "pigeon-pose": "Pigeon Pose (Eka Pada Rajakapotasana prep), three-quarter view. Right shin forward on the mat, knee bent. Left leg extended straight back, top of the foot down. Hips square, torso upright, fingertips on the floor.",
 "plow-pose": "Plow Pose (Halasana), side view. On the shoulders, hips over the shoulders, legs straight overhead with the toes touching the floor behind the head, arms on the floor.",
 "reclining-hand-to-big-toe-pose": "Reclining Hand-to-Big-Toe Pose (Supta Padangusthasana), side view. Lying on her back, left leg straight on the floor. Right leg raised straight up, right hand holding the big toe of the raised foot.",
 "reclining-hero-pose": "Reclining Hero Pose (Supta Virasana), side view. From Hero Pose (kneeling, sitting between the heels) she lies back with her back on a bolster, knees together on the floor, arms relaxed.",
 "revolved-head-to-knee-pose": "Revolved Head-to-Knee Pose (Parivrtta Janu Sirsasana), seen from the front. Seated, left leg extended out to the side, right knee bent with the foot at the inner left thigh. Torso side-bending toward the left leg and turned up, right arm reaching over the head toward the left foot.",
 "sage-marichi-i": "Sage Marichi I (Marichyasana I), side view. Seated, left leg straight, right knee bent with the foot flat. Right arm wrapped around the right shin, hands clasped behind the back, torso folded forward over the left leg.",
 "seated-forward-bend": "Seated Forward Bend (Paschimottanasana), side view. Seated with legs straight together, torso folded forward over the legs, hands holding the feet.",
 "staff-pose": "Staff Pose (Dandasana), side view. Seated upright, legs straight together in front, feet flexed, hands on the floor beside the hips.",
 "supported-shoulderstand": "Supported Shoulderstand (Salamba Sarvangasana), side view. Balanced on the shoulders and upper arms, hands supporting the lower back, body vertical and straight, legs together pointing up.",
 "wide-angle-seated-forward-bend": "Wide-Angle Seated Forward Bend (Upavistha Konasana), seen from the front. Seated with legs straight and wide apart, torso folded forward between the legs, hands reaching forward on the floor.",
 # Fotos durch Zeichnungen ersetzen
 "bow-pose": "Bow Pose (Dhanurasana), side view. Lying on her belly, both knees bent, hands holding the outer ankles behind her. Chest and thighs lifted off the floor, the body forming a bow shape, gaze forward.",
 # Relaxation
 "reclining-bound-angle-pose": "Reclining Bound Angle Pose (Supta Baddha Konasana), three-quarter view. Lying on her back, soles of the feet together, knees falling open to the sides, arms relaxed beside the body with palms up, eyes closed.",
}


def kopf_bilder(pid):
    return re.search(r"^images:(.*)$", open(os.path.join(POSEN, pid + ".md"), encoding="utf-8").read(), re.M).group(1).strip()


def setze_bild(pid, name):
    p = os.path.join(POSEN, pid + ".md")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"^images:.*$", "images: " + name, s, count=1, flags=re.M)
    open(p, "w", encoding="utf-8").write(s)


def main():
    ids = sys.argv[1:] or [k for k in POSES if not kopf_bilder(k)]
    fehlt = [k for k in ids if k not in POSES]
    if fehlt:
        sys.exit("Keine Beschreibung für: " + ", ".join(fehlt))
    print(f"{len(ids)} Zeichnungen, nacheinander", flush=True)
    fehler = []
    for i, pid in enumerate(ids, 1):
        ziel = os.path.join(POSEN, "bilder", pid + "-1.png")
        t = time.time()
        r = subprocess.run(["zsh", SKRIPT, ziel], input=STIL_VORN + "Pose: " + POSES[pid] + STIL_HINTEN,
                           capture_output=True, text=True)
        pfad = (r.stdout.strip().splitlines() or [""])[-1]
        if r.returncode == 0 and os.path.isfile(pfad):
            setze_bild(pid, os.path.basename(pfad))
            print(f"[{i}/{len(ids)}] ok {pid} ({int(time.time() - t)} s)", flush=True)
        else:
            fehler.append(pid)
            print(f"[{i}/{len(ids)}] FEHLER {pid}: {(r.stderr or r.stdout).strip()[-300:]}", flush=True)
            if "login" in (r.stderr or "").lower() or "limit" in (r.stderr or "").lower():
                print("Abbruch: Anmeldung oder Kontingent", flush=True)
                break
    print("fertig. Fehler:", ", ".join(fehler) or "keine", flush=True)


if __name__ == "__main__":
    main()
