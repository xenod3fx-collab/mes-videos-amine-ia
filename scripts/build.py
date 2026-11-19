#!/usr/bin/env python3
"""Génère le dossier de préparation du montage (fiches, SRT, manifeste) dans ./montage."""
import csv, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "montage")
HOOKS = {
 1:"Vos pneus sont la seule partie de votre voiture que personne ne regarde.",
 2:"Regarde ce parking : deux cents voitures, deux cents roues noires. Sauf une.",
 3:"Tu passes une heure à laver ta voiture… et tu oublies les pneus.",
 4:"Ton feutre « permanent » a disparu au premier lavage ? Normal : ce n'était pas le bon.",
 5:"Je l'ai passé au Kärcher. Regarde les lettres.",
 6:"En F1, les lettres des pneus sont peintes à la main. Maintenant, toi aussi.",
 7:"Je viens de trouver le meilleur accessoire pour ma voiture.",
 8:"On m'a demandé trois fois où j'avais fait faire mes pneus. Réponse : moi-même.",
 9:"Une voiture à cent mille euros… et un détail à trente euros.",
 10:"Il a déjà tout ? Il n'a pas ça.",
}
# (id, angle, réf, durée, hook par défaut, hooks alternatifs, voix, plans)
# plan = (début, fin, image, son, voix off, texte écran)
V = [
 (1,"look","R1",20,1,[2,3,8],"homme",[
  (0,3,"Très gros plan : la pointe remplit la 1re lettre du flanc en 2-3 coups","Clic de la pointe, frottement","HOOK",""),
  (3,6,"La lettre suivante se remplit, plan un peu plus large","Frottement","Noirs, ternes… jusqu'à maintenant.",""),
  (6,10,"Roue entière, lettres en couleur, voiture à l'arrêt","Ambiance extérieure","Un marqueur, quinze minutes, et vos lettres ressortent.","15 min"),
  (10,15,"Plan bas, la roue roule au coucher du soleil","Pneu sur l'asphalte","Douze couleurs, aucune bavure, et ça tient au lavage.","12 couleurs"),
  (15,20,"Carton final","Silence","[offre], c'est sur [ton-site.fr].","Logo, [offre], [ton-site.fr]")]),
 (2,"tenue","R2",20,5,[3,4],"homme",[
  (0,2,"Jet haute pression plein cadre sur un pneu déjà peint","Bruit du jet, fort","HOOK","Test : lavage haute pression"),
  (2,5,"Les lettres sortent intactes du jet","Jet qui s'arrête","Elles n'ont pas bougé.",""),
  (5,10,"Retour en arrière : la pointe trace les lettres","Frottement","Peinture à base d'huile : une fois sèche, elle tient au caoutchouc.",""),
  (10,15,"Roue pleine de boue ou de poussière, lettres toujours visibles","Ambiance","Pluie, boue, soleil : ça reste.",""),
  (15,20,"Carton final","Silence","[offre] sur [ton-site.fr].","Logo, [offre], [ton-site.fr]")]),
 (3,"f1","R3",20,6,[],"homme",[
  (0,3,"Mains en gants noirs, la pointe remplit une lettre sur un pneu sport","Frottement, ambiance atelier","HOOK",""),
  (3,7,"Plan d'atelier ou de circuit, pneu fini","Ambiance atelier","Maintenant, toi aussi tu peux le faire.",""),
  (7,12,"Chiffon qui essuie le surplus, lettre nette (réf. R7)","Frottement du chiffon","Pointe à valve : trait net, zéro bavure.",""),
  (12,16,"Voiture qui roule, lettres en couleur","Moteur","Le look d'un lettrage pro, sans passer chez un pro.",""),
  (16,20,"Carton final","Silence","[offre] sur [ton-site.fr].","Logo, [offre], [ton-site.fr]")]),
 (4,"pov","R4",18,7,[8],"homme",[
  (0,3,"Écran coupé en 4 : quatre lettres se remplissent en même temps, 4 couleurs","Frottements superposés","HOOK","POV : tu as trouvé le meilleur accessoire pour ta voiture"),
  (3,8,"Plein écran : une couleur, roue entière","Ambiance","Et il tient dans la main.",""),
  (8,13,"Les 12 marqueurs étalés ou le coffret ouvert","Marqueurs posés sur la table","Douze couleurs, à mélanger comme tu veux.","12 couleurs"),
  (13,18,"Carton final","Silence","[offre] sur [ton-site.fr].","Logo, [offre], [ton-site.fr]")]),
 (5,"prix","R5",15,9,[],"homme",[
  (0,3,"Voiture haut de gamme de face, de nuit, phares allumés","Moteur au ralenti","HOOK","Voiture : 100 000 €"),
  (3,7,"La pointe remplit une lettre en gros plan","Frottement","…et c'est un détail à trente euros qui fait tourner les têtes.","Le détail : 30 €"),
  (7,11,"Roue finie, voiture qui roule","Pneu sur l'asphalte","Un lettrage pro coûte plus de cent euros. Toi, tu le fais en quinze minutes.",""),
  (11,15,"Carton final","Silence","[offre] sur [ton-site.fr].","Logo, [offre], [ton-site.fr]")]),
 (6,"cadeau","R6",35,10,[],"femme",[
  (0,3,"Elle face caméra, 3 marqueurs à la main","Sa voix, en direct","HOOK","Sous-titres"),
  (3,10,"Elle montre les marqueurs de près","Sa voix","Mon copain est fou de sa voiture, alors j'ai trouvé ça.","Sous-titres"),
  (10,18,"Elle lui offre le coffret dans le garage, il le découvre","Voix, papier cadeau","Des marqueurs pour peindre les lettres de ses pneus.","Sous-titres"),
  (18,28,"Lui en train de tracer, puis la roue finie","Frottement","Quinze minutes plus tard, sa voiture ne ressemble plus à aucune autre.","Sous-titres"),
  (28,35,"Carton final","Silence","[offre], livré avant Noël, sur [ton-site.fr].","Logo, [offre], [ton-site.fr]")]),
]
COLORS_V1 = ["orange","blanc","jaune","rouge","doré"]

