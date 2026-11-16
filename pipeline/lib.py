import os, json, hashlib, base64, subprocess, re, math, sys
import numpy as np
import soundfile as sf
from scipy import signal
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'cache'); os.makedirs(CACHE, exist_ok=True)
SR = 48000
FPS = 30
W, H = 1080, 1920
FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
FONT_BLACK = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
YELLOW = (255, 221, 51)
KEYWORDS = {'sushi', 'sushis', 'chaussettes', 'cinq', 'paires', 'offert', 'noël'}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


# ---------------------------------------------------------------- TTS
def tts(voice, text, seed, prev=None, nxt=None, speed=1.0, stability=0.42, style=0.3, model='eleven_multilingual_v2'):
    body = {'text': text, 'model_id': model, 'seed': seed,
            'voice_settings': {'stability': stability, 'similarity_boost': 0.8, 'style': style,
                               'use_speaker_boost': True, 'speed': speed}}
    if model == 'eleven_multilingual_v2':
        if prev: body['previous_text'] = prev
        if nxt: body['next_text'] = nxt
    key = hashlib.sha1(json.dumps([voice, body], sort_keys=True).encode()).hexdigest()[:16]
    jf = os.path.join(CACHE, key + '.json'); wf = os.path.join(CACHE, key + '.wav')
    if not os.path.exists(wf):
        bf = os.path.join(CACHE, key + '.req'); open(bf, 'w').write(json.dumps(body))
        r = subprocess.run(['curl', '-sS', '-m', '120', '-X', 'POST',
                            f'https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128',
                            '-H', 'Content-Type: application/json', '--data-binary', '@' + bf], capture_output=True)
        d = json.loads(r.stdout)
        if 'audio_base64' not in d:
            raise RuntimeError(str(d)[:400])
        mp3 = os.path.join(CACHE, key + '.mp3'); open(mp3, 'wb').write(base64.b64decode(d['audio_base64']))
        run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR), wf])
        json.dump(d['alignment'], open(jf, 'w'))
    return wf, json.load(open(jf))


def tokens(text):
    out = []
    for t in text.split():
        if out and re.fullmatch(r'[\W_]+', t):
            out[-1] += ' ' + t
        else:
            out.append(t)
    return out


def align_words(al):
    ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    words = []; cur = None; br = False
    for c, s, e in zip(ch, st, en):
        if c == '[': br = True
        if br:
            if c == ']': br = False
            continue
        if c.isspace():
            if cur: words.append(cur); cur = None
        else:
            if cur is None: cur = [c, s, e]
            else: cur[0] += c; cur[2] = e
    if cur: words.append(cur)
    out = []
    for w in words:
        if out and re.fullmatch(r'[\W_]+', w[0]):
            out[-1][2] = w[2]
        else:
            out.append(list(w))
    return out


def proc_voice(wf, t0, t1, tempo, tag):
    out = os.path.join(CACHE, f'{os.path.basename(wf)[:-4]}_{tag}.wav')
    af = 'highpass=f=80,deesser=i=0.35,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=1'
    if tempo > 1.001: af += f',atempo={tempo:.4f}'
    run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-to', f'{t1:.3f}', '-i', wf, '-af', af, '-ar', str(SR), out])
    x, _ = sf.read(out); x = x.astype(np.float64)
    rms = np.sqrt(np.mean(x[np.abs(x) > 0.003] ** 2)) if np.any(np.abs(x) > 0.003) else 1e-3
    x *= 10 ** (-21 / 20) / rms
    n = int(0.006 * SR); x[:n] *= np.linspace(0, 1, n); m = int(0.04 * SR); x[-m:] *= np.linspace(1, 0, m)
    return x


# ---------------------------------------------------------------- SFX
_rng = np.random.default_rng(7)


def _svf_bp(x, fc, q=2.0):
    low = band = 0.0; out = np.empty_like(x)
    for i in range(len(x)):
        f = 2 * math.sin(math.pi * min(fc[i], SR / 6.5) / SR)
        low += f * band; high = x[i] - low - band / q; band += f * high; out[i] = band
    return out


