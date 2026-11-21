#!/usr/bin/env python3
"""Montage des pubs LETTRIX / gommeo.com a partir des rushs fournis."""
import os, sys, subprocess, json, shutil, hashlib
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recolor as RC

S = os.path.dirname(os.path.abspath(__file__))
SRC = f"{S}/src"
VO = f"{S}/assets/vo"
SFX = f"{S}/assets/sfx"
CLIPS = f"{S}/clips"
WORK = f"{S}/work"
OUT = "/home/user/mes-videos-amine-ia/livrables"
for d in (CLIPS, WORK, OUT):
    os.makedirs(d, exist_ok=True)

FORMATS = {"9x16": (1080, 1920), "4x5": (1080, 1350), "1x1": (1080, 1080)}
SW, SH = 720, 1280  # taille source
INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
INTER_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
if not os.path.exists(INTER_BLACK):
    INTER_BLACK = INTER

ORANGE = "#F27800"


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("CMD FAIL:", " ".join(cmd)[:300])
        print(r.stderr[-1500:])
        raise SystemExit(1)
    return r


def dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)


# ---------------------------------------------------------------- plans
# (src, t0, t1, cx, cy, zoom, ymax)  ymax<1280 => on evite le filigrane en bas
def sh(src, t0, t1, cx, cy, z=1.0, ymax=1280, fx=None):
    return dict(src=src, t0=t0, t1=t1, cx=cx, cy=cy, z=z, ymax=ymax, fx=fx)


GOLD = [
    sh("v04", 0.0, 1.5, .58, .48, 1.30),
    sh("v04", 1.5, 3.0, .58, .50, 1.55),
    sh("v04", 3.0, 4.5, .55, .52, 1.30),
    sh("v04", 4.8, 6.3, .45, .55, 1.15),
    sh("v04", 6.3, 7.65, .35, .55, 1.30),
    sh("v04", 7.7, 9.3, .50, .62, 1.10),
    sh("v04", 9.3, 10.7, .50, .50, 1.10),
    sh("v04", 10.7, 11.65, .55, .40, 1.25),
    sh("v04", 11.7, 13.2, .55, .55, 1.00),
    sh("v04", 14.2, 15.8, .55, .55, 1.00),
    sh("v04", 15.8, 17.15, .55, .50, 1.15),
    sh("v04", 12.3, 13.8, .40, .45, 1.50),
    sh("v04", 15.0, 16.5, .55, .30, 1.60),
]
ORANGE_T = [
    sh("v01", 0.0, 1.2, .50, .48, 1.30),
    sh("v01", 1.2, 2.4, .50, .48, 1.55),
    sh("v01", 2.4, 3.5, .50, .48, 1.30),
    sh("v01", 3.6, 5.1, .50, .50, 1.20),
    sh("v01", 5.9, 7.4, .45, .50, 1.20),
    sh("v01", 10.3, 11.9, .50, .55, 1.00),
    sh("v01", 11.9, 13.3, .50, .55, 1.00),
    sh("v01", 13.3, 14.3, .50, .55, 1.00),
    sh("v01", 7.5, 9.0, .55, .50, 1.15),
    sh("v01", 17.3, 18.9, .55, .55, 1.00),
    sh("v01", 18.9, 20.5, .55, .55, 1.00),
    sh("v01", 8.4, 9.9, .60, .50, 1.60),
    sh("v01", 21.0, 22.5, .55, .50, 1.35),
]
MAIN_DURS = [1.5, 1.5, 1.5, 1.5, 1.4, 1.6, 1.4, 1.4, 1.5, 1.6, 1.6, 1.5, 1.5]
MAIN_SHORT = [0, 1, 2, 9, 10]  # index de plans

