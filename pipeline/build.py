import sys, os, json, subprocess, re
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import ndimage, signal
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from cfg import V

OUT = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
WORK = os.path.join(ROOT, 'work'); os.makedirs(WORK, exist_ok=True)


VAL = '/home/user/mes-videos-amine-ia/Voix_FR_a_valider'


def toks(s):
    out = []; pend = ''
    for t in s.split():
        if not re.search(r'\w', t):
            if out: out[-1] += '\u00a0' + t
            else: pend += t + '\u00a0'
        else: out.append(pend + t); pend = ''
    return out


def take_voice(c, log):
    import voix
    lines = [voix.strip_tags(l) for l in voix.S[c['take_vid']][1]]
    slots = c['slots']; assert len(slots) == len(lines), (len(slots), len(lines))
    mp3 = os.path.join(VAL, c['take'])
    fa = os.path.join(WORK, c['take'] + '.fa.json')
    if not os.path.exists(fa):
        txt = os.path.join(WORK, c['take'] + '.txt'); open(txt, 'w').write(' '.join(lines))
        r = subprocess.run(['curl', '-sS', '-m', '300', '-X', 'POST', 'https://api.elevenlabs.io/v1/forced-alignment', '-F', f'file=@{mp3}', '-F', f'text=<{txt}'], capture_output=True, text=True)
        d = json.loads(r.stdout); assert 'words' in d, r.stdout[:300]; json.dump(d, open(fa, 'w'))
    fw = [w for w in json.load(open(fa))['words'] if w['text'].strip()]
    W_ = []; pend = None
    for w in fw:
        t = w['text']
        if not re.search(r'\w', t):
            if W_: W_[-1][0] += '\u00a0' + t
            else: pend = t
        else:
            W_.append([(pend + '\u00a0' if pend else '') + t, w['start'], w['end']]); pend = None
    wav = os.path.join(WORK, c['take'] + '.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', str(SR), wav])
    audio, _ = sf.read(wav)
    k = 0; parts = []
    for l in lines:
        n = len(toks(l)); parts.append((toks(l), W_[k:k + n])); k += n
    assert k == len(W_), (k, len(W_))
    placed = []; prev_end = -1.0; mt = c.get('max_tempo', 1.05)
    for i, ((s, e), (dt, ws)) in enumerate(zip(slots, parts)):
        a = ws[0][1] - 0.12
        if i: a = max(a, (parts[i - 1][1][-1][2] + ws[0][1]) / 2)
        b = ws[-1][2] + 0.2
        if i + 1 < len(parts): b = min(b, max(ws[-1][2] + 0.05, (ws[-1][2] + parts[i + 1][1][0][1]) / 2))
        a = max(0, a); d = b - a; slot = e - s
        tempo = float(np.clip(d / max(slot, 0.1), 1.0, mt))
        start = max(s - 0.1, prev_end + 0.04); end = start + d / tempo
        seg = os.path.join(WORK, f"{c['take']}_{i:02d}.wav")
        af = f'atempo={tempo:.4f}' if tempo > 1.001 else 'anull'
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-i', wav, '-af', af, seg])
        x, _ = sf.read(seg); x = x.astype(np.float64)
        n1 = int(0.008 * SR); x[:n1] *= np.linspace(0, 1, n1); n2 = int(0.03 * SR); x[-n2:] *= np.linspace(1, 0, n2)
        words = [[t, start + (w[1] - a) / tempo, start + (w[2] - a) / tempo] for t, w in zip(dt, ws)]
        placed.append(dict(t=start, x=x, words=words, end=end, i=i))
        over = end - e
        log.append(f'  ligne{i+1:02d} slot {s:5.2f}-{e:5.2f} voix {d:4.2f}s tempo {tempo:4.2f} -> {start:5.2f}-{end:5.2f} {"DEPASSE %+.2f" % over if over > 0.15 else "ok"} | {" ".join(dt)[:55]}')
        prev_end = end
    return placed


