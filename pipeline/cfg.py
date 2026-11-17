V = {}
LEA = 'KSyQzmsYhFbuOhqj1Xxv'; MANON = 'm5U7XCsc8v988k2RJAqN'; CAMILLE = 'Da9VfudgKUvFOKayCiue'
MARION = 'Pipj99NMS7t8dQEzyxgB'; AGATHE = 'SptHT9PQ49isQvxFm28t'; CHLOE = 'Hy28BjVfgieDVMiyQpQe'
OFFER = "1 ACHETÉ = 1 OFFERT"

V['01'] = dict(
    name='Revelation', src='01.mp4', dur=25.4, voice=LEA, vs=dict(stability=0.35, style=0.45),
    segs=[
        (0.04, 2.6, "Franchement, je vois déjà dix personnes à qui l'offrir."),
        (2.72, 6.65, "Prêts pour LE petit cadeau de Noël parfait ? Des chaussettes sushi !", "Prêts pour le petit cadeau de Noël parfait ? Des chaussettes sushi !"),
        (6.72, 8.0, "Non mais sérieux ?"),
        (8.06, 11.8, "Regardez-moi ça : l'emballage, le toucher, l'effet waouh."),
        (11.88, 13.15, "Oh là là, j'adore."),
        (13.24, 17.0, "Quand je l'ai vu, j'ai fait : oh mon dieu. Je vois déjà dix personnes à qui l'offrir."),
        (17.1, 18.9, "Et il y a cinq paires dans la boîte."),
        (18.96, 22.2, "Ça existe aussi en version pizza, burger…"),
        (22.3, 25.35, "Clique sur « Acheter » pour tout voir."),
    ],
    cuts=[1.133, 2.367, 3.533, 5.9, 13, 15.6, 18.633, 21.767, 22.867],
    overlays=[dict(text="Je vois déjà 10 personnes à qui l'offrir 😍", t0=0.0, t1=2.6, cx=540, cy=370, sz=60, maxw=820, style='white', sound='pop')],
    sfx=[('snap', 6.6), ('riser', 8.6, 0.9), ('ding', 9.55), ('sparkle', 22.35)],
)

V['02'] = dict(
    sub45=dict(cy=1398, rect=(770, 108), sz=40),
    name='Demo-plateau', src='02.mp4', dur=19.1333, voice=MANON, vs=dict(stability=0.5), model='eleven_v3', oneshot='[whispers]', takes=3,
    segs=[
        (0.14, 3.6, "On dirait des sushis, baguettes comprises."),
        (3.68, 7.0, "Prends un morceau… ce sont des chaussettes."),
        (7.05, 11.0, "Cinq paires, cinq modèles : saumon, tamago, maki."),
        (11.05, 14.95, "Drôles à ouvrir, et elles ne finissent pas au fond d'un tiroir."),
        (15.0, 18.95, "Dès le lendemain matin, elles sont aux pieds."),
    ],
    cuts=[2.167, 8.633, 11.533, 14, 16.967],
    overlays=[dict(text="On dirait des sushis… 🍣", t0=0.0, t1=2.3, cx=540, cy=345, sz=64, style='white', sound='pop'),
              dict(text="1 acheté = 1 offert", t0=16.967, t1=99, cx=541, cy=1010, sz=62, style='badge', rect=(648, 230), anim=None, sound='ding')],
    sfx=[('snap', 3.0), ('riser@', 'chaussettes.', 0, 0.7), ('snap', 6.3), ('snap', 8.9), ('snap', 12.2), ('snap', 14.4)],
)

V['03'] = dict(
    sub_fill=True, sub_cy=1006, sub_rect=(810, 132), sub_sz=50, sub_style='solid', sub_maxw=770,
    name='Il-est-enfin-la', src='03.mp4', dur=27.12, voice=CAMILLE, vs=dict(stability=0.42, style=0.3),
    segs=[
        (0.30, 2.85, "Le cadeau dont tout le monde parle à Noël…"),
        (2.95, 4.12, "Il est enfin là.", "il est enfin là."),
        (4.24, 6.15, "On dirait de vrais sushis, non ?"),
        (6.28, 8.62, "C'est comme si tu les connaissais par cœur."),
        (8.74, 10.55, "Tu sais quel est leur plat préféré."),
        (10.66, 12.3, "Cinq paires dans chaque plateau."),
        (12.40, 15.75, "À offrir, à apporter en soirée ou à glisser sous le sapin."),
        (15.84, 18.2, "Regarde-moi cette tête !"),
        (18.15, 19.1, "Et le meilleur ?"),
        (19.18, 21.02, "Un acheté… un offert."),
        (21.06, 23.25, "Deux plateaux, tu n'en paies qu'un."),
        (23.34, 27.05, "Commande vite pour le recevoir avant Noël."),
    ],
    cuts=[6.04, 10.28, 12.2, 13.96, 15.6, 17.32, 18.88, 23],
    overlays=[dict(text="Il est enfin là !", t0=0.0, t1=4.4, cx=538, cy=422, sz=56, style='white', rect=(430, 108), anim=None, sound='pop'),
              dict(text=OFFER, t0=19.18, t1=22.9, cx=540, cy=425, sz=84, style='offer', sound='ding')],
    sfx=[('ding', 23.34)],
)

