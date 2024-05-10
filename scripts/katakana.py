import sys
import pandas as pd
import alkana
import re
import unidic
import MeCab

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

alphaReg = re.compile(r'^[a-zA-Z]+$')

def isalpha(s):
    return alphaReg.match(s) is not None

def katakanaConverter(text):
    wakati = MeCab.Tagger('-Owakati')
    wakatiRez = wakati.parse(text)

    df = pd.DataFrame(wakatiRez.split(" "), columns=["word"])
    df = df[df["word"].str.isalpha() == True]
    df["english_word"] = df["word"].apply(isalpha)
    df = df[df["english_word"] == True]
    df["katakana"] = df["word"].apply(alkana.get_kana)

    dictRep = dict(zip(df["word"], df["katakana"]))

    for word, read in dictRep.items():
        try:
            text = text.replace(word, read)
        except:
            pass
    
    return text
