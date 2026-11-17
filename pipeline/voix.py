import os, sys, json, re, subprocess, base64, hashlib, difflib, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'voix'); os.makedirs(OUT, exist_ok=True)
CACHE = os.path.join(ROOT, 'cache_voix'); os.makedirs(CACHE, exist_ok=True)

VOICE = {'01': 'UQXv1pYCJdc8grB7QA4g', '02': 'lLp9KH0lLPSsvLcxBIwN', '03': '2qZ0mbkwxQUMq4q7Vz9q', '04': 'h7vSwh1IRhXnTyYrMOo6',
         '05': '9JkQINcsedWxSxigcZ6v', '06': 'mqhi4dyA0omVKB74HZFj', '07': 'Xam1LWMZEgcyiWttHxi7'}
NAME = {'01': 'Revelation', '02': 'Demo-plateau', '03': 'Il-est-enfin-la', '04': 'Maki-face-camera', '05': 'Sous-le-sapin', '06': '3raisons', '07': 'Cadeau'}

# Scripts : texte exact du brief. Les balises [..] ne servent qu'à la version B (v3) et ne sont pas prononcées.
S = {
'01': ("[excited]", [
    "Franchement, je vois déjà dix personnes à qui l'offrir.",
    "Prêts pour le petit cadeau de Noël parfait ? Des chaussettes sushi !",
    "Non mais sérieux ?",
    "Regardez-moi ça : l'emballage, le toucher, l'effet waouh.",
    "[laughs] Oh là là, j'adore.",
    "Quand je l'ai vu, j'ai fait : oh mon dieu.",
    "Je vois déjà dix personnes à qui l'offrir.",
    "Et il y a cinq paires dans la boîte.",
    "Ça existe aussi en version pizza, burger…",
    "Clique sur « Acheter » pour tout voir."]),
'02': ("[whispers]", [
    "On dirait une vraie boîte de sushis, baguettes comprises.",
    "Prends un morceau… ce sont des chaussettes.",
    "Cinq paires, cinq modèles : saumon, tamago, maki.",
    "Drôles à ouvrir le soir même, et elles ne finissent pas au fond d'un tiroir.",
    "Dès le lendemain matin, elles sont aux pieds."]),
'03': ("[warmly]", [
    "Le cadeau dont tout le monde parle à Noël…",
    "… il est enfin là.",
    "On dirait de vrais sushis à emporter, non ?",
    "C'est comme si tu les connaissais par cœur.",
    "Tu sais quel est leur plat préféré.",
    "Cinq paires dans chaque plateau.",
    "À offrir, à apporter en soirée ou à glisser sous le sapin.",
    "Regarde-moi cette tête !",
    "Et le meilleur ?",
    "Un acheté… un offert.",
    "Deux plateaux, tu n'en paies qu'un.",
    "Commande vite pour le recevoir avant Noël."]),
'04': ("[playful]", [
    "C'est ton signe : voilà le cadeau de Noël.",
    "À offrir, à apporter en soirée ou à glisser sous le sapin.",
    "Offre-les et c'est comme si tu les connaissais par cœur, jusqu'à leur plat préféré.",
    "Dix pièces de sushi avec des baguettes en bois. Et aussi des versions pizza et burger, chacune dans sa boîte.",
    "Des modèles qui trompent l'œil.",
    "Regarde-moi cette tête ! [laughs]",
    "Ouais, elle était vraiment surprise.",
    "Drôles à ouvrir, portées toute l'année.",
    "Commande via le lien pour les recevoir avant Noël."]),
'05': ("[sincere]", [
    "C'est sûrement le seul sushi qui a sa place sous le sapin… parce que ce sont des chaussettes !",
    "Cinq paires de chaussettes sushi, emballées comme une vraie boîte à emporter, jusqu'aux baguettes en bois.",
    "L'emballage, les baguettes, la qualité… c'est une idée complètement folle et tellement drôle.",
    "Je vois déjà une dizaine de personnes à qui l'offrir.",
    "Ce ne sont pas juste des chaussettes, c'est tout le cadeau.",
    "Et en ce moment, c'est deux boîtes pour le prix d'une, lien juste en dessous."]),
'06': ("[playful]", [
    "Trois raisons de ne pas acheter des chaussettes sushi.",
    "Un : elles sont tout simplement uniques.",
    "Oublie les cadeaux ennuyeux qui finissent au fond d'un tiroir.",
    "Là, c'est une vraie expérience.",
    "À l'ouverture, tout le monde croit que ce sont de vrais sushis… et en fait, ce sont des chaussettes.",
    "Deux : le rapport qualité-prix est dingue.",
    "Pas juste cinq paires de chaussettes :",
    "une matière douce, de qualité, qui dure longtemps.",
    "Et en plus, elles sont vraiment portées.",
    "Pas un énième cadeau qui prend la poussière.",
    "Trois : tu vas faire tellement plaisir.",
    "Ma mère m'a dit que c'était son cadeau préféré.",
    "Et devine quoi ?",
    "Elle en veut déjà d'autres.",
    "Réaction et fou rire garantis.",
    "Le genre de cadeau qui te fait passer pour quelqu'un de malin.",
    "Tu deviens la personne qui offre les meilleurs cadeaux.",
    "Tout le monde te demande où tu les as trouvées.",
    "Clique sur le lien et découvre tout."]),
'07': ("[calm]", [
    "Besoin d'un cadeau ?",
    "Les chaussettes sushi, c'est le plus joli cadeau qu'on puisse faire.",
    "Moi, j'offre toujours la même bougie à tout le monde.",
    "J'attends toujours la dernière minute pour trouver des idées, et à chaque fois, c'est la panique.",
    "Mais un truc dont tout le monde manque, c'est de chaussettes.",
    "Et de paires dépareillées, toujours.",
    "Celles-là, impossible de les mélanger.",
    "C'est l'équilibre parfait entre pratique et inattendu.",
    "D'abord on croit que ce sont des sushis, puis on comprend que ce sont des chaussettes. Et là, ton cadeau fait réagir, et en plus il est vraiment porté.",
    "C'est le petit cadeau parfait pour toutes les occasions.",
    "Attentionné, drôle, sans en faire trop.",
    "[amused] On dirait des sushis…",
    "Ce sont des chaussettes.",
    "Des chaussettes sushi."]),
}


