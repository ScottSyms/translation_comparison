import requests
import uuid
import json
import spacy
from string import punctuation
import urllib.request
from bs4 import BeautifulSoup
import fr_core_news_lg


# Set up the Microsoft Translation boiler plate
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


# Load the French and English tokenization lists
nlpen = spacy.load("en_core_web_lg")
nlpfr= fr_core_news_lg.load()


# Fetch two sample pages
# french=urllib.request.urlopen("https://www.canada.ca/fr/ministere-defense-nationale/organisation/politiques-normes/directives-ordonnances-administratives-defense/serie-5000/5031/5031-50-apprentissage-et-perfectionnement-professionnel-du-personnel-civil.html")
# english=urllib.request.urlopen("https://www.canada.ca/en/department-national-defence/corporate/policies-standards/defence-administrative-orders-directives/5000-series/5031/5031-50-civilian-learning-and-professional-development.html")

english=urllib.request.urlopen("https://www.canada.ca/en/department-national-defence/corporate/policies-standards/defence-administrative-orders-directives/1000-series/1002/1002-1-requests-under-privacy-act-personal-information.html")
french=urllib.request.urlopen("https://www.canada.ca/fr/ministere-defense-nationale/organisation/politiques-normes/directives-ordonnances-administratives-defense/serie-1000/1002/1002-1-demandes-de-renseignements-personnels-vertu-loi-protection-des-renseignements-personnels.html")


# extract the data from the pages and remove line breaks
english=BeautifulSoup(english, features="lxml").get_text().replace("\n", " ")
french=BeautifulSoup(french, features="lxml").get_text().replace("\n", " ")


# Translate the French page into English
params = {
    'api-version': '3.0',
    'from': 'fr',
    'to': ['en']
}
# Pass the French text to the translation service and isolate the text
body = [{
    'text': french
}]
request = requests.post(constructed_url, params=params, headers=headers, json=body)
translated_from_french = request.json()[0]["translations"][0]["text"]


# Translate the English text to French
params = {
    'api-version': '3.0',
    'from': 'en',
    'to': ['fr']
}
# Pass the English text to the translation service and isolate the text
body = [{
    'text': english
}]
request = requests.post(constructed_url, params=params, headers=headers, json=body)
translated_from_english = request.json()[0]["translations"][0]["text"]


# Parse all texts in the language parser
original_french=nlpfr(french)
original_english=nlpen(english)
french_from_english=nlpen(translated_from_french)
english_from_french=nlpfr(translated_from_english)

# Extract all the significant words from the source English text
keywords_original_english={}
stopwords=list(spacy.lang.en.stop_words.STOP_WORDS)
pos_tag = ['VERB', 'ADJ', 'NOUN', 'ADV']
for token in original_english:
           if(token.text in stopwords or token.text in punctuation):
             continue
           if(token.pos_ in pos_tag):
                if (token.lemma_ in keywords_original_english.keys()):
                    keywords_original_english[token.lemma_]=keywords_original_english[token.lemma_]+1
                else:
                    keywords_original_english[token.lemma_]=1

# Extract all the significant words from the source French text
keywords_original_french={}
stopwords=list(spacy.lang.fr.stop_words.STOP_WORDS)
pos_tag = ['VERB', 'ADJ', 'NOUN', 'ADV']
for token in original_french:
           if(token.text in stopwords or token.text in punctuation):
             continue
           if(token.pos_ in pos_tag):
                if (token.lemma_ in keywords_original_french.keys()):
                    keywords_original_french[token.lemma_]=keywords_original_french[token.lemma_]+1
                else:
                    keywords_original_french[token.lemma_]=1

# Extract all the significant words fromt the French translated from English
keywords_translated_from_french={}
stopwords=list(spacy.lang.en.stop_words.STOP_WORDS)
pos_tag = ['VERB', 'ADJ', 'NOUN', 'ADV']
for token in french_from_english:
           if(token.text in stopwords or token.text in punctuation):
             continue
           if(token.pos_ in pos_tag):
                if (token.lemma_ in keywords_translated_from_french.keys()):
                    keywords_original_french[token.lemma_]=keywords_translated_from_french[token.lemma_]+1
                else:
                    keywords_translated_from_french[token.lemma_]=1

# Extract all the significant words from the English translated from the French
keywords_translated_from_english={}
stopwords=list(spacy.lang.fr.stop_words.STOP_WORDS)
pos_tag = ['VERB', 'ADJ', 'NOUN', 'ADV']
for token in english_from_french:
           if(token.text in stopwords or token.text in punctuation):
             continue
           if(token.pos_ in pos_tag):
                if (token.lemma_ in keywords_translated_from_english.keys()):
                    keywords_translated_from_english[token.lemma_]=keywords_translated_from_english[token.lemma_]+1
                else:
                    keywords_translated_from_english[token.lemma_]=1


french_comparison=set(keywords_translated_from_french.keys()).intersection(set(keywords_original_french.keys()))
english_comparison=set(keywords_translated_from_english.keys()).intersection(set(keywords_original_english.keys()))

print("How many words in the original English", len(keywords_original_english))
print("How many words in the original French", len(keywords_original_french))
print("How many words shared between English translations.", len(english_comparison))
print("How many words shared between the French translations", len(french_comparison))
print("Simularity English", len(english_comparison)*2/(len(keywords_original_english)+len(keywords_translated_from_french)))
print("Simularity French", len(french_comparison)*2/(len(keywords_original_french)+len(keywords_translated_from_english)))

# Open a file and save some diagnostic data
f=open("summary_trans.txt", "w")
f.write(english + "\n\n\n")
f.write(translated_from_french + "\n\n\n")
f.write(french + "\n\n\n")


# Write the sorted word lists
f.write("Original English")
for i,j in sorted(keywords_original_english.items()) :
    f.write(i+"\n")

f.write("\n\n\n\nTranslated English")
for i,j in sorted(keywords_translated_from_french.items()):
    f.write(i+"\n")

f.write("\n\n\n\Original French")
for i,j in sorted(keywords_original_french.items()):
    f.write(i+"\n")

f.write("\n\n\n\Translated French")
for i,j in sorted(keywords_translated_from_english.items()):
    f.write(i+"\n")
f.close()   
