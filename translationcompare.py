#!/usr/bin/env python

# Module imports
import warnings

# Supress warnings
warnings.filterwarnings("ignore")

import requests
import re
import sys
import pprint
import os
import uuid
import json
from dotenv import load_dotenv
import spacy
from string import punctuation
from bs4 import BeautifulSoup
import fr_core_news_lg
import es_core_news_lg

# Bert comparisons
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# On Premises Translation 
from transformers import MarianTokenizer, AutoModelForSeq2SeqLM

print("test")

class translator():
    def __init__():
        pass

class webpage():
    def __init__(self, URL, LANG):
        self.LANG=LANG

        try:
            page = requests.get(URL)
        except:
            print("Error: Could not retrieve the page")
            sys.exit(1)

        # Some globals
        self.french=""
        self.english=""
        self.spanish=""
        self.nlpfrench=""
        self.nlpenglish=""
        self.nlpspanish=""        

        # extract the text from the pages
        page = BeautifulSoup(
            page.content, features="lxml").get_text(separator=" ")
        # Strip off excess line endings
        self.pagetext=re.sub(r'\n+[ \n]*', '\n', page)

        # We use SpaCy to do some local processing of the text
        # Load the language token lists
        print("Loading language files...")
        self.nlpen = spacy.load("en_core_web_lg")  # English
        self.nlpfr = fr_core_news_lg.load()  # French
        self.nlpes = es_core_news_lg.load()  # Spanish

            # Return language object
        if LANG == "ENGLISH":
            self.nlpobject = self.nlpen(self.pagetext)
        elif LANG == "FRENCH":
            self.nlpobject = self.nlpfr(self.pagetext)
        else:
           self.nlpobject = self.nlpes(self.pagetext)

class azuretranslate():
    def __init__(self, webpageobject):
        webpageobject.french = ""
        webpageobject.english = ""
        webpageobject.spanish = ""

        # Set up the Microsoft Translation boiler plate
        # Taken from Translation services example
        # **************************************************

        # Load the secret key for the translation service from a .env file
        load_dotenv()
        subscription_key = os.getenv("AZURE_TRANSLATION_KEY")

        # End point for the translation service
        endpoint = "https://api.cognitive.microsofttranslator.com/"

        # Add your location, also known as region. The default is global.
        # This is required if using a Cognitive Services resource.
        self.location = "canadacentral"

        # Construct the endpoint URL and POST headers
        path = '/translate'
        self.constructed_url = endpoint + path

        self.headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        # Initialize empty dictionaries for on prem tokenizer and model
        self.model={}
        self.tokenizer={}


        # Instantiate models and tokenizers
        if webpageobject.LANG == "ENGLISH":
            webpageobject.english=webpageobject.pagetext
            webpageobject.nlpenglish=webpageobject.nlpes(webpageobject.pagetext)

            # English to French
            print("Translating English to French")
            params = { 'api-version': '3.0', 'from': 'en', 'to': ["fr"] }
            for i in webpageobject.pagetext.split("."):
                body = [{'text': i }]
                request = requests.post(self.constructed_url, params=params, headers=self.headers, json=body)
                webpageobject.french=webpageobject.french + request.json()[0]["translations"][0]["text"] + ".\n"
            webpageobject.nlpfrench=webpageobject.nlpfr(webpageobject.french)

            # English to Spanish
            print("Translating English to Spanish")
            params = { 'api-version': '3.0', 'from': 'en', 'to': ["es"] }
            for i in webpageobject.pagetext.split("."):
                body = [{'text': i }]
                request = requests.post(self.constructed_url, params=params, headers=self.headers, json=body)
                webpageobject.spanish=webpageobject.spanish + request.json()[0]["translations"][0]["text"] + ".\n"
            webpageobject.nlpspanish=webpageobject.nlpes(webpageobject.spanish)

        else:
            # French to English
            print("Translating French to English")
            params = { 'api-version': '3.0', 'from': 'fr', 'to': ["en"] }
            for i in webpageobject.pagetext.split("."):
                body = [{'text': i }]
                request = requests.post(self.constructed_url, params=params, headers=self.headers, json=body)
                webpageobject.english=webpageobject.english + request.json()[0]["translations"][0]["text"] + ".\n"
            webpageobject.nlpenglish=webpageobject.nlpen(webpageobject.english)

            #  French to Spanish tokenizer and model
            print("Translating French to Spanish")
            params = { 'api-version': '3.0', 'from': 'fr', 'to': ["en"] }
            for i in webpageobject.pagetext.split("."):
                body = [{'text': i }]
                request = requests.post(self.constructed_url, params=params, headers=self.headers, json=body)
                webpageobject.spanish=webpageobject.spanish + request.json()[0]["translations"][0]["text"] + ".\n"
            webpageobject.nlpspanish=webpageobject.nlpes(webpageobject.spanish)


