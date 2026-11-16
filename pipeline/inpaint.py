import sys, subprocess, numpy as np, onnxruntime as ort, os, time
from PIL import Image
from scipy import ndimage
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# regions: (mode, band(y0,y1), xclamp(x0,x1), t0, t1[, thr])
R = {
 '07': dict(fps=30, regs=[('white', (860, 951), (140, 580), 0, 99), ('white', (850, 938), (140, 580), 40.0, 99)]),
 '05': dict(fps=25, regs=[('white', (877, 935), (40, 680), 0, 99)]),
 '04': dict(fps=25, regs=[('white', (887, 945), (40, 680), 0, 99)]),
 '06': dict(fps=30, regs=[('dark', (813, 917), (96, 624), 0, 46.2)]),
 '02': dict(fps=30, regs=[('fixed', (900, 964), (112, 608), 0, 16.95)]),
 '03': dict(fps=25, regs=[('fixed', (644, 698), (100, 628), 0, 99), ('fixed', (255, 307), (244, 474), 0, 4.4)]),
}
vid = sys.argv[1]; c = R[vid]; W, H = 720, 1280; CW, CH = 640, 320
so = ort.SessionOptions(); so.intra_op_num_threads = int(sys.argv[2]) if len(sys.argv) > 2 else 2
sess = ort.InferenceSession(os.path.join(ROOT, 'inp/lama.onnx'), so, providers=['CPUExecutionProvider'])
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', f'{ROOT}/src/{vid}.mp4', '-an', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(c['fps']), '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '10', '-pix_fmt', 'yuv420p', f'{ROOT}/clean/{vid}.tmp.mp4'], stdin=subprocess.PIPE)

def detect(fr, mode, band, xc):
    y0, y1 = band; x0, x1 = xc
    if mode == 'fixed': return (x0, y0, x1, y1)
    a = fr[y0 + 6:y1 - 6, :, :].astype(int)
    m = (a.min(2) > 232) if mode == 'white' else (a.max(2) < 80)
    col = m.mean(0) > 0.30
    col[:x0] = False; col[x1:] = False
    col = ndimage.binary_closing(np.pad(col, 40), structure=np.ones(31))[40:-40]
    lab, k = ndimage.label(col)
    if k == 0: return None
    sizes = ndimage.sum(col, lab, range(1, k + 1)); j = int(np.argmax(sizes)) + 1
    xs = np.where(lab == j)[0]
    if len(xs) < 70: return None
    return (int(max(x0, xs[0] - 14)), y0 - 9, int(min(x1, xs[-1] + 14)), y1 + 14)