PINK = [
    sh("v06", 17.8, 19.4, .55, .50, 1.15, ymax=1140),
    sh("v06", 0.0, 1.2, .50, .48, 1.30),
    sh("v06", 1.2, 2.3, .50, .48, 1.55),
    sh("v06", 2.3, 3.4, .50, .48, 1.30),
    sh("v06", 11.6, 13.2, .50, .50, 1.20, ymax=1140),
    sh("v04", 7.7, 9.3, .50, .62, 1.10),
    sh("v04", 9.3, 10.7, .50, .50, 1.10, fx="pink"),
    sh("v06", 3.5, 5.1, .55, .50, 1.15, ymax=1140),
    sh("v06", 8.0, 9.6, .55, .50, 1.15, ymax=1140),
    sh("v06", 14.0, 15.9, .55, .50, 1.15, ymax=1140),
    sh("v06", 18.5, 20.0, .55, .50, 1.40, ymax=1140),
    sh("v06", 16.0, 17.5, .55, .50, 1.15, ymax=1140),
]
GTA_DURS = [1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.9, 1.5, 1.7]
GTA_SHORT = [0, 1, 2, 3, 9]


def hsv_key_graph(fx):
    """Remplace la couleur doree des lettres par blanc / rose (masque HSV)."""
    # gold: teinte ~ 40deg, saturation haute
    if fx == "white":
        recol = "hue=s=0,curves=all='0/0 0.30/0.55 0.60/0.93 1/1'"
    elif fx == "pink":
        recol = "hue=h=-80:s=1.25,eq=saturation=1.2"
    else:
        raise ValueError(fx)
    return recol


# ---------------------------------------------------------------- clips
def clip_path(variant, fmt, idx, spec, out_d):
    return f"{CLIPS}/{variant}_{fmt}_{idx:02d}_{hashlib.md5(repr((spec, out_d)).encode()).hexdigest()[:8]}.mp4"


def crop_box(spec, fmt):
    W, H = FORMATS[fmt]
    z = spec["z"]
    w = SW / z
    h = w * H / W
    if h > SH:  # ne pas depasser
        h = SH / 1.0
        w = h * W / H
    ymax = spec["ymax"]
    if h > ymax:
        h = ymax
        w = h * W / H
    x = spec["cx"] * SW - w / 2
    y = spec["cy"] * SH - h / 2
    x = max(0, min(x, SW - w))
    y = max(0, min(y, ymax - h))
    return int(w) // 2 * 2, int(h) // 2 * 2, int(x), int(y)


def render_clip(variant, fmt, idx, spec, out_d, grade):
    path = clip_path(variant, fmt, idx, spec, out_d)
    if os.path.exists(path):
        return path
    W, H = FORMATS[fmt]
    w, h, x, y = crop_box(spec, fmt)
    t0, t1 = spec["t0"], spec["t1"]
    speed = out_d / (t1 - t0)
    src = f"{SRC}/{spec['src']}.mp4"
    fx = spec["fx"] or variant_fx(variant)
    if fx in ("white", "pink") and spec["src"] == "v04":
        src, off = recolored_src(fx, t0, t1)
        t0, t1 = t0 - off, t1 - off
    chain = f"[0:v]setpts=(PTS-STARTPTS)*{speed:.4f},fps=30"
    g = f"{chain}[o]"
    last = "[o]"
    post = f"crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5:3:3:0.0"
    if grade == "gta":
        post += (",colorbalance=rs=-0.05:gs=-0.08:bs=0.14:rm=0.06:gm=-0.05:bm=0.10:rh=0.08:bh=0.05,"
                 "eq=saturation=1.25:contrast=1.08")
    post += ",setsar=1,format=yuv420p"
    g = f"{g};{last}{post}[v]"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", src,
         "-filter_complex", g, "-map", "[v]", "-t", f"{out_d}", "-r", "30",
         "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-an", path])
    return path


RC_SEGS = {"white": [("A", 0.0, 4.7, True), ("R", 4.7, 17.2, False)],
           "pink": [("P", 9.2, 10.8, False)]}


