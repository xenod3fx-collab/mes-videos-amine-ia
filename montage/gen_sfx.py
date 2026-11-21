import json,subprocess
sfx={
 "click":("Close-up mechanical click of a paint marker valve tip being pressed down, short, dry, no music",1.0),
 "scrape":("Paint marker tip rubbing and squeaking softly on a rubber tire sidewall, close up, wet paint, no music",4.0),
 "cloth":("Microfiber cloth rubbing on a wet rubber tire surface, close microphone, no music",3.5),
 "foam":("Soapy foam being scrubbed with a wet sponge on a car tire, close microphone, no music",3.5),
 "jet":("High pressure washer water jet spraying on a car wheel and tire, close, no music",5.0),
 "engine":("Sports car engine idling then a slow pass-by on a quiet street at night, no music",5.0),
 "tire":("Car tire rolling on asphalt road at moderate speed, steady road noise, no music",6.0),
 "city":("Quiet city night ambience, light distant traffic, wet street, no music",8.0),
 "chime":("Short video game mission complete notification blip, clean electronic, no music, very short",1.2),
}
for k,(p,d) in sfx.items():
    body=json.dumps({"text":p,"duration_seconds":d,"prompt_influence":0.6})
    r=subprocess.run(["curl","-s","-X","POST","https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128","-H","Content-Type: application/json","-d",body,"-o",f"assets/sfx/{k}.mp3","-w","%{http_code}"],capture_output=True,text=True)
    print(k,r.stdout)