def _norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def sfx(kind, dur=None, var=0):
    r = np.random.default_rng(100 + var)
    if kind == 'whoosh':
        d = dur or 0.38; n = int(d * SR); t = np.linspace(0, 1, n)
        fc = (350 + 150 * var % 300) + 2600 * np.sin(np.pi * t) ** 2
        y = _svf_bp(r.standard_normal(n), fc, 1.4) * np.sin(np.pi * t) ** 1.6
    elif kind == 'pop':
        n = int(0.09 * SR); t = np.arange(n) / SR
        f = (760 + 60 * (var % 3)) * np.exp(-t * 16) + 240
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 55)
    elif kind == 'tick':
        n = int(0.03 * SR); t = np.arange(n) / SR
        y = np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 260)
    elif kind == 'snap':
        n = int(0.07 * SR); t = np.arange(n) / SR
        b, a = signal.butter(2, 1800 / (SR / 2), 'high')
        y = signal.lfilter(b, a, r.standard_normal(n)) * np.exp(-t * 130) + 0.5 * np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 90)
    elif kind == 'riser':
        d = dur or 0.8; n = int(d * SR); t = np.linspace(0, 1, n)
        fc = 300 * (16 ** t)
        y = _svf_bp(r.standard_normal(n), fc, 3.0) * 0.7
        f = 220 * (5 ** t); y += 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR)
        y *= t ** 2.2; k = int(0.015 * SR); y[-k:] *= np.linspace(1, 0, k)
    elif kind == 'ding':
        n = int(1.1 * SR); t = np.arange(n) / SR; f0 = 1568
        y = sum(a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-t * dcy) for m, a, dcy in [(1, 1, 4.5), (2.0, .35, 7), (2.76, .3, 9), (5.4, .12, 14)])
        k = int(0.003 * SR); y[:k] *= np.linspace(0, 1, k)
    elif kind == 'sparkle':
        n = int(0.9 * SR); y = np.zeros(n); t = np.arange(int(0.35 * SR)) / SR
        for i, f in enumerate([2637, 3136, 3951, 5274, 4186, 6272]):
            s = int(i * 0.07 * SR); p = np.sin(2 * np.pi * f * t) * np.exp(-t * 14) * (0.9 ** i)
            y[s:s + len(p)] += p[:n - s]
    elif kind == 'impact':
        n = int(0.5 * SR); t = np.arange(n) / SR
        f = 95 * np.exp(-t * 7) + 38
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
        b, a = signal.butter(2, 900 / (SR / 2), 'low')
        y += 0.5 * signal.lfilter(b, a, r.standard_normal(n)) * np.exp(-t * 40)
    elif kind == 'boing':
        n = int(0.35 * SR); t = np.arange(n) / SR
        f = 260 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 6) + 180 * t
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    else:
        raise ValueError(kind)
    return _norm(y)


SFX_DB = {'whoosh': -25, 'pop': -22, 'tick': -31, 'snap': -22, 'riser': -20, 'ding': -19, 'sparkle': -22, 'impact': -17, 'boing': -21}
_sfx_cache = {}


def get_sfx(kind, dur=None, var=0):
    k = (kind, dur, var % 4)
    if k not in _sfx_cache: _sfx_cache[k] = sfx(kind, dur, var % 4)
    return _sfx_cache[k]


def add(buf, x, t, gain_db=0.0):
    s = int(round(t * SR))
    if s < 0: x = x[-s:]; s = 0
    if s >= len(buf): return
    x = x[:len(buf) - s]
    buf[s:s + len(x)] += x * 10 ** (gain_db / 20)


# ---------------------------------------------------------------- text rendering
def is_emoji(c):
    o = ord(c); return o >= 0x1F000 or 0x2600 <= o <= 0x27BF


_fonts = {}


def font(sz, path=FONT):
    if (sz, path) not in _fonts: _fonts[(sz, path)] = ImageFont.truetype(path, sz)
    return _fonts[(sz, path)]


_emo = {}


def emoji_img(c, sz):
    if (c, sz) not in _emo:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(im).text((2, 2), c, font=f, embedded_color=True)
        im = im.crop(im.getbbox()); s = sz / 109 * 1.0
        _emo[(c, sz)] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return _emo[(c, sz)]


def word_w(w, f, sz):
    tot = 0; run_ = ''
    for c in w:
        if is_emoji(c) or c == '️':
            tot += f.getlength(run_); run_ = ''
            if c != '️': tot += emoji_img(c, sz).width
        else: run_ += c
    return tot + f.getlength(run_)


def layout(words, sz, maxw):
    f = font(sz); sp = f.getlength(' '); lines = [[]]; cur = 0
    for w in words:
        brk = w[0].startswith('\x01')
        if brk: w = (w[0][1:],) + tuple(w[1:])
        ww = word_w(w[0], f, sz)
        if lines[-1] and (brk or cur + sp + ww > maxw):
            lines.append([]); cur = 0
        cur += (sp if lines[-1] else 0) + ww; lines[-1].append((w, ww))
    # balance two lines
    if len(lines) == 2 and not any(w[0].startswith('\x01') for w in words):
        while len(lines[0]) > 1:
            w0 = sum(x[1] for x in lines[0]) + sp * (len(lines[0]) - 1); w1 = sum(x[1] for x in lines[1]) + sp * (len(lines[1]) - 1)
            mv = lines[0][-1][1] + sp
            if w1 + mv <= maxw and abs((w0 - mv) - (w1 + mv)) < abs(w0 - w1):
                lines[1].insert(0, lines[0].pop())
            else: break
    return lines, sp


