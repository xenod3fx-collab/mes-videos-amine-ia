import json,subprocess,sys,base64
VID="fEtpdogpDkBrq53KdupV"
lines={
 "L1":"Trois coups de marqueur… et la lettre est faite.",
 "L2":"Peinture à l'huile, pointe à valve.",
 "L3":"Un coup de mousse, un coup de jet… elle bouge pas.",
 "L4":"Et ta caisse change complètement.",
 "L5":"Douze couleurs, à toi de choisir.",
 "L6":"Lettrix, c'est sur gommeo point com.",
 "G1":"En attendant Gé Té A six, j'ai déjà custom ma caisse.",
 "G2":"Trois coups de marqueur… peinture à l'huile, pointe à valve.",
 "G3":"Un coup de jet, elle bouge pas.",
 "G4":"Douze couleurs. À toi de jouer.",
}
for k,t in lines.items():
    body=json.dumps({"text":t,"model_id":"eleven_multilingual_v2","language_code":"fr","seed":7,
      "voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.15,"use_speaker_boost":True,"speed":1.0}})
    r=subprocess.run(["curl","-s","-X","POST",f"https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128",
      "-H","Content-Type: application/json","-d",body,"-o",f"assets/vo/{k}.mp3","-w","%{http_code}"],capture_output=True,text=True)
    print(k,r.stdout)
