from transformers import MarianTokenizer, AutoModelForSeq2SeqLM

# Bert comparisons
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Instantiate BERT multilingual transformor
bert = SentenceTransformer('distiluse-base-multilingual-cased-v1')

# convert from downloaded html to plain text with pandoc
# pandoc source.html -w plain -o source.txt
# 16 minutes to run this script

texte=open("english.txt", "r").read()
textf=open("french.txt", "r").read()

# texte="""
# You become a resident of Canada for income tax purposes when you
# establish significant residential ties in Canada. You usually establish
# these ties on the date you arrive in Canada.
# """

# textf="""
# Vous devenez un résident du Canada aux fins de l'impôt sur le revenu
# lorsque vous établissez des liens de résidence importants au Canada.
# Vous établissez habituellement ces liens à la date de votre arrivée au
# Canada.
# """

# textf="""
# On entend par « économie clandestine » les revenus gagnés qui ne sont
# pas déclarés aux fins fiscales et les ventes de biens ou de services
# pour lesquelles les taxes ou les droits n'ont pas été payés. L'économie
# clandestine est souvent associée à l'échange de produits et de services
# contre de l'argent comptant sans qu'aucun registre ne soit tenu.
# """

enfr = 'Helsinki-NLP/opus-mt-en-fr'
fren = 'Helsinki-NLP/opus-mt-fr-en'
enes = 'Helsinki-NLP/opus-mt-en-es'
fres = 'Helsinki-NLP/opus-mt-fr-es'

model={}
tokenizer={}

print("Loading models...")
# instantiate the English to French tokenizer and model
tokenizer["enfr"] = MarianTokenizer.from_pretrained(enfr)
model["enfr"] = AutoModelForSeq2SeqLM.from_pretrained(enfr)

# instantiate the French to English tokenizer and model
tokenizer["fren"] = MarianTokenizer.from_pretrained(fren)
model["fren"] = AutoModelForSeq2SeqLM.from_pretrained(fren)

# instantiate the English to Spanish tokenizer and model
tokenizer["enes"] = MarianTokenizer.from_pretrained(enes)
model["enes"] = AutoModelForSeq2SeqLM.from_pretrained(enes)

# instantiate the French to Spanish tokenizer and model
tokenizer["fres"] = MarianTokenizer.from_pretrained(fres)
model["fres"] = AutoModelForSeq2SeqLM.from_pretrained(fres)

def translate(text, language):
    input_ids = tokenizer[language].encode(text, return_tensors="pt")
    outputs = model[language].generate(input_ids)
    return tokenizer[language].decode(outputs[0], skip_special_tokens=True)


print("Beginning translation...")
frenchfromenglish = ""
for i in texte.split("."):
    frenchfromenglish += translate(i, "enfr") + ". "

englishfromfrench = ""
for i in textf.split("."):
    englishfromfrench += translate(i, "fren") + ". "

spanishfromenglish = ""
for i in texte.split("."):
    spanishfromenglish += translate(i, "enes") + ". "

spanishfromfrench = ""
for i in textf.split("."):
    spanishfromfrench += translate(i, "fres") + ". "

# print("French from English\n", frenchfromenglish)
# print("English from French\n", englishfromfrench)
# print("Spanish from English\n", spanishfromenglish)
# print("Spanish from French\n", spanishfromfrench)

output=open("test_onpremtranslation.txt", "w")
output.write("Cosine Similarity Scores")
output.write("\nFrench source, Engqlish translated to French: {}".format(cosine_similarity(bert.encode([textf]), bert.encode([frenchfromenglish]))[0][0]))
output.write("\nEnglish source, French translated to English: {}".format(cosine_similarity(bert.encode([texte]), bert.encode([englishfromfrench]))[0][0]))
output.write("\nFrench translated to Spanish, English translated to Spanish: {}".format(cosine_similarity(bert.encode([spanishfromfrench]), bert.encode([spanishfromenglish]))[0][0]))
output.write("\n\n\n***********************************************************\n\n")

output.write("French from English\n{}\n\n".format(frenchfromenglish))
output.write("\n\n\n***********************************************************\n\n")
output.write("English from French\n{}\n\n".format(englishfromfrench))
output.write("\n\n\n***********************************************************\n\n")
output.write("Spanish from English\n{}\n\n".format(spanishfromenglish))
output.write("\n\n\n***********************************************************\n\n")
output.write("Spanish from French\n{}\n\n".format(spanishfromfrench))
output.write("\n\n\n***********************************************************\n\n")

output.close()

print("Cosine Similarity Scores")
print("French source, English translated to French: ", cosine_similarity(bert.encode([textf]), bert.encode([frenchfromenglish]))[0][0])
print("English source, French translated to English: ", cosine_similarity(bert.encode([texte]), bert.encode([englishfromfrench]))[0][0])
print("French translated to Spanish, English translated to Spanish: ", cosine_similarity(bert.encode([spanishfromfrench]), bert.encode([spanishfromenglish]))[0][0])