def render_label(words, sz=62, maxw=900, style='dark', max_lines=2, rect=None, pad=None):
    """words: list of (text, highlighted). returns RGBA image."""
    while True:
        lines, sp = layout(words, sz, maxw)
        if len(lines) <= max_lines or sz <= 30: break
        sz -= 3
    f = font(sz); lh = int(sz * 1.22)
    tw = max(sum(x[1] for x in l) + sp * (len(l) - 1) for l in lines); th = lh * len(lines)
    px, py = pad or (int(sz * 0.45), int(sz * 0.3))
    stroke = 0
    if style in ('outline', 'digit'): stroke = max(4, sz // 9); px = py = stroke + 8
    bw, bh = (int(tw + 2 * px), int(th + 2 * py)) if rect is None else rect
    sh = 10
    im = Image.new('RGBA', (bw + 2 * sh, bh + 2 * sh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bg = {'dark': (12, 12, 12, 225), 'solid': (12, 12, 12, 255), 'white': (255, 255, 255, 255), 'offer': (255, 214, 0, 255),
          'badge': (112, 98, 94, 255), 'cream': (248, 237, 204, 255), 'orange': (240, 130, 40, 255)}.get(style)
    fg = {'dark': (255, 255, 255), 'solid': (255, 255, 255), 'white': (15, 15, 15), 'offer': (15, 15, 15), 'badge': (255, 255, 255),
          'outline': (255, 255, 255), 'digit': YELLOW, 'cream': (15, 15, 15), 'orange': (255, 255, 255)}[style]
    hl = {'white': (225, 45, 45), 'offer': (200, 20, 20), 'cream': (225, 45, 45)}.get(style, YELLOW)
    if bg:
        if style in ('white', 'offer'):
            d.rounded_rectangle((sh + 3, sh + 5, sh + bw + 3, sh + bh + 5), radius=int(min(bh, 160) * 0.2), fill=(0, 0, 0, 70))
        d.rounded_rectangle((sh, sh, sh + bw, sh + bh), radius=int(min(bh, 160) * 0.2), fill=bg)
    y = sh + (bh - th) / 2
    for l in lines:
        lw = sum(x[1] for x in l) + sp * (len(l) - 1); x = sh + (bw - lw) / 2
        for (w, ww) in l:
            col = hl if w[1] else fg; run_ = ''; xx = x
            def flush(run_, xx):
                if run_:
                    d.text((xx, y + (lh - sz) / 2 - sz * 0.08), run_, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
                return xx + f.getlength(run_)
            for c in w[0]:
                if is_emoji(c):
                    xx = flush(run_, xx); run_ = ''
                    e = emoji_img(c, sz); im.alpha_composite(e, (int(xx), int(y + (lh - e.height) / 2))); xx += e.width
                elif c != '️': run_ += c
            flush(run_, xx); x += ww + sp
        y += lh
    return im


def label(text, hl=(), **kw):
    ws = [(w.replace('\u00a0', ' '), w.strip('.,!?:…«»"\u00a0\x01 ').lower() in hl) for w in tokens(text.replace('\n', ' \x01'))]
    return render_label(ws, **kw)


# ---------------------------------------------------------------- subtitles
def norm_word(w):
    return re.sub(r"[^\wàâäéèêëîïôöùûüç'-]", '', w.lower()).split("'")[-1]


def chunk_words(words, maxc=30):
    """words: [text,t0,t1] -> chunks"""
    chunks = []; cur = []
    def L(c): return sum(len(w[0]) for w in c) + len(c) - 1
    for i, w in enumerate(words):
        cur.append(w); txt = w[0]
        nxt = words[i + 1] if i + 1 < len(words) else None
        end_sent = bool(re.search(r'[.?!…]$', txt.replace(' ', '').rstrip('»"')))
        soft = bool(re.search(r'[,:;]$', txt.replace(' ', '')))
        if nxt is None or end_sent or (soft and L(cur) >= 12) or L(cur) + 1 + len(nxt[0]) > maxc:
            chunks.append(cur); cur = []
    # merge tiny orphan chunk (single short word) with previous if same sentence
    out = []
    for c in chunks:
        if out and L(c) <= 6 and L(out[-1]) + L(c) < maxc + 8 and not re.search(r'[.?!…]$', out[-1][-1][0].replace(' ', '')):
            out[-1] = out[-1] + c
        else: out.append(c)
    return out


def srt_time(t):
    ms = int(round(t * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'
