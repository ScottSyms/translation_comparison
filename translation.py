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


# ****************************************************************
# TODO
# Format numbers in the comparisons, ie/ fixed digits after the decimal point
# Clean out commented tests
# Save files and translation to disk for auditing.

class Compare():
    def __init__(self):
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

        # We use SpaCy to do some local processing of the text
        # Load the language token lists
        print("Loading language files...")
        self.nlpen = spacy.load("en_core_web_lg")  # English
        self.nlpfr = fr_core_news_lg.load()  # French
        self.nlpes = es_core_news_lg.load()  # Spanish

        # Initialize the translation dictionary
        self.translations = {}
        template = {"url": "",
                    "text": "",
                    "language": "",
                    "object": "",
                    "keywords": {},
                    "complement_text": "",
                    "complement_language": "",
                    "complement_object": "",
                    "complement_keywords": {},
                    "third_text": "",
                    "third_language": "",
                    "third_object": "",
                    "third_keywords": {}}

        self.translations[0] = template
        self.translations[1] = template

        # Instantiate BERT multilingual transformor
        self.bert = SentenceTransformer('distiluse-base-multilingual-cased-v1')

    def comparepages(self, url1, language1, url2, language2):
        self.url1 = url1
        self.language1 = language1
        self.url2 = url2
        self.language2 = language2

        self.translations[0] = {"url": self.url1, "text": self.get_webpage_text(
            self.url1), "language": self.language1}
        self.translations[1] = {"url": self.url2, "text": self.get_webpage_text(
            self.url2), "language": self.language2}

        for i in self.translations:
            self.translations[i]["complement_text"], \
                self.translations[i]["object"], \
                self.translations[i]["complement_object"], \
                self.translations[i]["complement_language"] \
                = self.get_translation(
                self.translations[i]["text"],
                self.translations[i]["language"],
                self.complement_language(self.translations[i]["language"]))

            self.translations[i]["third_text"], \
                self.translations[i]["object"], \
                self.translations[i]["third_object"], \
                self.translations[i]["third_language"] \
                = self.get_translation(
                self.translations[i]["text"],
                self.translations[i]["language"],
                "es")

            self.translations[i]["keywords"] = self.isolate_words(
                self.translations[i]["object"])
            self.translations[i]["complement_keywords"] = self.isolate_words(
                self.translations[i]["complement_object"])
            self.translations[i]["third_keywords"] = self.isolate_words(
                self.translations[i]["third_object"])

    def complement_language(self, language):
        if language == "en":
            return "fr"
        elif language == "fr":
            return "en"

    # Retrieve a web page
    def get_webpage_text(self, url):
        try:
            page = requests.get(url)
        except:
            print("Error: Could not retrieve the page")
            sys.exit(1)

        # extract the text from the pages
        page = BeautifulSoup(
            page.content, features="lxml").get_text(separator=" ")
        # Strip off excess line endings
        return re.sub(r'\n+', '\n', page)

    # Return language object
    def language_object(self, text, source_language):
        if source_language == "en":
            nlpobject = self.nlpen(text)
        elif source_language == "fr":
            nlpobject = self.nlpfr(text)
        else:
            nlpobject = self.nlpes(text)
        return nlpobject

    def get_translation(self, text, source_language, output_language):
        print("\n\nText is {} characters.".format(len(text)))
        # Translate the French page into Spanish
        params = {
            'api-version': '3.0',
            'from': source_language,
            'to': [output_language]
        }
        nlpobject = self.language_object(text, source_language)

        translation = ""
        number_of_sentences = len(list(nlpobject.sents))
        counter = 0
        source_text = ""
        translated_text = ""

        # Because the particular API has a limit of 20K characters at once, we need to split the text into chunks.
        for i in nlpobject.sents:
            counter += 1
            print("Translating sentence {} of {} sentences.                     ".format(
                counter, number_of_sentences), end='\r')
            # test if number is event
            if(counter % 4 != 0):
                source_text = source_text + i.text + "\n"
                continue
            # print("Sending request to Azure.", end='\n')
            # print(source_text)
            # Pass the text to the translation service and return it
            body = [{
                'text': source_text
            }]
            source_text = ""
            request = requests.post(
                self.constructed_url, params=params, headers=self.headers, json=body)
            # parsed=json.loads(request.text)
            # print("Parsed translation: ", json.dumps(request.text, indent=4, sort_keys=True))
            translated_text = translated_text + \
                request.json()[0]["translations"][0]["text"] + ".\n"
        return translated_text, nlpobject, self.language_object(translated_text, output_language), output_language

    # Extract the significant words from the text
    def isolate_words(self, text):
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

    # Extract the significant words from the text

    def clean_text(self, text, language):
        # Extract all the significant words from the source English text
        return_text = ""
        if language == "en":
            stopwords = list(spacy.lang.en.stop_words.STOP_WORDS)
        elif language == "fr":
            stopwords = list(spacy.lang.fr.stop_words.STOP_WORDS)
        else:
            stopwords = list(spacy.lang.es.stop_words.STOP_WORDS)
        pos_tag = ['VERB', 'NOUN', 'ADV', 'ADJ']
        for token in text:
            if(token.text in stopwords or token.text in punctuation):
                continue
            if(token.pos_ in pos_tag):
                return_text = return_text + " " + token.lemma_
        return return_text

    def bag_of_words(self, language1_keywords, language2_keywords, language):
        words_in_common = set(language1_keywords.keys()).intersection(
            set(language2_keywords.keys()))
        language1_frequency_greater_than_one = dict(
            filter(lambda val: val[1] > 1, language1_keywords.items()))
        language2_frequency_greater_than_one = dict(
            filter(lambda val: val[1] > 1, language2_keywords.items()))
        return ((len(words_in_common)/(len(language1_keywords) + len(language2_keywords)))*100)

    def gut_text(self):
        for i in range(len(self.translations)):
            for j in ["", "complement_", "third_"]:
                self.translations[i][j+"text"] = self.clean_text(
                    self.translations[i][j+"object"], self.translations[i][j+"language"])

    def crosstranslationsimularity(self):
        return (self.translations[0]["object"].similarity(self.translations[1]["complement_object"]) +
                self.translations[1]["object"].similarity(self.translations[0]["complement_object"])) / 2

    def thirdpartysimularity(self):
        return self.translations[0]["third_object"].similarity(self.translations[1]["third_object"])

    def bowcrosstranslationsimularity(self):
        return (self.bag_of_words(self.translations[0]["keywords"], self.translations[1]["complement_keywords"], self.translations[0]["language"]) +
                self.bag_of_words(self.translations[1]["keywords"], self.translations[0]["complement_keywords"], self.translations[0]["language"])) / (len(self.translations[0]["keywords"]) + len(self.translations[1]["keywords"]))

    def bowthirdpartysimularity(self):
        return self.bag_of_words(self.translations[0]["third_keywords"], self.translations[1]["third_keywords"], "es")

    def bertsimularity(self):
        language1 = self.bert.encode([self.translations[0]["text"]])
        language2 = self.bert.encode([self.translations[1]["text"]])
        return cosine_similarity(language1, language2)[0][0]

    def bertcrosssimularity(self):
        language1 = self.bert.encode([self.translations[0]["text"]])
        language2 = self.bert.encode([self.translations[1]["text"]])
        language3 = self.bert.encode([self.translations[0]["complement_text"]])
        language4 = self.bert.encode([self.translations[1]["complement_text"]])
        return (cosine_similarity(language1, language4)[0][0] + cosine_similarity(language2, language3)[0][0])/2

    def bert3rdsimularity(self):
        language1 = self.bert.encode([self.translations[0]["third_text"]])
        language2 = self.bert.encode([self.translations[1]["third_text"]])
        return cosine_similarity(language1, language2)[0][0]