V['04'] = dict(
    sub45=dict(cy=1378, rect=(810, 130), sz=44),
    name='Maki-face-camera', src='04.mp4', dur=27.72, voice=CAMILLE, vs=dict(stability=0.38, style=0.4),
    segs=[
        (0.15, 2.4, "C'est ton signe : voilà LE cadeau de Noël.", "C'est ton signe : voilà le cadeau de Noël."),
        (2.48, 5.5, "À offrir, à apporter en soirée ou à glisser sous le sapin."),
        (5.62, 9.28, "Offre-les et c'est comme si tu les connaissais par cœur, jusqu'à leur plat préféré."),
        (9.38, 15.12, "Dix pièces de sushi avec des baguettes en bois. Et aussi des versions pizza et burger, chacune dans sa boîte."),
        (15.24, 16.72, "Des modèles qui trompent l'œil."),
        (16.78, 19.95, "Regarde-moi cette tête ! Ouais, elle était vraiment surprise."),
        (20.06, 22.35, "Drôles à ouvrir, portées toute l'année."),
        (22.44, 27.65, "Commande via le lien pour les recevoir avant Noël."),
    ],
    cuts=[2.52, 4.88, 6.72, 9.16, 11.52, 12.96, 14.12, 15.2, 20.36, 22.16, 24.76],
    overlays=[dict(text="Ton signe pour le cadeau de Noël 🎁", t0=0.0, t1=2.5, cx=540, cy=368, sz=60, maxw=820, style='white', sound='pop')],
    sfx=[('riser', 0.1, 0.8), ('boing', 16.8), ('ding', 22.44)],
)

V['05'] = dict(
    sub45=dict(cy=1363, rect=(810, 130), sz=44),
    name='Sous-le-sapin', src='05.mp4', dur=25.6, voice=CAMILLE, vs=dict(stability=0.45, style=0.25),
    segs=[
        (0.2, 5.05, "C'est sûrement le seul sushi qui a sa place sous le sapin… parce que ce sont des chaussettes !"),
        (5.18, 10.2, "Cinq paires de chaussettes sushi, emballées comme à emporter, jusqu'aux baguettes en bois."),
        (10.32, 15.05, "L'emballage, les baguettes, la qualité… c'est une idée folle et tellement drôle."),
        (15.18, 18.45, "Je vois déjà une dizaine de personnes à qui l'offrir."),
        (18.60, 21.35, "Ce ne sont pas juste des chaussettes, c'est tout le cadeau."),
        (21.50, 25.55, "Et en ce moment, c'est deux boîtes pour le prix d'une, lien juste en dessous."),
    ],
    cuts=[3.44, 4.8, 5.72, 6.76, 8.04, 9.04, 10.52, 11.36, 17.92, 18.92, 20.88],
    overlays=[dict(text="Le seul sushi qui a sa place sous le sapin 🎄", t0=0.0, t1=2.6, cx=540, cy=360, sz=58, maxw=800, style='white', sound='pop'),
              dict(text=OFFER, t0=21.5, t1=99, cx=540, cy=415, sz=80, style='offer', sound='ding')],
    sfx=[('riser@', 'chaussettes !', 0, 0.6)],
)

