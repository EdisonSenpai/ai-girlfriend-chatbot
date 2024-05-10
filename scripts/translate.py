import sys
import json
import requests
import googletrans

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def googleTranslate(text, source, target):
    try:
        translator = googletrans.Translator()
        rez = translator.translate(text, src=source, dest=target)
        return rez.text
    except:
        print("Error while translating!")
        return
    
def googleDetect(text):
    try:
        translator = googletrans.Translator()
        rez = translator.detect(text)
        return rez.lang.upper()
    except:
        print("Error while detecting language!")
        return
    
# Functie alternativa pentru Google Translate
def deeplxTranslate(text, source, target):
    url = "http://localhost:1188/translate"
    headers = {"Content-Type": "application/json"}

    # Definire parametrii pentru cererea de traducere
    params = {
        "text": text,
        "source_lang": source,
        "target_lang": target
    }

    # Convertire parametrii in sir de cractere (format JSON)
    payload = json.dumps(params)

    # Trimitere cerere POST in cadrul payload-ului de JSON
    response = requests.post(url, headers=headers, data=payload)

    # Obtinerea de date ale raspunsului ca obiect de tip JSON
    data = response.json()

    # Extragerea textului tradus din raspuns
    translated_text = data['data']

    return translated_text

if __name__ == '__main__':
    text = "buna ziua"
    source = googleTranslate(text, "RO", "JA")
    print(source)