def recolored_src(fx, t0, t1):
    for name, a, b, loose in RC_SEGS[fx]:
        if t0 >= a - 1e-6 and t1 <= b + 1e-6:
            path = f"{WORK}/rc_{fx}_{name}.mp4"
            if not os.path.exists(path):
                print("recolor", fx, name, flush=True)
                RC.recolor_video(f"{SRC}/v04.mp4", a, b, fx, path, loose)
            return path, a
    raise SystemExit(f"pas de segment recolore pour {fx} {t0}-{t1}")


def variant_fx(variant):
    return "white" if variant.startswith("blanc") else None


# ---------------------------------------------------------------- carton final
def font(path, size):
    return ImageFont.truetype(path, int(size))


def make_card(fmt, path):
    W, H = FORMATS[fmt]
    s = {"9x16": 1.0, "4x5": 0.92, "1x1": 0.74}[fmt]
    cy = {"9x16": 800, "4x5": 590, "1x1": 470}[fmt]
    im = Image.new("RGB", (W, H), (11, 11, 11))
    d = ImageDraw.Draw(im)
    logo = Image.open(f"{S}/assets/logo_white.png").convert("RGBA")
    lw = int(840 * s)
    lh = int(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    f1, f2, f3 = font(INTER_BLACK, 84 * s), font(INTER_BLACK, 98 * s), font(INTER, 64 * s)
    gap = int(80 * s)
    h1, h2, h3 = int(84 * s), int(98 * s), int(64 * s)
    total = lh + gap + h1 + int(14 * s) + h2 + gap + h3
    y = cy - total // 2
    im.paste(logo, ((W - lw) // 2, y), logo)
    y += lh + gap

    def centered(text, f, yy, fill):
        bb = d.textbbox((0, 0), text, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], yy - bb[1]), text, font=f, fill=fill)
    centered("2 ACHETÉS", f1, y, (255, 255, 255))
    y += h1 + int(14 * s)
    centered("= 2 OFFERTS", f2, y, ORANGE)
    y += h2 + gap
    centered("gommeo.com", f3, y, (255, 255, 255))
    im.save(path)


def card_clip(fmt, d=2.5):
    png = f"{WORK}/card_{fmt}.png"
    mp4 = f"{CLIPS}/card_{fmt}_{d}.mp4"
    if not os.path.exists(mp4):
        make_card(fmt, png)
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-t", f"{d}", "-i", png,
             "-vf", "fade=t=in:st=0:d=0.2,format=yuv420p", "-c:v", "libx264", "-crf", "15", "-r", "30", mp4])
    return mp4


# ---------------------------------------------------------------- sous-titres / textes (ASS)
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def wrap2(text, maxc):
    if len(text) <= maxc:
        return text
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        sc = abs(len(a) - len(b))
        if len(a) <= maxc and len(b) <= maxc and (best is None or sc < best[0]):
            best = (sc, a, b)
    if best is None:
        i = len(words) // 2
        return " ".join(words[:i]) + "\\N" + " ".join(words[i:])
    return best[1] + "\\N" + best[2]


def chunk_sub(a, b, text, maxc):
    """Decoupe un texte trop long (> 2 lignes) en blocs successifs, temps au prorata."""
    import re
    if len(text) <= 2 * maxc:
        return [(a, b, text)]
    parts = re.split(r"(?<=[…\.,]) ", text)
    chunks, cur = [], ""
    for pt in parts:
        cand = (cur + " " + pt).strip()
        if cur and len(cand) > 2 * maxc:
            chunks.append(cur); cur = pt
        else:
            cur = cand
    if cur:
        chunks.append(cur)
    tot = sum(len(c) for c in chunks)
    out, t = [], a
    for c in chunks:
        d = (b - a) * len(c) / tot
        out.append((t, t + d, c)); t += d
    return out


