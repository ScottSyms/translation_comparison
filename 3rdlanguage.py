from gettext import translation
from webbrowser import get
import requests
import re
import uuid
import json
import spacy
from string import punctuation
# import urllib.request
from bs4 import BeautifulSoup
import fr_core_news_lg
import es_core_news_lg


# Retrieve a web page
def get_webpage_text(url):
    # Fetch two sample pages
    page=requests.get(url)

    # extract the text from the pages
    page=BeautifulSoup(page.text, features="lxml").get_text()

    # Strip off excess line endings 
    return re.sub(r'\n+', '\n', page)

# Translate text from source language to Spanish
def get_translation(text, source_language):
    # Translate the French page into Spanish
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': ['es']
    }

    # Pass the text to the translation service and return it
    body = [{
        'text': text
    }]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    return request.json()[0]["translations"][0]["text"]

# Extract the significant words from the text
def isolate_words(text):
    # Extract all the significant words from the source English text
    keywords={}
    if text.lang_=="en":
        stopwords=list(spacy.lang.en.stop_words.STOP_WORDS)
    elif text.lang_=="fr":
        stopwords=list(spacy.lang.fr.stop_words.STOP_WORDS)
    else:
        stopwords=list(spacy.lang.es.stop_words.STOP_WORDS)
    pos_tag = ['VERB', 'NOUN', 'ADV', 'ADJ']
    for token in text:
            if(token.text in stopwords or token.text in punctuation):
                continue
            if(token.pos_ in pos_tag):
                    if (token.lemma_ in keywords.keys()):
                        keywords[token.lemma_]=keywords[token.lemma_]+1
                    else:
                        keywords[token.lemma_]=1
    return keywords


# Set up the Microsoft Translation boiler plate
# Taken from Translation services example
# **************************************************
# Add your subscription key and endpoint
subscription_key = "c3e034153d3f4842bd4db3886b75e5b2"
endpoint="https://api.cognitive.microsofttranslator.com/"

# Add your location, also known as region. The default is global.
# This is required if using a Cognitive Services resource.
location = "canadacentral"

# Custruct the endpoint URL 
path = '/translate'
constructed_url = endpoint + path

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# Load the language token lists
nlpen = spacy.load("en_core_web_lg")
nlpfr= fr_core_news_lg.load()
nlpes=es_core_news_lg.load()

# Get the pages
english=get_webpage_text("https://www.canada.ca/en/department-national-defence/corporate/policies-standards/defence-administrative-orders-directives/1000-series/1002/1002-1-requests-under-privacy-act-personal-information.html")
french=get_webpage_text("https://www.canada.ca/fr/ministere-defense-nationale/organisation/politiques-normes/directives-ordonnances-administratives-defense/serie-1000/1002/1002-1-demandes-de-renseignements-personnels-vertu-loi-protection-des-renseignements-personnels.html")


# Translate them
translated_from_english=get_translation(english, "en")
translated_from_french=get_translation(french, "fr")

# Parse all texts in the language parser
original_french_keywords=isolate_words(nlpfr(french))
original_english_keywords=isolate_words(nlpen(english))
translation_from_english_keywords=isolate_words(nlpes(translated_from_french))
translation_from_french_keywords=isolate_words(nlpes(translated_from_english))


comparison=set(translation_from_french_keywords.keys()).intersection(set(translation_from_english_keywords.keys()))

print("How many words in the original English", len(original_english_keywords))
print("How many words in the original French", len(original_french_keywords))
print("How many words in the English translation", len(translation_from_english_keywords))
print("How many words in the French Translation", len(translation_from_french_keywords))
print("How many words shared between  translations.", len(comparison))

# similarity score is the comparison value multiplied by 2 and divided by the total number of keywords for French and English source.
print("Simularity: %5.2f" % ((len(comparison)*2/(len(translation_from_english_keywords)+len(translation_from_french_keywords)))*100))

# Open a file and save some diagnostic data
f=open("translation_summary.txt", "w")
f.write(english + "\n\n\n")
f.write(translated_from_french + "\n\n\n")
f.write(french + "\n\n\n")
f.write(translated_from_english + "\n\n\n")



# Write the sorted word lists
f.write("Original English\n")
for i,j in sorted(original_english_keywords.items(), key=lambda item: item[1], reverse=True):
    f.write(str(j)+" " +i+"\n")

f.write("\n\n\n\nTranslated English\n")
for i,j in sorted(translation_from_english_keywords.items(), key=lambda item: item[1], reverse=True): 
    f.write(str(j)+" " +i+"\n")

f.write("\n\n\n\Original French\n")
for i,j in sorted(original_french_keywords.items(), key=lambda item: item[1], reverse=True): 
    f.write(str(j)+" " +i+"\n")

f.write("\n\n\n\Translated French\n")
for i,j in sorted(translation_from_french_keywords.items(), key=lambda item: item[1], reverse=True): 
    f.write(str(j)+" " +i+"\n")

f.close()   
