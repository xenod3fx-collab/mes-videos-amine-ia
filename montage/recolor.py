import numpy as np
from PIL import Image, ImageFilter

def _hsv(a):
    r,g,b=a[...,0],a[...,1],a[...,2]
    mx=a.max(-1); mn=a.min(-1); d=mx-mn+1e-6
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
    s=d/(mx+1e-6)
    return h,s,mx

def gold_mask(a, loose=False):
    h,s,v=_hsv(a)
    mode = 'loose' if loose is True else ('strict' if loose is False else loose)
    # rampes douces autour de la teinte doree
    if mode=='wide':
        hm=np.clip((h-30)/4,0,1)*np.clip((64-h)/6,0,1)
        sm=np.clip((s-0.16)/0.10,0,1)
        vm=np.clip((v-0.28)/0.10,0,1)
    elif mode=='loose':
        hm=np.clip((h-24)/6,0,1)*np.clip((60-h)/6,0,1)
        sm=np.clip((s-0.38)/0.14,0,1)
        vm=np.clip((v-0.30)/0.12,0,1)
    else:
        hm=np.clip((h-33)/5,0,1)*np.clip((62-h)/6,0,1)
        sm=np.clip((s-0.27)/0.12,0,1)
        vm=np.clip((v-0.24)/0.10,0,1)
    m=hm*sm*vm
    return m

def recolor(img, mode, blur=1.4, loose=False):
    a=np.asarray(img.convert("RGB")).astype(np.float32)/255
    m=gold_mask(a, loose)
    mi=Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    m=np.asarray(mi).astype(np.float32)[...,None]/255
    lum=(0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2])[...,None]
    if mode=="white":
        l=np.clip(0.50+0.62*lum,0,1)
        new=np.concatenate([l*1.0,l*0.995,l*0.98],-1)
        new=np.clip(new,0,1)
    elif mode=="pink":
        # garde la luminosite, teinte rose vif
        l=np.clip(lum*1.15,0,1)
        new=np.concatenate([np.clip(l*1.35+0.05,0,1),np.clip(l*0.22,0,1),np.clip(l*0.80+0.05,0,1)],-1)
    out=a*(1-m)+new*m
    return Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))

if __name__=="__main__":
    import sys
    ts=["1.8","3.5","6.0","10.5","12.8","15.0"]
    for mode in ("white","pink"):
        tiles=[Image.open(f"rc/f_{t}.png").convert("RGB") for t in ts]
        res=[recolor(t,mode).resize((288,512)) for t in tiles]
        W=Image.new("RGB",(288*len(res),512))
        for i,r in enumerate(res): W.paste(r,(288*i,0))
        W.save(f"rc/test_{mode}.png")


def recolor_video(src, t0, t1, mode, out, loose=False):
    """Recolorie les lettres dorees de src[t0:t1] (720x1280) -> out (mp4 quasi sans perte)."""
    import subprocess
    W,H=720,1280
    rd=subprocess.Popen(["ffmpeg","-v","error","-ss",str(t0),"-t",str(t1-t0),"-i",src,"-vf","fps=30","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-",
                         "-c:v","libx264","-crf","10","-preset","fast","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
    n=0
    while True:
        buf=rd.stdout.read(W*H*3)
        if len(buf)<W*H*3: break
        im=Image.frombuffer("RGB",(W,H),buf,"raw","RGB",0,1)
        wr.stdin.write(recolor(im,mode,loose=loose).tobytes()); n+=1
    wr.stdin.close(); wr.wait(); rd.wait()
    return n