def make_ass(fmt, subs, texts, path):
    """subs: [(start,end,text)]; texts: [(start,end,style,text,pos)]"""
    W, H = FORMATS[fmt]
    p = {
        "9x16": dict(sub=66, mv=440, ml=60, mr=120, hook=104, hy=290, maxc=21, hud=120),
        "4x5": dict(sub=56, mv=115, ml=60, mr=60, hook=90, hy=150, maxc=24, hud=104),
        "1x1": dict(sub=50, mv=90, ml=60, mr=60, hook=76, hy=100, maxc=26, hud=88),
    }[fmt]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter,{p['sub']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,{max(4, p['sub'] // 9)},0,2,{p['ml']},{p['mr']},{p['mv']},1
Style: Hook,Inter Black,{p['hook']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,{max(6, p['hook'] // 11)},0,8,{p['ml']},{p['mr']},{p['hy']},1
Style: Hud,Inter Black,{p['hud']},&H00FFB000,&H00FFB000,&H00000000,&H00000000,-1,1,0,0,100,100,2,0,1,{max(6, p['hud'] // 11)},0,5,{p['ml']},{p['mr']},0,1
Style: Hud2,Inter Black,{int(p['hud'] * 0.78)},&H00FF5CF0,&H00FF5CF0,&H00000000,&H00000000,-1,1,0,0,100,100,2,0,1,{max(5, p['hud'] // 14)},0,5,{p['ml']},{p['mr']},0,1
Style: Tag,Inter Black,{int(p['hook'] * 0.9)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,{max(6, p['hook'] // 11)},0,5,{p['ml']},{p['mr']},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for a, b, t in subs:
        for a2, b2, t2 in chunk_sub(a, b, t, p['maxc']):
            ev.append(f"Dialogue: 0,{ts(a2)},{ts(b2)},Sub,,0,0,0,,{wrap2(t2, p['maxc'])}")
    for a, b, style, t, pos in texts:
        extra = ""
        if pos is not None:  # pos = (fx, fy) fraction de l'ecran
            extra = f"{{\\pos({int(pos[0] * W)},{int(pos[1] * H)})}}"
        fade = "{\\fad(120,150)}"
        ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},{style},,0,0,0,,{fade}{extra}{t}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


# ---------------------------------------------------------------- audio
def make_audio(name, vo_events, sfx_events, total, path):
    """vo_events [(line,start)], sfx_events [(file,start,vol,maxdur,fadeout)]"""
    cmd = ["ffmpeg", "-v", "error", "-y"]
    inputs = []
    for line, st in vo_events:
        inputs.append(f"{VO}/{line}.mp3")
    for f, st, vol, md, fo in sfx_events:
        inputs.append(f"{SFX}/{f}.mp3")
    for i in inputs:
        cmd += ["-i", i]
    fc = []
    vo_labels, sfx_labels = [], []
    n = 0
    for line, st in vo_events:
        fc.append(f"[{n}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.0,adelay={int(st * 1000)}|{int(st * 1000)}[v{n}]")
        vo_labels.append(f"[v{n}]")
        n += 1
    for f, st, vol, md, fo in sfx_events:
        d = min(md, dur(f"{SFX}/{f}.mp3"))
        fc.append(f"[{n}:a]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:{d},"
                  f"afade=t=in:st=0:d=0.08,afade=t=out:st={max(0, d - fo):.2f}:d={fo},volume={vol},"
                  f"adelay={int(st * 1000)}|{int(st * 1000)}[s{n}]")
        sfx_labels.append(f"[s{n}]")
        n += 1
    fc.append("".join(vo_labels) + f"amix=inputs={len(vo_labels)}:normalize=0,apad=whole_dur={total}[vom]")
    fc.append("".join(sfx_labels) + f"amix=inputs={len(sfx_labels)}:normalize=0,apad=whole_dur={total}[sfm]")
    fc.append("[vom]asplit[vo1][vo2]")
    fc.append("[sfm][vo1]sidechaincompress=threshold=0.015:ratio=8:attack=15:release=350:makeup=1[sfd]")
    fc.append("[sfd][vo2]amix=inputs=2:normalize=0,alimiter=limit=0.95,"
              f"loudnorm=I=-14:TP=-1.5:LRA=9,atrim=0:{total},aformat=sample_rates=44100:channel_layouts=stereo[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[a]", "-t", f"{total}", "-c:a", "pcm_s16le", path]
    run(cmd)


# ---------------------------------------------------------------- definitions des videos
SUBTXT = {
    "L1": "Trois coups de marqueur… et la lettre est faite.",
    "L2": "Peinture à l'huile, pointe à valve.",
    "L3": "Un coup de mousse, un coup de jet… elle bouge pas.",
    "L4": "Et ta caisse change complètement.",
    "L5": "Douze couleurs, à toi de choisir.",
    "L6": "Lettrix, c'est sur gommeo.com.",
    "G1": "En attendant GTA 6, j'ai déjà custom ma caisse.",
    "G2": "Trois coups de marqueur… peinture à l'huile, pointe à valve.",
    "G3": "Un coup de jet, elle bouge pas.",
    "G4": "Douze couleurs. À toi de jouer.",
}


def main_def(short):
    if not short:
        durs = MAIN_DURS
        vo = [("L1", .2), ("L2", 4.3), ("L3", 7.2), ("L4", 11.9), ("L5", 16.6), ("L6", 19.6)]
        sfx = [("click", .1, .9, 1.0, .2), ("scrape", .4, .8, 4.0, .4), ("click", 3.05, .8, 1.0, .2),
               ("cloth", 4.5, .8, 3.0, .4), ("foam", 7.4, .8, 1.7, .3), ("jet", 8.9, .8, 3.0, .5),
               ("engine", 11.8, .75, 5.0, .6), ("tire", 13.6, .8, 6.0, .7)]
        texts = [(0.0, 2.3, "Hook", "3 COUPS.\\NC'EST FAIT.", None),
                 (16.5, 19.4, "Tag", "12 COULEURS", (0.5, 0.20))]
    else:
        durs = [MAIN_DURS[i] for i in MAIN_SHORT]
        vo = [("L1", .2), ("L5", 5.0), ("L6", 7.8)]
        sfx = [("click", .1, .9, 1.0, .2), ("scrape", .4, .8, 4.0, .4), ("click", 3.05, .8, 1.0, .2),
               ("engine", 4.4, .75, 3.4, .5), ("tire", 4.5, .8, 3.2, .6)]
        texts = [(0.0, 2.3, "Hook", "3 COUPS.\\NC'EST FAIT.", None),
                 (4.9, 7.6, "Tag", "12 COULEURS", (0.5, 0.20))]
    return durs, vo, sfx, texts


def gta_def(short):
    if not short:
        durs = GTA_DURS
        vo = [("G1", .3), ("G2", 3.9), ("G3", 7.9), ("G4", 16.5), ("L6", 19.6)]
        sfx = [("city", 0.0, .5, 8.0, .6), ("click", .1, .9, 1.0, .2), ("click", 1.7, .8, 1.0, .2),
               ("scrape", 1.9, .8, 4.0, .4), ("chime", 4.85, .9, 1.2, .3), ("chime", 5.5, .7, 1.2, .3),
               ("cloth", 6.4, .8, 1.6, .3), ("foam", 8.0, .8, 1.6, .3), ("jet", 9.5, .8, 3.0, .5),
               ("engine", 11.2, .75, 5.0, .6), ("tire", 13.5, .8, 6.0, .7), ("city", 11.0, .4, 8.0, .8)]
        texts = [(0.0, 2.6, "Hook", "EN ATTENDANT\\NGTA 6…", None),
                 (4.8, 6.4, "Hud", "MISSION RÉUSSIE", (0.5, 0.42)),
                 (5.4, 6.4, "Hud2", "+1 STYLE", (0.5, 0.50))]
    else:
        durs = [GTA_DURS[i] for i in GTA_SHORT]
        vo = [("G1", .3), ("G4", 6.0), ("L6", 8.4)]
        sfx = [("city", 0.0, .5, 8.0, .6), ("click", .1, .9, 1.0, .2), ("click", 1.7, .8, 1.0, .2),
               ("scrape", 1.9, .8, 4.0, .4), ("chime", 4.85, .9, 1.2, .3), ("chime", 5.5, .7, 1.2, .3),
               ("engine", 6.4, .75, 2.0, .5), ("tire", 6.5, .8, 2.0, .6)]
        texts = [(0.0, 2.6, "Hook", "EN ATTENDANT\\NGTA 6…", None),
                 (4.8, 6.4, "Hud", "MISSION RÉUSSIE", (0.5, 0.42)),
                 (5.4, 6.4, "Hud2", "+1 STYLE", (0.5, 0.50))]
    return durs, vo, sfx, texts


def build(angle, color, fmt, short, preview=False):
    variant = f"{angle}_{color}"
    if angle == "neon":
        table = {"dore": GOLD, "blanc": GOLD, "orange": ORANGE_T}[color]
        idxs = MAIN_SHORT if short else list(range(len(table)))
        durs, vo, sfx, texts = main_def(short)
        grade = None
        vkey = {"dore": "dore", "blanc": "blanc", "orange": "orange"}[color]
    else:
        table = PINK
        idxs = GTA_SHORT if short else list(range(len(table)))
        durs, vo, sfx, texts = gta_def(short)
        grade = "gta"
        vkey = "rose"
        variant = "gta6_rose"
    vkey2 = {"dore": "dore", "blanc": "blanc", "orange": "orange", "rose": "rose"}[vkey]
    # le fx de couleur "blanc" passe par variant ; gta passe par spec['fx']
    vn = vkey2 if angle == "neon" else "gta6_rose"
    clips = []
    for k, (i, d) in enumerate(zip(idxs, durs)):
        clips.append(render_clip(vn if angle == "neon" else "gta", fmt, i, table[i], d, grade))
    card = card_clip(fmt, 2.5)
    total = round(sum(durs) + 2.5, 2)
    lst = f"{WORK}/{variant}_{fmt}_{'s' if short else 'm'}.txt"
    open(lst, "w").write("".join(f"file '{c}'\nfile '{card}'\n" if False else f"file '{c}'\n" for c in clips) + f"file '{card}'\n")
    base = f"{WORK}/{variant}_{fmt}_{'s' if short else 'm'}_base.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])
    # sous-titres
    subs = []
    for line, st in vo:
        d = dur(f"{VO}/{line}.mp3")
        subs.append((st, st + d + 0.15, SUBTXT[line]))
    ass = f"{WORK}/{variant}_{fmt}_{'s' if short else 'm'}.ass"
    make_ass(fmt, subs, texts, ass)
    wav = f"{WORK}/{variant}_{'s' if short else 'm'}.wav"
    if not os.path.exists(wav):
        make_audio(variant, vo, sfx, total, wav)
    n = round(total)
    fname = f"GOMMEO_{angle if angle=='neon' else 'GTA6'}_{color}_{fmt}_{n}s.mp4"
    out = f"{OUT}/{fname}" if not preview else f"{WORK}/prev_{fname}"
    run(["ffmpeg", "-v", "error", "-y", "-i", base, "-i", wav,
         "-vf", f"subtitles={ass}:fontsdir=/usr/share/fonts/opentype/inter,fps=30,format=yuv420p",
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M",
         "-preset", "medium", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", "-shortest", out])
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "one":
        angle, color, fmt, short = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] == "s"
        print(build(angle, color, fmt, short, preview=len(sys.argv) > 6))