V['06'] = dict(
    sub45=dict(cy=1301, rect=(810, 198), sz=52),
    name='3raisons', src='06.mp4', dur=47.9, voice=LEA, vs=dict(stability=0.38, style=0.4),
    segs=[
        (0.12, 3.95, "Trois raisons de ne pas acheter des chaussettes sushi."),
        (4.20, 8.75, "Un : elles sont tout simplement uniques. Oublie les cadeaux ennuyeux qui finissent au fond d'un tiroir."),
        (8.88, 10.55, "Là, c'est une vraie expérience."),
        (10.70, 15.55, "À l'ouverture, tout le monde croit que ce sont de vrais sushis… et en fait, ce sont des chaussettes."),
        (15.64, 17.9, "Deux : le rapport qualité-prix est dingue."),
        (18.00, 23.0, "Pas juste cinq paires de chaussettes : une matière douce, de qualité, qui dure longtemps."),
        (23.10, 26.1, "Et elles sont vraiment portées : pas un cadeau qui prend la poussière."),
        (26.22, 28.25, "Trois : tu vas faire tellement plaisir."),
        (28.36, 30.45, "Ma mère m'a dit que c'était son cadeau préféré."),
        (30.54, 32.18, "Et devine quoi ? Elle en veut d'autres."),
        (32.24, 35.1, "Réaction et fou rire garantis."),
        (35.24, 37.8, "Le genre de cadeau qui te fait passer pour quelqu'un de malin."),
        (37.90, 40.5, "Tu deviens la personne qui offre les meilleurs cadeaux."),
        (40.62, 42.32, "Tout le monde te demande où tu les as trouvées."),
        (42.40, 45.2, "Clique sur le lien et découvre tout."),
    ],
    cuts=[3.6, 4.4, 10.567, 14.233, 15.633, 17.9, 20.167, 22.933, 24.833, 26.767, 28.333, 30.967, 35.067],
    overlays=[
        dict(text="STOP ! N'achète pas de\nchaussettes sushi\navant d'avoir vu ça", t0=0.0, t1=3.5, cx=542, cy=454, sz=50, maxw=730, style='white', rect=(800, 266), hl=('stop',), anim=None),
        dict(text="1 : ELLES SONT UNIQUES", t0=3.5, t1=15.4, cx=540, cy=426, sz=46, style='white', rect=(850, 136), anim=None),
        dict(text="2 : UN RAPPORT QUALITÉ-PRIX DINGUE", t0=15.4, t1=26.2, cx=540, cy=426, sz=40, style='white', rect=(850, 136), anim=None),
        dict(text="3 : TU VAS FAIRE PLAISIR", t0=26.2, t1=35.15, cx=540, cy=426, sz=46, style='white', rect=(850, 136), anim=None),
        dict(text=" ", t0=45.9, t1=99, cx=540, cy=1215, sz=40, style='cream', rect=(520, 190), anim=None),
        dict(text="JE COMMANDE", t0=46.0, t1=99, cx=540, cy=1040, sz=58, style='orange', pad=(54, 30), sound='sparkle'),
        dict(text="1", t0=4.2, t1=5.1, cx=540, cy=800, sz=320, style='digit', sound='pop'),
        dict(text="2", t0=15.64, t1=16.5, cx=540, cy=800, sz=320, style='digit', sound='pop'),
        dict(text="3", t0=26.24, t1=27.1, cx=540, cy=800, sz=320, style='digit', sound='pop'),
    ],
    sfx=[('impact', 0.0), ('whoosh', 0.0), ('riser@', 'chaussettes.', 0, 0.8), ('ding', 42.4)],
    shorts=[dict(name='3raisons-COURT', keep=[(0, 15.633), (26.2, 32.2), (42.3667, 47.9)])],
)

V['07'] = dict(
    sub45=dict(cy=1362, rect=(690, 172), sz=50),
    name='Cadeau', src='07.mp4', dur=41.4667, tail=1.2, voice=CHLOE, vs=dict(stability=0.42, style=0.3),
    segs=[
        (0.10, 4.78, "Besoin d'un cadeau ? Les chaussettes sushi, c'est le plus joli cadeau qu'on puisse faire."),
        (4.94, 7.28, "Moi, j'offre toujours la même bougie à tout le monde."),
        (7.36, 13.2, "J'attends toujours la dernière minute pour trouver des idées, et à chaque fois, c'est la panique."),
        (13.36, 16.0, "Mais un truc dont tout le monde manque, c'est de chaussettes."),
        (16.08, 17.5, "Et toujours dépareillées."),
        (17.62, 19.28, "Impossible de les mélanger."),
        (19.36, 22.8, "C'est l'équilibre parfait entre pratique et inattendu."),
        (22.92, 31.02, "D'abord on dirait des sushis, puis on comprend que ce sont des chaussettes. Et là, ton cadeau fait réagir, et en plus il est vraiment porté."),
        (31.30, 35.12, "C'est le petit cadeau parfait pour toutes les occasions."),
        (35.28, 38.12, "Attentionné, drôle, sans en faire trop."),
        (38.22, 42.62, "On dirait des sushis. Ce sont des chaussettes. Des chaussettes sushi."),
    ],
    cuts=[0.733, 1.267, 1.833, 2.5, 4.7, 5.267, 7.2, 8.733, 11.033, 13.2, 14.1, 14.9, 15.967, 16.7, 17.533, 19.167, 22.667, 25.967, 26.9, 29.367, 30.067, 31.067, 32.067, 32.7, 33.2, 34.767, 36.467, 37.167, 38.2, 39.267],
    overlays=[
        dict(text="Besoin d'un cadeau ? 🎁", t0=0.0, t1=2.4, cx=540, cy=345, sz=66, style='white', sound='pop'),
        dict(text="On dirait des sushis.\nCe sont des chaussettes.", t0=38.2, t1=99, cx=541, cy=385, sz=52, maxw=780, style='white', rect=(856, 226), hl=('chaussettes',), anim=None),
    ],
    sfx=[('riser', 37.4, 0.8), ('ding@', 'chaussettes.', 2), ('sparkle@', 'sushi.', 0)],
    shorts=[dict(name='Cadeau-COURT', keep=[(0, 4.7), (13.3, 15.967), (19.167, 31.067), (38.2, 42.6667)])],
)


