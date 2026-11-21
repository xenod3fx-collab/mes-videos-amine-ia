import subprocess, json, glob, os, re
OUT="/home/user/mes-videos-amine-ia/livrables"
exp={"9x16":(1080,1920),"4x5":(1080,1350),"1x1":(1080,1080)}
files=sorted(glob.glob(OUT+"/*.mp4")); bad=0
for f in files:
    n=os.path.basename(f); fmt=re.search(r"_(9x16|4x5|1x1)_",n).group(1)
    d=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels:format=duration,size","-of","json",f],capture_output=True,text=True).stdout)
    v=[s for s in d["streams"] if s["codec_type"]=="video"][0]; a=[s for s in d["streams"] if s["codec_type"]=="audio"]
    dur=float(d["format"]["duration"]); mb=int(d["format"]["size"])/1e6
    nom=int(re.search(r"_(\d+)s\.mp4",n).group(1))
    # niveau sonore
    r=subprocess.run(["ffmpeg","-nostats","-i",f,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
    lufs=re.findall(r"I:\s+(-?\d+\.\d+) LUFS",r)[-1]; tp=re.findall(r"Peak:\s+(-?\d+\.\d+) dBFS",r)[-1]
    ok=(v["codec_name"]=="h264" and (v["width"],v["height"])==exp[fmt] and v["r_frame_rate"]=="30/1" and v["pix_fmt"]=="yuv420p"
        and a and a[0]["codec_name"]=="aac" and mb<250 and abs(dur-nom)<=0.6)
    bad+=0 if ok else 1
    print(("OK  " if ok else "BAD ")+f"{n:44s} {v['width']}x{v['height']} {v['r_frame_rate']} {dur:5.2f}s {mb:5.1f}Mo {a[0]['codec_name'] if a else 'noaudio'} {lufs} LUFS  peak {tp} dB")
print(len(files),"fichiers,",bad,"problème(s)")
