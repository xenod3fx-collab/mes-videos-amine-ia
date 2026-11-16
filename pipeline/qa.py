import sys, os, subprocess, json, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out'); rows = []
for f in sorted(glob.glob(OUT + '/*.mp4')):
    if len(sys.argv) > 1 and not any(a in f for a in sys.argv[1:]): continue
    p = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', f], capture_output=True, text=True).stdout)
    v = [s for s in p['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in p['streams'] if s['codec_type'] == 'audio'][0]
    r = subprocess.run(['ffmpeg', '-nostats', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]; TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1]
    row = dict(file=os.path.basename(f), res=f"{v['width']}x{v['height']}", fps=v['r_frame_rate'], vcodec=v['codec_name'], acodec=a['codec_name'], sr=a['sample_rate'], ch=a['channels'],
               dur=round(float(p['format']['duration']), 2), mb=round(os.path.getsize(f) / 1e6, 1), lufs=float(I), tp=float(TP))
    if f.endswith('_9x16.mp4'):
        wav = f.replace('.mp4', '.qa.wav').replace('/out/', '/work/')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vn', '-ac', '1', '-ar', '16000', wav])
        o = subprocess.run(['curl', '-sS', '-m', '180', 'https://api.elevenlabs.io/v1/speech-to-text', '-F', 'model_id=scribe_v1', '-F', f'file=@{wav}', '-F', 'tag_audio_events=true'], capture_output=True, text=True).stdout
        d = json.loads(o); row['lang'] = d.get('language_code'); row['stt'] = d.get('text')
    rows.append(row)
    print(row['file'], row['res'], row['fps'], row['vcodec'], row['acodec'], row['sr'], row['ch'], f"{row['dur']}s", f"{row['mb']}MB", f"{row['lufs']} LUFS", f"TP {row['tp']}", row.get('lang', ''))
    if 'stt' in row: print('   STT:', row['stt'])
json.dump(rows, open(os.path.join(ROOT, 'work', 'qa.json'), 'w'), ensure_ascii=False, indent=1)
