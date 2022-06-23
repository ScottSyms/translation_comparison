import translationcompare

# # Heritage Canada
# print("Heritage Canada landing page")
# english=translationcompare.webpage("https://www.canada.ca/en/canadian-heritage.html", "ENGLISH")
# french=translationcompare.webpage("https://www.canada.ca/fr/patrimoine-canadien.html", "FRENCH")

# Heritage Canada
print("Hockey Canada landing page")
english=translationcompare.webpage("https://www.hockeycanada.ca/en-ca/home", "ENGLISH")
french=translationcompare.webpage("https://www.hockeycanada.ca/fr-ca/home", "FRENCH")


# Translate with Local Translator
print("Translate with Local Services")
translated_english=translationcompare.localtranslate(english)
translated_french=translationcompare.localtranslate(french)

# Compare page content
throwaway = translationcompare.textcompare(english, french)

# # Translate with Azure
# print("Azure translation")
# translated_english=translationcompare.azuretranslate(english)
# translated_french=translationcompare.azuretranslate(french)

# # Compare page content
# throwaway = translationcompare.textcompare(english, french)