if __name__ == '__main__':
    f = Compare()

    testitems = [["https://en.wikipedia.org/wiki/Volodymyr_Zelenskyy", "en", "https://fr.wikipedia.org/wiki/Volodymyr_Zelenskyy", "fr"],
                 ["https://en.wikipedia.org/wiki/Julius_Caesar", "en",
                     "https://fr.wikipedia.org/wiki/Jules_C%C3%A9sar", "fr"],
                 ["https://en.wikipedia.org/wiki/Luge", "en",
                     "https://fr.wikipedia.org/wiki/Luge_de_course", "fr"],
                 ["https://en.wikipedia.org/wiki/Charles_de_Gaulle", "en",
                     "https://fr.wikipedia.org/wiki/Charles_de_Gaulle", "fr"],
                 ["https://en.wikipedia.org/wiki/Charles_de_Gaulle", "en",
                     "https://fr.wikipedia.org/wiki/Luge_de_course", "fr"],
                 ]

    # testitems = [
    #             ["https://en.wikipedia.org/wiki/Charles_de_Gaulle","en", "https://fr.wikipedia.org/wiki/Charles_de_Gaulle", "fr"],
    #             ]

    # testitems = [
    #             ["https://en.wikipedia.org/wiki/Charles_de_Gaulle","en", "https://fr.wikipedia.org/wiki/Luge_de_course", "fr"],
    #             ]

    # Short test article
    # testitems = [[
    #     "https://en.wikipedia.org/wiki/Engelbert_Humperdinck_(composer)", "en", "https://fr.wikipedia.org/wiki/Engelbert_Humperdinck", "fr"]]

    for i in testitems:
        f.comparepages(i[0], i[1], i[2], i[3])
        f.gut_text()
        print(
            "\n\nThe similarity scores between {} and {} are...".format(i[0], i[2]))
        print("Cross translation cosine similarity score",
              f.crosstranslationsimularity())
        print("Third language  cosine similarity score", f.thirdpartysimularity())
        print("Raw language BERT cosine similarity score", f.bertsimularity())
        print("Cross translation language BERT cosine similarity score",
              f.bertcrosssimularity())
        print("Third language BERT cosine similarity score", f.bert3rdsimularity())

        # print("Bag of Words/ Cross translation similarity score", f.bowcrosstranslationsimularity())
        # print("Bag of Words/ third language translation similarity score", f.bowthirdpartysimularity())
