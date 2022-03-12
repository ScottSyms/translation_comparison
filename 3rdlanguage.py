from gettext import translation
from webbrowser import get
import requests
import re
import sys
import uuid
import json
import spacy
from string import punctuation
from bs4 import BeautifulSoup
import fr_core_news_lg
import es_core_news_lg

# TODO
# handle errors from the translator
# "{\"error\":{\"code\":400077,\"message\":\"The maximum request size has been exceeded.\"}}"
# handle requests greater than 20K characters.  Split on sentence boundaries for translation benefit.
# Semantic similarity with Word2Vec/Spacy similarity
# Use MS similarity feature
# play with stripping words that aren't in the vocabulary.


# Retrieve a web page
def get_webpage_text(url):
    # Fetch two sample pages
    page = requests.get(url)

    # extract the text from the pages
    page = BeautifulSoup(page.content, features="lxml").get_text()
    # Strip off excess line endings
    return re.sub(r'\n+', '\n', page)

# Translate text from source language to Spanish


def get_translation(text, source_language):
    print("Text is {} characters.".format(len(text)))
    # Translate the French page into Spanish
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': ['es']
    }
    if source_language == "en":
        print("Translating from English.")
        nlpobject = nlpen(text)
    elif source_language == "fr":
        print("Translating from French.")
        nlpobject = nlpfr(text)
    else:
        print("Translating from Spanish.")
        nlpobject = nlpes(text)

    translation = ""
    number_of_sentences = len(list(nlpobject.sents))
    counter=0
    source_text=""
    translated_text=""

    # Because the particular API has a limit of 20K characters at once, we need to split the text into chunks.
    for i in nlpobject.sents:
        counter+=1
        print("Translating sentence {} of {} sentences.".format(
            counter, number_of_sentences), end ='\r')
        # test if number is event
        if(counter%4!=0):
            source_text = source_text + i.text + "\n"
            continue
        print("Sending request to Azure.                                 ", end ='\r')
        # print(source_text)
        # Pass the text to the translation service and return it
        body = [{
            'text': source_text
        }]
        source_text=""
        request = requests.post(
            constructed_url, params=params, headers=headers, json=body)
        # parsed=json.loads(request.text)
        # print(json.dumps(request.text, indent=4, sort_keys=True))
        translated_text = translated_text+request.json()[0]["translations"][0]["text"] + ".\n"
    return nlpobject, translated_text, nlpes(translated_text)

# Extract the significant words from the text