def strip_tags(t): return re.sub(r'\s*\[[^\]]*\]\s*', ' ', t).strip()


def plain(lines): return ' '.join(strip_tags(l) for l in lines)


def words(t):
    t = unicodedata.normalize('NFC', t.lower()).replace('’', "'")
    t = re.sub(r"[^\w'\- ]", ' ', t).replace('-', ' ').replace("'", ' ')
    rep = {'10': 'dix', '5': 'cinq', '2': 'deux', '3': 'trois', '1': 'un', 'ouh': 'oh', 'waouh': 'waouh', 'wahou': 'waouh', 'wouah': 'waouh'}
    return [rep.get(w, w) for w in t.split() if w]


def tts(voice, text, model, seed):
    if model == 'eleven_v3':
        vs = {'stability': 0.5, 'similarity_boost': 0.9}
    else:
        vs = {'stability': 0.45, 'similarity_boost': 0.9, 'style': 0.25, 'use_speaker_boost': True}
    body = {'text': text, 'model_id': model, 'seed': seed, 'language_code': 'fr', 'voice_settings': vs}
    key = hashlib.sha1(json.dumps([voice, body], sort_keys=True).encode()).hexdigest()[:16]
    mp3 = os.path.join(CACHE, key + '.mp3')
    if not os.path.exists(mp3):
        req = os.path.join(CACHE, key + '.req'); open(req, 'w').write(json.dumps(body))
        r = subprocess.run(['curl', '-sS', '-m', '300', '-X', 'POST', f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128',
                            '-H', 'Content-Type: application/json', '--data-binary', '@' + req, '-o', mp3, '-w', '%{http_code}'], capture_output=True, text=True)
        if r.stdout != '200':
            msg = open(mp3, errors='ignore').read()[:300]; os.remove(mp3); raise RuntimeError(msg)
    return mp3


def stt(mp3):
    j = mp3[:-4] + '.stt.json'
    if not os.path.exists(j):
        r = subprocess.run(['curl', '-sS', '-m', '300', 'https://api.elevenlabs.io/v1/speech-to-text', '-F', 'model_id=scribe_v1', '-F', f'file=@{mp3}',
                            '-F', 'language_code=fr', '-F', 'tag_audio_events=true'], capture_output=True, text=True)
        open(j, 'w').write(r.stdout)
    return json.load(open(j))


def check(expected, d):
    ref = words(expected); hyp = words(re.sub(r'\([^)]*\)', ' ', d.get('text', '')))
    sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
    miss = []; extra = []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op in ('delete', 'replace'): miss.append(' '.join(ref[a0:a1]))
        if op in ('insert', 'replace'): extra.append(' '.join(hyp[b0:b1]))
    err = sum(a1 - a0 for op, a0, a1, b0, b1 in sm.get_opcodes() if op in ('delete', 'replace'))
    ws = [w for w in d.get('words', []) if w.get('type') == 'word']
    span = (ws[-1]['end'] - ws[0]['start']) if ws else 0
    return err, miss, extra, span


def orig_span(n):
    ws = [w for w in json.load(open(os.path.join(ROOT, f'a{n}', 'stt.json')))['words'] if w['type'] == 'word' and not w['text'].startswith('[')]
    return ws[-1]['end'] - ws[0]['start']


def finalize(mp3, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af',
                    'highpass=f=80,deesser=i=0.3,acompressor=threshold=-20dB:ratio=2:attack=10:release=150,loudnorm=I=-16:TP=-1.5:LRA=9',
                    '-ar', '48000', '-ac', '2', '-c:a', 'libmp3lame', '-b:a', '192k', out], check=True)


if __name__ == '__main__':
    vids = sys.argv[1:] or list(S)
    report = {}
    for n in vids:
        tag, lines = S[n]; expected = plain(lines); report[n] = {}
        for ver, model, text, seeds in [('A', 'eleven_multilingual_v2', expected, [1, 2]),
                                         ('B', 'eleven_v3', tag + ' ' + ' '.join(lines), [1, 2])]:
            best = None
            for seed in seeds:
                mp3 = tts(VOICE[n], text, model, seed)
                err, miss, extra, span = check(expected, stt(mp3))
                print(f'{n}{ver} seed{seed}: {err} mot(s) manquant(s) {miss} | ajoutés {extra} | durée parole {span:.1f}s (original {orig_span(n):.1f}s)', flush=True)
                if best is None or err < best[0]: best = (err, mp3, miss, span, seed)
                if err == 0: break
            out = os.path.join(OUT, f'VOIX_{n}_{NAME[n]}_{ver}.mp3'); finalize(best[1], out)
            report[n][ver] = dict(err=best[0], miss=best[2], span=round(best[3], 1), orig=round(orig_span(n), 1), seed=best[4], file=os.path.basename(out))
    json.dump(report, open(os.path.join(OUT, 'report.json'), 'w'), ensure_ascii=False, indent=1)