# ======== Montage avec les voix VALIDÉES (clones des créatrices) ========
import copy
def T(base, **kw):
    d = copy.deepcopy(V[base]); d.update(kw); return d

V['03'] = T('03', take='VOIX_03_Il-est-enfin-la_B.mp3', take_vid='03',
    slots=[(0.30, 2.85), (2.95, 4.12), (4.24, 6.15), (6.28, 8.62), (8.74, 10.55), (10.66, 12.3), (12.40, 15.75),
           (15.84, 18.0), (18.15, 19.1), (19.18, 21.0), (21.06, 23.25), (23.34, 27.05)],
    overlays=[V['03']['overlays'][0], dict(text=OFFER, at=('un', 0), len=3.6, cx=540, cy=425, sz=84, style='offer', sound='ding')],
    sfx=[('ding@', 'Commande', 0)])

_06 = dict(take_vid='06', max_tempo=1.05,
    slots=[(0.12, 3.6), (3.75, 5.70), (5.78, 8.75), (8.88, 10.55), (10.70, 15.55), (15.64, 17.9), (18.00, 19.75), (19.80, 23.0),
           (23.10, 24.35), (24.40, 26.1), (26.20, 28.25), (28.36, 30.45), (30.54, 31.1), (31.18, 32.15), (32.20, 35.1),
           (35.24, 37.8), (37.90, 40.5), (40.62, 42.32), (42.38, 45.6)],
    overlays=[o for o in V['06']['overlays'] if o['text'] not in ('1', '2', '3')] + [
        dict(text="1", at=('Un\u00a0:', 0), len=0.9, cx=540, cy=800, sz=320, style='digit', sound='pop'),
        dict(text="2", at=('Deux\u00a0:', 0), len=0.9, cx=540, cy=800, sz=320, style='digit', sound='pop'),
        dict(text="3", at=('Trois\u00a0:', 0), len=0.9, cx=540, cy=800, sz=320, style='digit', sound='pop')],
    sfx=[('impact', 0.0), ('whoosh', 0.0), ('riser@', 'chaussettes.', 0, 0.8), ('ding@', 'Clique', 0)])
for v in 'AB':
    V['06' + v] = T('06', num='06', name='3raisons-voix' + v, take=f'VOIX_06_3raisons_{v}.mp3', **copy.deepcopy(_06),
                    shorts=[dict(name='3raisons-COURT-voix' + v, lines=[1, 2, 3, 4, 5, 11, 12, 13, 14, 19], end_card=True)])

V['07'] = T('07', take='VOIX_07_Cadeau_B.mp3', take_vid='07',
    slots=[(0.10, 1.05), (1.12, 4.75), (4.94, 7.25), (7.34, 13.2), (13.36, 15.95), (16.05, 17.6), (17.70, 19.25), (19.34, 22.85),
           (22.92, 31.2), (31.30, 35.15), (35.28, 38.2), (38.36, 39.4), (39.42, 40.4), (40.42, 41.45)],
    sfx=[('riser@', 'On', 2, 0.8), ('ding@', 'chaussettes.', 2), ('sparkle@', 'sushi.', 0)],
    shorts=[dict(name='Cadeau-COURT', lines=[1, 2, 5, 6, 7, 9, 12, 13, 14])])