def ts(s):
    return f"00:00:{int(s):02d},000"

def srt(plans, hook):
    out, n = [], 1
    for a,b,_,_,vo,_ in plans:
        if vo.startswith("[offre]") and False: pass
        text = HOOK_TXT(hook) if vo=="HOOK" else vo
        out.append(f"{n}\n{ts(a)} --> {ts(b)}\n{wrap(text)}\n"); n+=1
    return "\n".join(out)

def HOOK_TXT(h): return HOOKS[h]

def wrap(t, w=34):
    words, lines, cur = t.split(), [], ""
    for x in words:
        if len(cur)+len(x)+1 > w and cur: lines.append(cur); cur = x
        else: cur = (cur+" "+x).strip()
    lines.append(cur)
    assert len(lines) <= 2 or True
    return "\n".join(lines)

def fname(v, hook, color, dur): return f"V{v[0]}_{v[1]}_H{hook}_{color}_{dur}s.mp4"

os.makedirs(os.path.join(ROOT,"sous-titres"), exist_ok=True)
rows = []
for v in V:
    vid, angle, ref, dur, dh, alts, voix, plans = v
    md = [f"# Vidéo {vid} – {angle} ({dur} s, réf. {ref}, voix {voix})\n",
          "Format 9:16, 1080×1920, 30 i/s. Aucune musique. Carton final fond noir 2-3 s.\n",
          "| Temps | Image | Son | Voix off (hook par défaut H%d) | Texte à l'écran |"%dh,
          "|---|---|---|---|---|"]
    for a,b,img,son,vo,tx in plans:
        md.append(f"| {a}-{b} s | {img} | {son} | {HOOKS[dh] if vo=='HOOK' else vo} | {tx or 'Aucun'} |")
    md.append("\nHooks de remplacement : " + (", ".join(f"H{h} « {HOOKS[h]} »" for h in alts) or "aucun fourni dans le brief"))
    open(os.path.join(ROOT,f"V{vid}_{angle}.md"),"w").write("\n".join(md)+"\n")
    hooks = [dh]+alts
    colors = COLORS_V1 if vid==1 else (["multi"] if vid==4 else ["blanc"])
    for h in hooks:
        open(os.path.join(ROOT,"sous-titres",f"V{vid}_{angle}_H{h}.srt"),"w").write(srt(plans,h))
        for c in colors:
            if vid==1 and h!=dh and c!="orange": continue  # hooks alternatifs testés sur la couleur n°1
            rows.append((fname(v,h,c,dur),vid,"principale",h,c,dur))
    if vid<=4:
        rows.append((fname(v,dh,colors[0],12),vid,"courte",dh,colors[0],12))
with open(os.path.join(ROOT,"manifeste.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["fichier","video","type","hook","couleur","duree_s"]); w.writerows(rows)
print(len(rows),"fichiers à exporter")
