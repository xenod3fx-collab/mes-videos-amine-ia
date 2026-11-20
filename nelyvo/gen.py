from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, math
random.seed(7)
SB="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"; S="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
GOLD=(244,200,110); 
def bg(w,h):
    im=Image.new("RGB",(w,h)); px=im.load()
    for y in range(h):
        for x in range(w):
            d=math.hypot(x-w*.5,y-h*.45)/math.hypot(w*.5,h*.6)
            t=min(1,d)
            px[x,y]=(int(30-18*t),int(20-12*t),int(60-30*t)) if False else (int(52-34*t),int(18-8*t),int(40-14*t))
    return im
def glow(im,xy,r,col,a=150):
    l=Image.new("RGBA",im.size,(0,0,0,0));d=ImageDraw.Draw(l)
    d.ellipse((xy[0]-r,xy[1]-r,xy[0]+r,xy[1]+r),fill=col+(a,))
    l=l.filter(ImageFilter.GaussianBlur(r/2)); im.paste(l,(0,0),l)
def star(d,cx,cy,R,fill,n=4,k=.28):
    pts=[]
    for i in range(n*2):
        r=R if i%2==0 else R*k; a=math.pi*i/n-math.pi/2
        pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    d.polygon(pts,fill=fill)
def sparkles(im,n,minr,maxr,area):
    for _ in range(n):
        x=random.randint(area[0],area[2]);y=random.randint(area[1],area[3]);r=random.randint(minr,maxr)
        glow(im,(x,y),r*2,GOLD,60)
        d=ImageDraw.Draw(im); star(d,x,y,r,(255,236,190))
def text_c(d,xy,t,f,fill,sp=0):
    w=sum(d.textlength(c,font=f)+sp for c in t)-sp; x=xy[0]-w/2
    for c in t:
        d.text((x,xy[1]),c,font=f,fill=fill,anchor="lm"); x+=d.textlength(c,font=f)+sp
# PROFILE
W=1080; im=bg(W,W).convert("RGB")
glow(im,(W//2,W//2-60),330,(255,170,70),110)
sparkles(im,40,4,12,(60,60,W-60,W-60))
d=ImageDraw.Draw(im)
d.ellipse((30,30,W-30,W-30),outline=GOLD,width=6)
star(d,W//2,330,150,GOLD,k=.25)
star(d,W//2,330,70,(255,244,214),k=.3)
text_c(d,(W//2,640),"NELYVO",ImageFont.truetype(SB,140),(255,244,226),sp=6)
d.line((W//2-160,745,W//2+160,745),fill=GOLD,width=4)
text_c(d,(W//2,805),"MAGIE DE NOËL",ImageFont.truetype(S,46),GOLD,sp=8)
im.save("nelyvo-photo-profil-1080.png")
# COVER 1640x924 ; safe zone mobile centre ~ 640px wide
CW,CH=1640,924
c=bg(CW,CH)
glow(c,(CW//2,CH//2),420,(255,160,60),90)
sparkles(c,70,4,13,(0,0,CW,CH))
d=ImageDraw.Draw(c)
star(d,CW//2,250,70,GOLD,k=.25)
text_c(d,(CW//2,420),"NELYVO",ImageFont.truetype(SB,170),(255,244,226),sp=10)
d.line((CW//2-200,515,CW//2+200,515),fill=GOLD,width=4)
text_c(d,(CW//2,590),"La magie de Noël, chez vous",ImageFont.truetype(S,54),GOLD)
text_c(d,(CW//2,665),"Décorations & projecteurs lumineux  ·  nelyvo.com",ImageFont.truetype(S,34),(235,220,200))
c.save("nelyvo-couverture-1640x924.png")
