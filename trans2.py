from transformers import MarianTokenizer, AutoModelForSeq2SeqLM
# pandoc source.html -w plain -o source.txt

texte="""
A trustee includes a liquidator, a receiver, a receiver-manager, a trustee in bankruptcy, an assignee, an executor, an administrator, a sequestrator, or any other person who performs a function similar to the one a trustee performs. A trustee does both of the following authorizes a payment or causes a payment to be made for another person. administers, manages, distributes, winds up, controls, or otherwise deals with another person's property, business, estate, or income
"""

textf="""
Un fiduciaire est un liquidateur, un séquestre, un séquestre-gérant, un syndic de faillite, un cessionnaire, un exécuteur, un administrateur, un administrateur-séquestre ou toute autre personne accomplissant des fonctions semblables à celles d’un fiduciaire Les fonctions du fiduciaire sont les suivantes Il autorise ou fait effectuer un paiement pour le compte d’une autre personne. Il administre, gère, distribue, liquide ou contrôle les biens, l’entreprise, la succession ou le revenu d’une autre personne.
"""

texte=open("english.txt", "r").read()
textf=open("french.txt", "r").read()

enfr = 'Helsinki-NLP/opus-mt-en-fr'
fren = 'Helsinki-NLP/opus-mt-fr-en'
enes = 'Helsinki-NLP/opus-mt-en-es'
fres = 'Helsinki-NLP/opus-mt-fr-es'

model={}
tokenizer={}

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

frenchfromenglish = ""
for i in texte.split("."):
    frenchfromenglish += translate(i, "enfr") + "."

englishfromfrench = ""
for i in textf.split("."):
    englishfromfrench += translate(i, "enfr") + "."

spanishfromenglish = ""
for i in texte.split("."):
    spanishfromenglish += translate(i, "enfr") + "."

spanishfromfrench = ""
for i in textf.split("."):
    spanishfromfrench += translate(i, "enfr") + "."

print("French from English\n", frenchfromenglish)
print("English from French\n", englishfromfrench)
print("Spanish from English\n", spanishfromenglish)
print("Spanish from French\n", spanishfromfrench)

output=open("onpremtranslation.txt", "w")
output.write("French from English\n{}\n\n".format(frenchfromenglish))
output.write("English from French\n{}\n\n".format(englishfromfrench))
output.write("Spanish from English\n{}\n\n".format(spanishfromenglish))
output.write("Spanish from French\n{}\n\n".format(spanishfromfrench))

output.close()