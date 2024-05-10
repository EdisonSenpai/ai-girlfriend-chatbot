import os
import torch
import requests
import urllib.parse

from scripts.katakana import *

def voicevoxTTS(tts):
    # Se ruleaza VoicevoxEngine.exe inainte de rularea acestui script prin Docker
    # ATENTIE! Rularea prin Doker necesita mult spatiu pe discul C (nu e recomandat daca nu sunt disponibili macar 35-40GB)
    # Se poate urmari un tutorial pe YT despre cum sa muti folderul "docker-desktop-data" pe un alt disc pentru a avea mai mult spatiu pe discul unde e sistemul de operare

    # Folosind GPU:
        # docker pull voicevox/voicevox_engine:nvidia-ubuntu20.04-latest (doar o data se ruleaza aceasta comanda)
        # docker run --rm --gpus all -p 50021:50021 voicevox/voicevox_engine:nvidia-ubuntu20.04-latest
    # Folosind CPU:
        # docker pull voicevox/voicevox_engine:cpu-ubuntu20.04-latest (doar o data se ruleaza aceasta comanda)
        # docker run --rm -it -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest

    voicevoxURL = 'http://localhost:50021/'

    # Convertim textul in katakana pentru ca vocea ei sa sune mai natural in Japoneza. De exemplu, guitar -> ギター
    katakanaText = katakanaConverter(tts)

    # Se poate schimba vocea dupa preferinta. Lista de voci si variatii se poate gasi in speaker.json
    # Sau pe site-ul https://voicevox.hiroshiba.jp
    paramsEncoded = urllib.parse.urlencode({'text': katakanaText, 'speaker': 4})
    request = requests.post(f'{voicevoxURL}audio_query?{paramsEncoded}')
    paramsEncoded = urllib.parse.urlencode({'speaker': 4, 'enable_interrogative_upspeak': True})
    request = requests.post(f'{voicevoxURL}synthesis?{paramsEncoded}', json=request.json())

    with open("output.wav", "wb") as out:
        out.write(request.content)

def sileroTTS(tts, language, model, speaker):
    device = torch.device('cpu')
    torch.set_num_threads(4)
    localFile = 'model.pt'

    if not os.path.isfile(localFile):
        torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt', localFile)

    model = torch.package.PackageImporter(localFile).load_pickle("tts_models", "model")
    model.to(device)

    exText = "I'm alright, thank you and you?"
    sampleRate = 48000

    audioPaths = model.save_wav(text=tts,
                                speaker=speaker,
                                sample_rate=sampleRate)

if __name__ == '__main__':
    voicevoxTTS()