def infer(jobs):
    # jobs: list of (frame, rect) ; two strips per inference
    for i in range(0, len(jobs), 2):
        pair = jobs[i:i + 2]
        img = np.zeros((512, 512, 3), np.float32); msk = np.zeros((512, 512), np.float32); meta = []
        for k, (fr, (xa, ya, xb, yb)) in enumerate(pair):
            cy = (ya + yb) // 2; cx = (xa + xb) // 2
            x0 = int(np.clip(cx - CW // 2, 0, W - CW)); y0 = int(np.clip(cy - CH // 2, 0, H - CH))
            crop = Image.fromarray(fr[y0:y0 + CH, x0:x0 + CW]).resize((512, 256), Image.LANCZOS)
            m = np.zeros((CH, CW), np.uint8); m[ya - y0:yb - y0, xa - x0:xb - x0] = 255
            ms = np.asarray(Image.fromarray(m).resize((512, 256), Image.BILINEAR)) > 20
            img[k * 256:(k + 1) * 256] = np.asarray(crop, np.float32) / 255; msk[k * 256:(k + 1) * 256] = ms
            meta.append((x0, y0, m))
        if len(pair) == 1:
            img[256:] = img[:256][::-1]; msk[256:] = 0
        o = sess.run(None, {'image': img.transpose(2, 0, 1)[None], 'mask': msk[None, None]})[0][0].transpose(1, 2, 0)
        o = np.clip(o, 0, 255).astype(np.uint8)
        for k, (fr, rect) in enumerate(pair):
            x0, y0, m = meta[k]
            fill = np.asarray(Image.fromarray(o[k * 256:(k + 1) * 256]).resize((CW, CH), Image.LANCZOS), np.float32)
            al = ndimage.gaussian_filter(m.astype(np.float32) / 255, 2.0)[..., None]
            al = np.maximum(al, (m[..., None] > 0) * 0.0)
            al = np.clip(al * 1.6, 0, 1)
            reg = fr[y0:y0 + CH, x0:x0 + CW].astype(np.float32)
            fr[y0:y0 + CH, x0:x0 + CW] = (reg * (1 - al) + fill * al + 0.5).astype(np.uint8)

def alpha_for(rect):
    xa, ya, xb, yb = rect
    m = np.zeros((H, W), np.float32); m[ya:yb, xa:xb] = 1
    y0, y1 = max(0, ya - 8), min(H, yb + 8); x0, x1 = max(0, xa - 8), min(W, xb + 8)
    al = np.clip(ndimage.gaussian_filter(m[y0:y1, x0:x1], 2.0) * 1.6, 0, 1)[..., None]
    return (y0, y1, x0, x1, al)

def same(r1, r2):
    if len(r1) != len(r2) or not r1: return False
    return all(max(abs(a - b) for a, b in zip(p, q)) <= 8 for p, q in zip(r1, r2))

def small(fr): return fr[::16, ::16].astype(np.int16)
def is_cut(a, b): return np.abs(small(a) - small(b)).mean() > 22

def read():
    global n
    buf = dec.stdout.read(fsz)
    if len(buf) < fsz: return None
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); t = n / c['fps']; n += 1
    rects = []
    for mode, band, xc, t0, t1 in c['regs']:
        if t0 <= t < t1:
            r = detect(fr, mode, band, xc)
            if r: rects.append(r)
    return [fr, rects, fr.copy()]

n = 0; t_start = time.time(); fsz = W * H * 3; ninf = 0; nint = 0
K = None  # previous output item [fr(processed), rects, orig]
done = False
while not done:
    B = []
    while len(B) < 4:
        it = read()
        if it is None: done = True; break
        B.append(it)
    if not B: break
    seq = ([K] if K else [None]) + B
    interp = []
    for p in (1, 3):
        if p + 1 < len(seq) and seq[p - 1] is not None:
            a_, b_, c_ = seq[p - 1], seq[p], seq[p + 1]
            if same(a_[1], b_[1]) and same(b_[1], c_[1]) and not is_cut(a_[2], b_[2]) and not is_cut(b_[2], c_[2]):
                interp.append(p)
    jobs = []
    for p in range(1, len(seq)):
        if p not in interp:
            for r in seq[p][1]: jobs.append((seq[p][0], r))
    if jobs: infer(jobs); ninf += len(jobs)
    for p in interp:
        fr = seq[p][0]; A = seq[p - 1][0]; Cn = seq[p + 1][0]
        for r, r2 in zip(seq[p][1], seq[p + 1][1]):
            u = (min(r[0], r2[0]), min(r[1], r2[1]), max(r[2], r2[2]), max(r[3], r2[3]))
            y0, y1, x0, x1, al = alpha_for(u)
            fill = (A[y0:y1, x0:x1].astype(np.float32) + Cn[y0:y1, x0:x1]) / 2
            fr[y0:y1, x0:x1] = (fr[y0:y1, x0:x1] * (1 - al) + fill * al + 0.5).astype(np.uint8)
            nint += 1
    for it in B: enc.stdin.write(it[0].tobytes())
    K = B[-1]
    if n % 100 < 4: print(vid, n, f'{time.time()-t_start:.0f}s inferred {ninf} interp {nint}', flush=True)
enc.stdin.close(); enc.wait()
os.rename(f'{ROOT}/clean/{vid}.tmp.mp4', f'{ROOT}/clean/{vid}.mp4')
print(vid, 'done', n, f'{time.time()-t_start:.0f}s inferred {ninf} interp {nint}', flush=True)