def gen_voice(c, log):
    if c.get('take'): return take_voice(c, log)
    segs = c['segs']; placed = []; prev_end = -1.0
    vs = c.get('vs', {})
    one = None
    if c.get('oneshot'):
        full = ' '.join(c['oneshot'] + ' ' + (x[3] if len(x) > 3 else x[2]) for x in segs)
        best = None
        for seed in [11, 23, 37][:c.get('takes', 2)]:
            wf, al = tts(c['voice'], full, seed, stability=vs.get('stability', 0.5), model=c['model'])
            ws = align_words(al); k = 0; parts = []; worst = 0
            for x in segs:
                n = len(tokens(x[2])); p = ws[k:k + n]; k += n; parts.append(p)
            for j, (x, p) in enumerate(zip(segs, parts)):
                worst = max(worst, (p[-1][2] - p[0][1] + 0.15) / (x[1] - x[0]))
            if k == len(ws) and (best is None or worst < best[0]): best = (worst, wf, parts, seed)
        one = best; log.append(f'  oneshot seed {best[3]} worst ratio {best[0]:.2f}')
    for i, sg in enumerate(segs):
        s, e, disp = sg[0], sg[1], sg[2]; ttx = sg[3] if len(sg) > 3 else disp
        prev = ' '.join((x[3] if len(x) > 3 else x[2]) for x in segs[max(0, i - 2):i]) or None
        nxt = (segs[i + 1][3] if len(segs[i + 1]) > 3 else segs[i + 1][2]) if i + 1 < len(segs) else None
        slot = e - s; cands = []
        tries = [(11, 1.0), (23, 1.0), (37, 1.0)][:c.get('takes', 2)]
        for k, (seed, sp) in enumerate(tries if not one else []):
            if k >= c.get('takes', 2) and cands and min(x[0] for x in cands) <= 1.1: break
            wf, al = tts(c['voice'], ttx, seed, prev, nxt, speed=sp * vs.get('speed', 1.0), stability=vs.get('stability', 0.42), style=vs.get('style', 0.3), model=c.get('model', 'eleven_multilingual_v2'))
            ws = align_words(al)
            a = max(0, ws[0][1] - 0.03); b = ws[-1][2] + 0.14
            d = b - a
            cands.append((d / slot, k, wf, ws, a, b, d))
        if one:
            p = one[2][i]; a = max(0, p[0][1] - 0.03); b = p[-1][2] + 0.14
            if i + 1 < len(segs): b = min(b, one[2][i + 1][0][1] - 0.02)
            cands.append(((b - a) / slot, 0, one[1], p, a, b, b - a))
        fit = [x for x in cands if x[0] <= 1.0]
        # among fitting takes prefer the slowest (least rushed); otherwise the shortest
        best = max(fit, key=lambda x: x[0]) if fit else min(cands, key=lambda x: x[0])
        ratio, k, wf, ws, a, b, d = best
        tempo = float(np.clip(ratio, 1.0, 1.1 / max(1.0, vs.get('speed', 1.0))))
        start = max(s, prev_end + 0.05); d2 = d / tempo; end = start + d2
        over = end - e
        x = proc_voice(wf, a, b, tempo, f'{int(a*1000)}_{int(tempo*1000)}')
        dw = tokens(disp)
        if len(dw) != len(ws):
            raise RuntimeError(f'token mismatch {dw} vs {[w[0] for w in ws]}')
        words = [[dw[j], start + (ws[j][1] - a) / tempo, start + (ws[j][2] - a) / tempo] for j in range(len(ws))]
        placed.append(dict(t=start, x=x, words=words, end=end))
        prev_end = end
        log.append(f'  seg{i:02d} slot {s:5.2f}-{e:5.2f} ({slot:4.2f}s) take{k} dur {d:4.2f} tempo {tempo:4.2f} -> {start:5.2f}-{end:5.2f} {"OVER %+.2f" % over if over > 0.03 else "ok"} | {disp[:50]}')
    return placed


def make_map(keep, total):
    if not keep: keep = [(0, total)]
    iv = []; off = 0
    for a, b in keep:
        fa = int(np.ceil(a * FPS - 1e-6)); fb = int(np.ceil(b * FPS - 1e-6))
        iv.append((fa / FPS, fb / FPS, off / FPS)); off += fb - fa
    def f(t, clip_end=False):
        for a, b, o in iv:
            if a - 1e-6 <= t < b - 1e-6: return o + t - a
        return None
    return f, iv, off


def limiter(x, thr=0.82):
    pk = np.max(np.abs(x), axis=1)
    g = np.minimum(1.0, thr / np.maximum(pk, 1e-9))
    n = int(0.004 * SR)
    g = ndimage.minimum_filter1d(g, 2 * n + 1)
    g = ndimage.uniform_filter1d(g, 2 * n + 1)
    return x * g[:, None]


