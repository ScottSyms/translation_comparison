# from cgitb import text
# from gettext import translation
# from webbrowser import get
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


class compareTranslations():
    def __init__(self):
        # Set up the Microsoft Translation boiler plate
        # Taken from Translation services example
        # **************************************************

        # Load the environment variables from a .env file
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
        template={"url": "", 
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

    def loadpages(self, url1, language1, url2, language2):
        self.url1 = url1
        self.language1 = language1
        self.url2 = url2
        self.language2 = language2

        self.translations[0] = {"url": self.url1, "text": self.get_webpage_text(
            self.url1), "language": self.language1}
        self.translations[1] = {"url": self.url2, "text": self.get_webpage_text(
            self.url2), "language": self.language2}

        for i in self.translations:
            self.translations[i]["complement"], \
            self.translations[i]["object"], \
            self.translations[i]["complement_object"], \
            self.translations[i]["complement_language"] \
            = self.get_translation( \
                self.translations[i]["text"], \
                self.translations[i]["language"], \
                self.complement_language(self.translations[i]["language"]))


            self.translations[i]["third_text"], \
            self.translations[i]["object"], \
            self.translations[i]["third_object"], \
            self.translations[i]["third_language"] \
            = self.get_translation( \
                self.translations[i]["text"], \
                self.translations[i]["language"], \
                "es")

            self.translations[i]["keywords"] = self.isolate_words(self.translations[i]["object"])
            self.translations[i]["complement_keywords"] = self.isolate_words(self.translations[i]["complement_object"])
            self.translations[i]["third_keywords"] = self.isolate_words(self.translations[i]["third_object"])

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
        page = BeautifulSoup(page.content, features="lxml").get_text(separator=" ")
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
        print("Text is {} characters.".format(len(text)))
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
            print("Translating sentence {} of {} sentences.".format(
                counter, number_of_sentences), end='\r')
            # test if number is event
            if(counter % 4 != 0):
                source_text = source_text + i.text + "\n"
                continue
            print("Sending request to Azure.                                 ", end='\r')
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

    def bag_of_words(self, language1_keywords, language2_keywords, marginal_threshold, language):

        words_in_common = set(language1_keywords.keys()).intersection(
        set(language2_keywords.keys()))

        language1_frequency_greater_than_one =  dict(filter(lambda val: val[1] > 1, language1_keywords.items()))
        language2_frequency_greater_than_one =  dict(filter(lambda val: val[1] > 1, language2_keywords.items()))

        # # See if we can squeeze out some marginal value from close vector matches
        # extra_words=set(language1_frequency_greater_than_one.keys()).difference(set(language2_frequency_greater_than_one.keys()))
        
        # nlpobject = self.language_object(text, language)

        # extra_score=0
        # for i in extra_words:
        #     if i in language1_keywords.keys():
        #         continue
        #     else:
        #         for j in language2_keywords.keys():
        #             # print(i,j)
        #             if nlpobject(i).similarity(nlpobject(j))>marginal_threshold:
        #                 extra_score+0.8
        return (len(words_in_common)/(len(language1_keywords) +len(language2_keywords)))*100

    def crosstranslationsimularity(self):
        return (self.translations[0]["object"].similarity(self.translations[1]["complement_object"]) + \
            self.translations[1]["object"].similarity(self.translations[0]["complement_object"])) / 2

    def thirdpartysimularity(self):
        return self.translations[0]["third_object"].similarity(self.translations[1]["third_object"])

    def bowcrosstranslationsimularity(self):
        return (self.bag_of_words(self.translations[0]["keywords"], self.translations[1]["complement_keywords"], 0.5, self.translations[0]["language"]) + \
            self.bag_of_words(self.translations[1]["keywords"], self.translations[0]["complement_keywords"], 0.5, self.translations[0]["language"])) / 2

    def bowthirdpartysimularity(self):
        return self.bag_of_words(self.translations[0]["third_keywords"], self.translations[1]["third_keywords"], 0.5, "es")

if __name__ == '__main__':
    f = compareTranslations("https://www.canada.ca/en/canadian-heritage.html",
                            "en", "https://www.canada.ca/fr/patrimoine-canadien.html", "fr")
    pprint.pprint(f.translations[0]["url"])


# # Translate text from source language to Spanish





# # Get the pages
# print("Retrieving web pages...")
# english = get_webpage_text("https://www.canada.ca/en/department-national-defence/corporate/policies-standards/defence-administrative-orders-directives/1000-series/1002/1002-1-requests-under-privacy-act-personal-information.html")
# french = get_webpage_text("https://www.canada.ca/fr/ministere-defense-nationale/organisation/politiques-normes/directives-ordonnances-administratives-defense/serie-1000/1002/1002-1-demandes-de-renseignements-personnels-vertu-loi-protection-des-renseignements-personnels.html")

# # sys.exit()
# # english=get_webpage_text("https://www.tbs-sct.gc.ca/agreements-conventions/view-visualiser-eng.aspx?id=10")
# # french=get_webpage_text("https://www.tbs-sct.gc.ca/agreements-conventions/view-visualiser-fra.aspx?id=10")

# # english=get_webpage_text("https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/ukraine-measures.html")
# # french=get_webpage_text("https://www.canada.ca/fr/immigration-refugies-citoyennete/services/immigrer-canada/mesures-ukraine.html")


# # Translate them- this is duplicating the construction of the source language object- the function it calls
# # hasn't been fully refactored.
# print("Translating...")
# source_english_nlp_object, english_translated_to_spanish_text, english_translated_to_spanish_language_object = get_translation(
#     english, "en", "es")
# source_french_nlp_object, french_translated_to_spanish_text, french_translated_to_spanish_language_object = get_translation(
#     french, "fr", "es")
# source_english_nlp_object, english_translated_to_french_text, english_translated_to_french_language_object = get_translation(
#     english, "en", "es")
# source_french_nlp_object, french_translated_to_english_text, french_translated_to_english_language_object = get_translation(
#     french, "fr", "es")

# # Construct the bag of words and the language object for each text
# original_french_keywords = isolate_words(source_french_nlp_object)
# original_english_keywords = isolate_words(source_english_nlp_object)
# translation_from_english_to_spanish_keywords = isolate_words(
#     english_translated_to_spanish_language_object)
# translation_from_french_to_spanish_keywords = isolate_words(
#     french_translated_to_spanish_language_object)
# translation_from_french_to_english_keywords = isolate_words(
#     french_translated_to_english_language_object)
# translation_from_english_to_french_keywords = isolate_words(
#     english_translated_to_spanish_language_object)


# words_in_common = set(translation_from_french_to_spanish_keywords.keys()).intersection(
#     set(translation_from_english_to_spanish_keywords.keys()))



#     # Score reporting

#     print("Extra score: ",extra_score)
#     print("How many words in the original English", len(original_english_keywords))
#     print("How many words in the original French", len(original_french_keywords))
#     print("How many words in the English translation",
#         len(translation_from_english_to_spanish_keywords))
#     print("How many words in the French Translation",
#         len(translation_from_french_to_spanish_keywords))
#     print("How many words shared between  translations.", len(words_in_common))

#     # similarity score is the comparison value multiplied by 2 and divided by the total number of keywords for French and English source.
#     print("Bag of words simularity: %5.2f" % (((len(words_in_common)*2+extra_score) /
#         (len(translation_from_english_to_spanish_keywords)+len(translation_from_french_to_spanish_keywords)))*100))
#     print("Vector simularity: %5.2f" %
#         (french_translated_to_spanish_language_object.similarity(english_translated_to_spanish_language_object)))

# # Open a file and save some diagnostic data
# f = open("translation_summary.txt", "w")
# f.write("English source text: \n****************************************************************\n")
# f.write(english + "\n\n\n")

# f.write("French source text: \n****************************************************************\n")
# f.write(french + "\n\n\n")

# f.write("English text translated to Spanish: \n****************************************************************\n")
# f.write(english_translated_to_spanish_text + "\n\n\n")

# f.write("French text translated to Spanish: \n****************************************************************\n")
# f.write(french_translated_to_spanish_text + "\n\n\n")

# # Write the sorted word lists
# f.write("Original English significant words and frequency: \n****************************************************************\n")
# for i, j in sorted(original_english_keywords.items(), key=lambda item: item[1], reverse=True):
#     f.write(str(j)+" " + i+"\n")

# f.write("\n\n\n\nEnglish translated to Spanish significant words and frequency: \n****************************************************************\n")
# for i, j in sorted(translation_from_english_to_spanish_keywords.items(), key=lambda item: item[1], reverse=True):
#     f.write(str(j)+" " + i+"\n")

# f.write("\n\n\n\Original French significant words and frequency: \n****************************************************************\n")
# for i, j in sorted(original_french_keywords.items(), key=lambda item: item[1], reverse=True):
#     f.write(str(j)+" " + i+"\n")

# f.write("\n\n\n\French translated to Spanish significant words and frequency: \n****************************************************************\n")
# for i, j in sorted(translation_from_french_to_spanish_keywords.items(), key=lambda item: item[1], reverse=True):
#     f.write(str(j)+" " + i+"\n")

# f.close()