def isolate_words(text):
    # Extract all the significant words from the source English text
    keywords = {}
    if text.lang_ == "en":
        stopwords = list(spacy.lang.en.stop_words.STOP_WORDS)
    elif text.lang_ == "fr":
        stopwords = list(spacy.lang.fr.stop_words.STOP_WORDS)
    else:
        stopwords = list(spacy.lang.es.stop_words.STOP_WORDS)
    pos_tag = ['VERB', 'NOUN', 'ADV', 'ADJ']
    for token in text:
        if(token.text in stopwords or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            if (token.lemma_ in keywords.keys()):
                keywords[token.lemma_] = keywords[token.lemma_]+1
            else:
                keywords[token.lemma_] = 1
    return keywords


# Set up the Microsoft Translation boiler plate
# Taken from Translation services example
# **************************************************
# Add your subscription key and endpoint
subscription_key = "c3e034153d3f4842bd4db3886b75e5b2"
endpoint = "https://api.cognitive.microsofttranslator.com/"

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
print("Loading language files...")
nlpen = spacy.load("en_core_web_lg")
nlpfr = fr_core_news_lg.load()
nlpes = es_core_news_lg.load()

# Get the pages
print("Retrieving web pages...")
# english = get_webpage_text("https://www.canada.ca/en/department-national-defence/corporate/policies-standards/defence-administrative-orders-directives/1000-series/1002/1002-1-requests-under-privacy-act-personal-information.html")
# french = get_webpage_text("https://www.canada.ca/fr/ministere-defense-nationale/organisation/politiques-normes/directives-ordonnances-administratives-defense/serie-1000/1002/1002-1-demandes-de-renseignements-personnels-vertu-loi-protection-des-renseignements-personnels.html")

# sys.exit()
# english=get_webpage_text("https://www.tbs-sct.gc.ca/agreements-conventions/view-visualiser-eng.aspx?id=10")
# french=get_webpage_text("https://www.tbs-sct.gc.ca/agreements-conventions/view-visualiser-fra.aspx?id=10")

english=get_webpage_text("https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/ukraine-measures.html")
french=get_webpage_text("https://www.canada.ca/fr/immigration-refugies-citoyennete/services/immigrer-canada/mesures-ukraine.html")
# Translate them
print("Translating...")
source_english_nlp_object, english_translated_text, english_translated_language_object = get_translation(
    english, "en")
source_french_nlp_object, french_translated_text, french_translated_language_object = get_translation(
    french, "fr")

# Parse all texts in the language parser
original_french_keywords = isolate_words(source_french_nlp_object)
original_english_keywords = isolate_words(source_english_nlp_object)
translation_from_english_keywords = isolate_words(
    english_translated_language_object)
translation_from_french_keywords = isolate_words(
    french_translated_language_object)


words_in_common = set(translation_from_french_keywords.keys()).intersection(
    set(translation_from_english_keywords.keys()))

french_frequency_greater_than_one =  dict(filter(lambda val: val[1] > 1, translation_from_french_keywords.items()))
english_frequency_greater_than_one =  dict(filter(lambda val: val[1] > 1, translation_from_english_keywords.items()))

extra_words=set(french_frequency_greater_than_one.keys()).difference(set(english_frequency_greater_than_one.keys()))

extra_score=0
for i in extra_words:
    if i in translation_from_english_keywords.keys():
        continue
    else:
        for j in translation_from_french_keywords.keys():
            # print(i,j)
            if nlpes(i).similarity(nlpes(j))>0.2:
                extra_score+0.8
print("Extra score: ",extra_score)
print("How many words in the original English", len(original_english_keywords))
print("How many words in the original French", len(original_french_keywords))
print("How many words in the English translation",
      len(translation_from_english_keywords))
print("How many words in the French Translation",
      len(translation_from_french_keywords))
print("How many words shared between  translations.", len(words_in_common))

# similarity score is the comparison value multiplied by 2 and divided by the total number of keywords for French and English source.
print("Bag of words simularity: %5.2f" % (((len(words_in_common)*2+extra_score) /
      (len(translation_from_english_keywords)+len(translation_from_french_keywords)))*100))
print("Vector simularity: %5.2f" %
      (french_translated_language_object.similarity(english_translated_language_object)))

# Open a file and save some diagnostic data
f = open("translation_summary.txt", "w")
f.write("English source text: \n****************************************************************\n")
f.write(english + "\n\n\n")

f.write("French source text: \n****************************************************************\n")
f.write(french + "\n\n\n")

f.write("English Translated text: \n****************************************************************\n")
f.write(english_translated_text + "\n\n\n")

f.write("French translated text: \n****************************************************************\n")
f.write(french_translated_text + "\n\n\n")

# Write the sorted word lists
f.write("Original English\n")
for i, j in sorted(original_english_keywords.items(), key=lambda item: item[1], reverse=True):
    f.write(str(j)+" " + i+"\n")

f.write("\n\n\n\nTranslated to Spanish\n")
for i, j in sorted(translation_from_english_keywords.items(), key=lambda item: item[1], reverse=True):
    f.write(str(j)+" " + i+"\n")

f.write("\n\n\n\Original French\n")
for i, j in sorted(original_french_keywords.items(), key=lambda item: item[1], reverse=True):
    f.write(str(j)+" " + i+"\n")

f.write("\n\n\n\Translated to Spanish\n")
for i, j in sorted(translation_from_french_keywords.items(), key=lambda item: item[1], reverse=True):
    f.write(str(j)+" " + i+"\n")

f.close()