def build(vid, short=None):
    c = V[vid]; log = [f'== {vid} {short["name"] if short else c["name"]}']
    src = os.path.join(ROOT, 'clean', c['src'])
    if not os.path.exists(src): src = os.path.join(ROOT, 'src', c['src']); log.append('  (source NON nettoyée)')
    total = c['dur'] + c.get('tail', 0)
    placed = gen_voice(c, log)
    keep = short.get('keep') if short else None
    if short and short.get('lines'):
        sel = [p for p in placed if p['i'] + 1 in short['lines']]; keep = []
        for j, p in enumerate(sel):
            a = 0.0 if j == 0 else p['t'] - 0.2
            bb = total if j == len(sel) - 1 else p['end'] + 0.3
            if keep and a <= keep[-1][1] + 0.05: keep[-1] = (keep[-1][0], max(keep[-1][1], bb))
            else: keep.append((a, bb))
        if short.get('end_card'): keep[-1] = (keep[-1][0], total)
        log.append('  plans gardés: ' + ', '.join(f'{a:.2f}-{b:.2f}' for a, b in keep))
        placed = sel
    tmap, iv, nfr = make_map(keep, total)
    dur = nfr / FPS; N = int(dur * SR)
    name = f'FR_{c.get("num", vid)}_{short["name"] if short else c["name"]}'
    full_words = [w for p in placed for w in p['words']]
    hl = KEYWORDS | set(c.get('hl', []))

    # ---------- audio
    voice = np.zeros(N); fx = np.zeros(N)
    all_words = []
    for p in placed:
        t = tmap(p['t'])
        if t is None: continue
        add(voice, p['x'], t)
        ws = [[w[0], tmap(w[1]) if tmap(w[1]) is not None else t, t + (w[2] - p['t'])] for w in p['words']]
        all_words.append(ws)
    # subtle room: early reflections
    if c.get('indoor', True):
        er = np.zeros(N)
        for dly, g in [(0.017, 0.07), (0.029, 0.05), (0.043, 0.03)]:
            k = int(dly * SR); er[k:] += voice[:-k] * g
        b, a = signal.butter(1, 3500 / (SR / 2), 'low'); voice = voice + signal.lfilter(b, a, er)
    meter = pyln.Meter(SR)
    voice *= 10 ** ((-16 - meter.integrated_loudness(voice)) / 20)
    vpk = 20 * np.log10(np.max(np.abs(voice)))

    # subtitle chunks
    chunks = []
    for ws in all_words:
        for ch in chunk_words(ws, c.get('maxc', 30)):
            chunks.append(ch)
    subs = []
    for i, ch in enumerate(chunks):
        t0 = ch[0][1]; t1 = ch[-1][2] + 0.3
        if i + 1 < len(chunks): t1 = min(t1, chunks[i + 1][0][1])
        t1 = min(t1, dur)
        if c.get('sub_fill'):
            t1 = chunks[i + 1][0][1] if i + 1 < len(chunks) else dur + 1
            if i == 0: t0 = 0.0
        subs.append((t0, max(t1, t0 + 0.25), ch))

    ev = []  # (kind,t,var/dur)
    for i, ct in enumerate(c.get('cuts', [])):
        t = tmap(ct)
        if t is not None and t > 0.3: ev.append(('whoosh', t - 0.17, None, i))
    for a, b, o in iv[1:]:
        ev.append(('whoosh', o - 0.17, None, 1))
    nhl = 0
    for (t0, t1, ch) in subs:
        ev.append(('tick', t0, None, 0))
        prevhl = False
        for w in ch:
            h = norm_word(w[0]) in hl
            if h and not prevhl: ev.append(('pop', w[1], None, nhl)); nhl += 1
            prevhl = h
    for e in c.get('sfx', []) + (short.get('sfx', []) if short else []):
        kind, t = e[0], e[1]
        if kind.endswith('@'):
            kind = kind[:-1]; occ = [w for ws in all_words for w in ws if w[0].lower() == e[1].lower()]
            if len(occ) <= e[2]:
                if not short: log.append(f'  !! sfx word not found: {e}')
                continue
            d = e[3] if len(e) > 3 else None
            ev.append((kind, occ[e[2]][1] - (d + 0.03 if kind == 'riser' else 0), d, 0)); continue
        tt = tmap(t)
        if tt is not None: ev.append((kind, tt, e[2] if len(e) > 2 else None, 0))
    ovs = list(c.get('overlays', []))
    if short: ovs = [o for o in ovs if not o.get('full_only')] + short.get('overlays', [])
    items = []
    for o in ovs:
        if 'at' in o:
            occ = [w for w in full_words if w[0].lower() == o['at'][0].lower()]
            if len(occ) <= o['at'][1]: log.append(f'  !! overlay anchor not found {o["at"]}'); continue
            ta = occ[o['at'][1]][1] - 0.05; o = dict(o, t0=ta, t1=ta + o['len'])
        pieces = []
        if short and o in short.get('overlays', []): pieces = [(o['t0'], o['t1'], True)]
        else:
            for a, b_, off in iv:
                lo, hi = max(a, o['t0']), min(b_, o['t1'])
                if hi - lo > 1e-3: pieces.append((off + lo - a, off + hi - a, a - 1e-6 <= o['t0'] < b_))
        for t0, t1, first in pieces:
            im = label(o['text'], hl=o.get('hl', ()), sz=o.get('sz', 62), maxw=o.get('maxw', 900), style=o.get('style', 'white'),
                       max_lines=o.get('lines', 3), rect=o.get('rect'), pad=o.get('pad'))
            x = int(o['cx'] - im.width / 2); y = int(o['cy'] - im.height / 2)
            items.append([t0, t1, im, x, y, o.get('anim', 'pop') if first else None])
            if o.get('sound') and first: ev.append((o['sound'], t0, None, 0))
    for (kind, t, d, var) in ev:
        add(fx, get_sfx(kind, d, var), t, SFX_DB[kind] + vpk)
    tone = np.random.default_rng(1).standard_normal(N); b, a = signal.butter(1, 600 / (SR / 2), 'low'); tone = signal.lfilter(b, a, tone)
    tone *= 10 ** (-66 / 20) / np.sqrt(np.mean(tone ** 2))
    # stereo: voice centre, fx slightly widened
    mixL = voice + fx + tone; mixR = voice + np.roll(fx, int(0.0004 * SR)) * 0.92 + tone
    mix = np.stack([mixL, mixR], 1)
    for _ in range(3):
        mix *= 10 ** ((-14.0 - meter.integrated_loudness(mix)) / 20); mix = limiter(mix)
    lufs = meter.integrated_loudness(mix)
    sf.write(os.path.join(WORK, name + '.wav'), mix, SR, subtype='PCM_24')
    sf.write(os.path.join(WORK, name + '_voice.wav'), voice, SR, subtype='PCM_16')
    fxl = meter.integrated_loudness(np.stack([fx, fx], 1) + 1e-7 * np.random.default_rng(2).standard_normal((N, 2))) if np.any(fx) else -99
    log.append(f'  audio: {dur:.2f}s  mix {lufs:.1f} LUFS peak {20*np.log10(np.max(np.abs(mix))):.1f} dBFS | voice -16.0 LUFS (pre-master) fx bus {fxl:.1f} LUFS, {len(ev)} sfx events')

    # ---------- subtitles overlays + srt
    sb = c.get('sub_bottom', 1236); alt = []; n_main = len(items)
    with open(os.path.join(OUT, name + '.srt'), 'w') as f:
        for i, (t0, t1, ch) in enumerate(subs):
            ws = [(w[0].replace(' ', ' '), norm_word(w[0]) in hl) for w in ch]
            im = render_label(ws, sz=c.get('sub_sz', 60), maxw=c.get('sub_maxw', 880), style=c.get('sub_style', 'dark'), max_lines=2, rect=c.get('sub_rect'))
            y = sb - im.height + 10 if not c.get('sub_cy') else int(c['sub_cy'] - im.height / 2)
            items.append([t0, t1, im, int(W / 2 - im.width / 2), y, 'pop'])
            s45 = c.get('sub45')
            if s45:
                im2 = render_label(ws, sz=s45.get('sz', 46), maxw=s45['rect'][0] - 40, style='solid', max_lines=2, rect=s45['rect'])
                alt.append([t0, t1, im2, int(W / 2 - im2.width / 2), int(s45['cy'] - im2.height / 2), None])
            f.write(f"{i+1}\n{srt_time(t0)} --> {srt_time(t1)}\n{' '.join(w[0] for w in ws)}\n\n")

    # safe-zone check (text bounding boxes, shadow margin excluded)
    for it in items:
        x0, y0 = it[3] + 10, it[4] + 10; x1, y1 = it[3] + it[2].width - 10, it[4] + it[2].height - 10
        if y0 < 0.14 * H - 1 or y1 > 0.65 * H + 1 or x0 < 0.06 * W - 1 or x1 > 0.94 * W + 1:
            log.append(f'  !! SAFE ZONE: item t={it[0]:.2f} box=({x0},{y0},{x1},{y1})')

    # ---------- video
    vf = []
    for (x, y, w, h, t0, t1) in c.get('delogo', []):
        vf.append(f"delogo=x={x}:y={y}:w={w}:h={h}:enable='between(t,{t0},{t1})'")
    if c.get('tail'): vf.append(f"tpad=stop_mode=clone:stop_duration={c['tail']}")
    vf.append(f'fps={FPS}')
    if keep:
        vf.append("select='" + '+'.join(f'gte(t,{a:.5f})*lt(t,{b:.5f})' for a, b, o in [(a - 1e-4, b - 1e-4, o) for a, b, o in iv]) + "',setpts=N/FRAME_RATE/TB")
    vf.append(f'scale={W}:{H}:flags=lanczos,unsharp=5:5:0.45:5:5:0.0')
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-an', '-vf', ','.join(vf), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    a45 = c.get('a45', 130); a11 = c.get('a11', 215)
    fmts = [('9x16', 0, H, '3500k'), ('4x5', a45, 1350, '2800k'), ('1x1', a11, 1080, '2300k')]
    encs = []
    for fn, a, hh, br in fmts:
        encs.append(subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{hh}', '-r', str(FPS), '-i', '-',
                                      '-i', os.path.join(WORK, name + '.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', br, '-bufsize', '7000k', '-pix_fmt', 'yuv420p',
                                      '-profile:v', 'high', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-shortest', '-movflags', '+faststart',
                                      os.path.join(OUT, f'{name}_{fn}.mp4')], stdin=subprocess.PIPE, stderr=open(os.path.join(WORK, f'{name}_{fn}.log'), 'w')))
    P = lambda its: [(t0, t1, np.asarray(im)[..., :3].astype(np.float32), np.asarray(im)[..., 3:].astype(np.float32) / 255, im, x, y, an) for t0, t1, im, x, y, an in its]
    pre_base = P(items[:n_main]); pre_sub = P(items[n_main:]); pre_alt = P(alt)
    def comp(fr, pre, t):
        for t0, t1, rgb, al, im, x, y, an in pre:
            if not (t0 <= t < t1): continue
            p = (t - t0) / 0.13
            if an == 'pop' and p < 1:
                s = 0.8 + 0.2 * (1 - (1 - p) ** 2) + 0.05 * np.sin(np.pi * p)
                im2 = im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.BILINEAR)
                x2 = x + (im.width - im2.width) // 2; y2 = y + (im.height - im2.height) // 2
                a2 = np.asarray(im2); rgb2 = a2[..., :3].astype(np.float32); al2 = a2[..., 3:].astype(np.float32) / 255 * min(1, 0.4 + p)
            else: rgb2, al2, x2, y2 = rgb, al, x, y
            hh, ww = rgb2.shape[:2]
            ys, xs = max(0, y2), max(0, x2); ye, xe = min(H, y2 + hh), min(W, x2 + ww)
            if ye <= ys or xe <= xs: continue
            sub = fr[ys:ye, xs:xe].astype(np.float32); a_ = al2[ys - y2:ye - y2, xs - x2:xe - x2]
            fr[ys:ye, xs:xe] = (sub * (1 - a_) + rgb2[ys - y2:ye - y2, xs - x2:xe - x2] * a_ + 0.5).astype(np.uint8)
    fsz = W * H * 3; n = 0
    while n < nfr:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz: break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); t = n / FPS + 1e-4
        comp(fr, pre_base, t)
        frB = fr.copy() if pre_alt else None
        comp(fr, pre_sub, t)
        if pre_alt: comp(frB, pre_alt, t)
        for (fn, a, hh, br), e in zip(fmts, encs):
            e.stdin.write((frB if (fn == '4x5' and frB is not None) else fr)[a:a + hh].tobytes())
        n += 1
    dec.stdout.close(); dec.wait()
    for e in encs: e.stdin.close(); e.wait()
    log.append(f'  video: {n} frames ({n/FPS:.2f}s)')
    print('\n'.join(log), flush=True)
    return name


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        vid, _, sh = arg.partition(':')
        if sh == 'voice':
            log = [f'== {vid}']; gen_voice(V[vid], log); print('\n'.join(log)); continue
        if sh == 'short':
            for s in V[vid].get('shorts', []): build(vid, s)
        else: build(vid)
