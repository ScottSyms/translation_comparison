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

# On Premises Translation support libraries
from transformers import MarianMTModel, MarianTokenizer
from transformers import  MarianTokenizer

#ONNX support libraries
from core.marian import MarianOnnx


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

class localtranslate():
    def __init__(self, webpageobject):
        if torch.cuda.is_available():  
            self.dev = "cuda"
            print("Using CUDA")
        else:  
            self.dev = "cpu" 
            print("Using CPU")
        self.device = torch.device(self.dev)

        # Initialize empty dictionaries for on prem tokenizer and model
        self.model={}
        self.tokenizer={}

        lt = LineTokenizer()
        batch_size = 8

        # Capture the current text in a language bucket
        print("Page language: ", webpageobject.LANG)
        # webpageobject.version[webpageobject.LANG]=webpageobject.pagetext
        webpageobject.nlpobject[webpageobject.LANG]=webpageobject.nlpmodel[webpageobject.LANG](webpageobject.pagetext)
        webpageobject.version[webpageobject.LANG]=" ".join([token.lemma_ for token in webpageobject.nlpmodel[webpageobject.LANG](webpageobject.pagetext)])


        # Languages other then the sample are our translation targets.
        targetlanguages = [x for x in ["fr", "en", "es"] if webpageobject.LANG != x]
        print("Translating to: ", targetlanguages)

        # Iterate through the language targets and translate
        for targetlanguage in targetlanguages:
            # Set up the model for translation. This depends upon the structured naming convention
            # for the Hugging Face models, eg/ Helsinki-NLP/opus-mt- followed by the source language, 
            # a hyphen and then a target language.
            translation_required = "./outs/" + webpageobject.LANG + "-" + targetlanguage

            print("Translating with " + translation_required)
            tokenizer = MarianTokenizer.from_pretrained(translation_required)
            # model = MarianMTModel.from_pretrained(translation_required)
            model = MarianOnnx(translation_required, device=self.dev)
            # model.to(self.device)

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
                    # model_inputs = tokenizer(sent_batch, return_tensors="pt", padding=True, truncation=True, max_length=500).to(self.device)
                    input_ids = tokenizer(sent_batch, return_tensors='pt', padding=True).to(self.device)
                    # with torch.no_grad():
                        # translated_batch = model.generate(**model_inputs)
                    tokens = model.generate(**input_ids)
                    # translated += translated_batch

                # translated = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
                translated=tokenizer.batch_decode(tokens, skip_special_tokens=True)
                translated_paragraphs += [" ".join(translated)]
            print("Finished translation")
            webpageobject.version[targetlanguage] = "\n".join(translated_paragraphs)
            webpageobject.nlpobject[targetlanguage]=webpageobject.nlpmodel[targetlanguage](webpageobject.version[targetlanguage])

            print("Lemmatising translation")
            webpageobject.version[targetlanguage] = " ".join([token.lemma_ for token in webpageobject.nlpobject[targetlanguage]])
            

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
    