class localtranslate():
    def __init__(self, webpageobject):

        # Download the on-premises translation models
        enfr = 'Helsinki-NLP/opus-mt-en-fr'
        fren = 'Helsinki-NLP/opus-mt-fr-en'
        enes = 'Helsinki-NLP/opus-mt-en-es'
        fres = 'Helsinki-NLP/opus-mt-fr-es'

        # Initialize empty dictionaries for on prem tokenizer and model
        self.model={}
        self.tokenizer={}

        # Instantiate models and tokenizers
        if webpageobject.LANG == "ENGLISH":
            webpageobject.english=webpageobject.pagetext
            webpageobject.nlpenglish=webpageobject.nlpen(webpageobject.pagetext)

            # English to French
            print("Translating English to French")
            self.tokenizer["ENGLISHFRENCH"] = MarianTokenizer.from_pretrained(enfr)
            self.model["ENGLISHFRENCH"] = AutoModelForSeq2SeqLM.from_pretrained(enfr)
            for i in webpageobject.pagetext.split("."):
                webpageobject.french=webpageobject.french + self.translate(i, "ENGLISHFRENCH")
            webpageobject.nlpfrench=webpageobject.nlpfr(webpageobject.french)


            # English to Spanish
            print("Translating English to Spanish")
            self.tokenizer["ENGLISHSPANISH"] = MarianTokenizer.from_pretrained(enes)
            self.model["ENGLISHSPANISH"] = AutoModelForSeq2SeqLM.from_pretrained(enes)
            for i in webpageobject.pagetext.split("."):
                webpageobject.spanish=webpageobject.spanish + self.translate(i, "ENGLISHSPANISH")
            webpageobject.nlpspanish=webpageobject.nlpes(webpageobject.spanish)

        else:
            webpageobject.french=webpageobject.pagetext
            webpageobject.nlpfrench=webpageobject.nlpfr(webpageobject.pagetext)

            # French to English
            print("Translating French to English")
            self.tokenizer["FRENCHENGLISH"] = MarianTokenizer.from_pretrained(fren)
            self.model["FRENCHENGLISH"] = AutoModelForSeq2SeqLM.from_pretrained(fren)
            for i in webpageobject.pagetext.split("."):
                webpageobject.english=webpageobject.english + self.translate(i, "FRENCHENGLISH")
            webpageobject.nlpenglish=webpageobject.nlpen(webpageobject.english)

            
            #  French to Spanish tokenizer and model
            print("Translating French to Spanish")
            self.tokenizer["FRENCHSPANISH"] = MarianTokenizer.from_pretrained(fres)
            self.model["FRENCHSPANISH"] = AutoModelForSeq2SeqLM.from_pretrained(fres)
            for i in webpageobject.pagetext.split("."):
                webpageobject.spanish=webpageobject.spanish + self.translate(i, "FRENCHSPANISH")
            webpageobject.nlpspanish=webpageobject.nlpes(webpageobject.spanish)


    def translate(self, TEXT, LANGVECTOR):
        input_ids = self.tokenizer[LANGVECTOR].encode(TEXT, return_tensors="pt")
        outputs = self.model[LANGVECTOR].generate(input_ids)
        return self.tokenizer[LANGVECTOR].decode(outputs[0], skip_special_tokens=True)


class textcompare():
    def __init__(self, firstobject, secondobject):
        # Instantiate BERT multilingual transformor
        self.bert = SentenceTransformer('distiluse-base-multilingual-cased-v1')

        self.englishcompare=firstobject.nlpenglish.similarity(secondobject.nlpenglish)*100
        self.frenchcompare=firstobject.nlpfrench.similarity(secondobject.nlpfrench)*100
        self.spanishcompare=firstobject.nlpspanish.similarity(secondobject.nlpspanish)*100

        self.bertenglish1 = self.bert.encode([firstobject.english])
        self.bertfrench1 = self.bert.encode([firstobject.french])
        self.bertspanish1 = self.bert.encode([firstobject.spanish])

        self.bertenglish2 = self.bert.encode([firstobject.english])
        self.bertfrench2 = self.bert.encode([firstobject.french])
        self.bertspanish2 = self.bert.encode([firstobject.spanish])
            
        print("SpaCy French similarity score: %6.2f" % self.frenchcompare)
        print("SpaCy English similarity score: %6.2f" % self.englishcompare)
        print("SpaCy Spanish similarity score: %6.2f" % self.spanishcompare)

        bertfrench=float(cosine_similarity(self.bertfrench1, self.bertfrench2)[0][0]) * 100
        bertenglish=float(cosine_similarity(self.bertenglish1, self.bertenglish2)[0][0]) * 100
        bertspanish=float(cosine_similarity(self.bertspanish1, self.bertspanish2)[0][0]) *100

        print("BERT French similarity score: %6.2f" % bertfrench)
        print("BERT English similarity score:  %6.2f" % bertenglish)
        print("BERT Spanish similarity score:  %6.2f" % bertspanish)
    



# ****************************************************************
# TODO
# Format numbers in the comparisons, ie/ fixed digits after the decimal point
# Clean out commented tests
# Save files and translation to disk for auditing