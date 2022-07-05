#!/usr/bin/env python

# Some code borrowed from 
# https://stackoverflow.com/questions/68185061/strange-results-with-huggingface-transformermarianmt-translation-of-larger-tex

# Supress warnings
import warnings
warnings.filterwarnings("ignore")

# Pedestrian imports
import requests
import re
import sys
import os
import uuid
import json
import math

# For hosting keys in a separate file
from dotenv import load_dotenv

# XML handling imports
# from string import punctuation
from bs4 import BeautifulSoup

# NLP like imports
import spacy
import fr_core_news_lg
import es_core_news_lg
from nltk.tokenize import sent_tokenize
from nltk.tokenize import LineTokenizer
import torch

# Bert comparisons
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# On Premises Translation 
from transformers import MarianMTModel, MarianTokenizer

class webpage():
    def __init__(self, URL, LANG):
        self.LANG=LANG

        try:
            page = requests.get(URL)
        except:
            print("Error: Could not retrieve the page")
            sys.exit(1)

        # Some globals
        self.nlpmodel={}
        self.nlpobject={}
        self.nlpfrench=""
        self.nlpenglish=""
        self.nlpspanish=""
        self.version={}        

        # extract the text from the pages
        page = BeautifulSoup(
            page.content, features="lxml").get_text(separator=" ")
        
        # Strip off excess line endings
        self.pagetext=re.sub(r'\n+[ \n]*', '\n', page)

        # Restrict to ASCII characters
        self.pagetext=self.pagetext.encode("ascii", errors="ignore").decode()

        # We use SpaCy to do some local processing of the text
        # Load the language token lists
        print("Loading language files...")
        self.nlpmodel["en"] = spacy.load("en_core_web_lg")  # English
        self.nlpmodel["fr"] = fr_core_news_lg.load()        # French
        self.nlpmodel["es"] = es_core_news_lg.load()        # Spanish
        

        # Return SpaCy language object
        self.nlpobject[LANG]=self.nlpmodel[LANG](self.pagetext)
        

class azuretranslate():
    # This code hasn't been updated to match  and won't likely work.

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
        if webpageobject.LANG == "en":
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
        if torch.cuda.is_available():  
            self.dev = "cuda"
        else:  
            self.dev = "cpu" 
        self.device = torch.device(self.dev)

        # Initialize empty dictionaries for on prem tokenizer and model
        self.model={}
        self.tokenizer={}

        lt = LineTokenizer()
        batch_size = 8

        # Capture the current text in a language bucket
        print("SOURCE LANGUAGE: ", webpageobject.LANG)
        webpageobject.version[webpageobject.LANG]=webpageobject.pagetext
        webpageobject.nlpobject[webpageobject.LANG]=webpageobject.nlpmodel[webpageobject.LANG](webpageobject.pagetext)

        # Languages other then the sample are our translation targets.
        targetlanguages = [x for x in ["fr", "en", "es"] if webpageobject.LANG != x]
        print("TARGET LANGUAGES: ", targetlanguages)

        # Iterate through the language targets and translate
        for targetlanguage in targetlanguages:
            # Set up the model for translation. This depends upon the structured naming convention
            # for the Hugging Face models, eg/ Helsinki-NLP/opus-mt- followed by the source language, 
            # a hyphen and then a target language.
            translation_required = "Helsinki-NLP/opus-mt-" + webpageobject.LANG + "-" + targetlanguage

            print("Translating with " + translation_required)
            tokenizer = MarianTokenizer.from_pretrained(translation_required)
            model = MarianMTModel.from_pretrained(translation_required)
            model.to(self.device)

            # Break up the data into digestable bits
            # The local translation doesn't like source text greater than 512 words.
            paragraphs = lt.tokenize(webpageobject.pagetext)   
            translated_paragraphs = []

            for paragraph in paragraphs:
                sentences = sent_tokenize(paragraph)
                batches = math.ceil(len(sentences) / batch_size)     
                translated = []
                for i in range(batches):
                    sent_batch = sentences[i*batch_size:(i+1)*batch_size]
                    model_inputs = tokenizer(sent_batch, return_tensors="pt", padding=True, truncation=True, max_length=500).to(self.device)
                    with torch.no_grad():
                        translated_batch = model.generate(**model_inputs)
                    translated += translated_batch
                translated = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
                translated_paragraphs += [" ".join(translated)]
            webpageobject.version[targetlanguage] = "\n".join(translated_paragraphs)
            webpageobject.nlpobject[targetlanguage]=webpageobject.nlpmodel[targetlanguage](webpageobject.version[targetlanguage])
            
            

class textcompare():
    def __init__(self, firstobject, secondobject):
        # Instantiate BERT multilingual transformor
        self.bert = SentenceTransformer('distiluse-base-multilingual-cased-v1')

        self.englishcompare=firstobject.nlpobject['en'].similarity(secondobject.nlpobject['en'])
        self.frenchcompare=firstobject.nlpobject['fr'].similarity(secondobject.nlpobject['fr'])
        self.spanishcompare=firstobject.nlpobject['es'].similarity(secondobject.nlpobject['es'])

        self.bertenglish1 = self.bert.encode([firstobject.version['en']])
        self.bertfrench1 = self.bert.encode([firstobject.version['fr']])
        self.bertspanish1 = self.bert.encode([firstobject.version['es']])

        self.bertenglish2 = self.bert.encode([secondobject.version['en']])
        self.bertfrench2 = self.bert.encode([secondobject.version['fr']])
        self.bertspanish2 = self.bert.encode([secondobject.version['es']])
            
        print("SpaCy French similarity score: %6.2f" % self.frenchcompare)
        print("SpaCy English similarity score: %6.2f" % self.englishcompare)
        print("SpaCy Spanish similarity score: %6.2f" % self.spanishcompare)

        bertfrench=cosine_similarity(self.bertfrench1, self.bertfrench2)[0][0]
        bertenglish=cosine_similarity(self.bertenglish1, self.bertenglish2)[0][0]
        bertspanish=cosine_similarity(self.bertspanish1, self.bertspanish2)[0][0]

        print("BERT French similarity score: %6.2f" % bertfrench)
        print("BERT English similarity score:  %6.2f" % bertenglish)
        print("BERT Spanish similarity score:  %6.2f" % bertspanish)
    