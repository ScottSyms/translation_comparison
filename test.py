import translationcompare

def testtranslation(description, englishpage, frenchpage):
    # Heritage Canada
    print("\n\n\n" + description)
    english=translationcompare.webpage(englishpage, "ENGLISH")
    french=translationcompare.webpage(frenchpage, "FRENCH")

    f=open("flang.txt", "w")
    f.write(french.pagetext)
    f.close()

    # Translate with Local Translator
    # print("Translate with Local Services")
    # translated_english=translationcompare.localtranslate(english)
    # translated_french=translationcompare.localtranslate(french)

    # # Compare page content
    # throwaway = translationcompare.textcompare(english, french)

    # # Translate with Azure
    # print("     Azure translation")
    # translated_english=translationcompare.azuretranslate(english)
    # translated_french=translationcompare.azuretranslate(french)

    # # Compare page content
    # throwaway = translationcompare.textcompare(english, french)
    print("+++++++++++++++++++\n\n")

# # Test 1
testtranslation("Hockey Canada landing page", "https://www.hockeycanada.ca/en-ca/home", "https://www.hockeycanada.ca/fr-ca/home")

# Test 2
# testtranslation("Mixup", "https://www.hockeycanada.ca/en-ca/home", "https://fencing.ca/fr/")

# # Test 3
# testtranslation("Mixup2", "http://slashdot.org", "https://fencing.ca/fr/")



#  # Test 3
# testtranslation("Fencing Canada Federation", "https://fencing.ca/", "https://fencing.ca/fr/")


# # Test 3
# testtranslation("Swimming Canada", "https://www.swimming.ca/en/", "https://www.swimming.ca/fr/")

# # Test 4
# testtranslation("Volleyball Canada", "https://volleyball.ca/en/news/canada-edged-by-germany-in-vnl", "https://volleyball.ca/fr/actualites/le-canada-subit-une-defaite-serree-contre-l-allemagne-en-ligue-des-nations")

# # Test 5
# testtranslation("Swimming Canada", "https://www.swimming.ca/en/", "https://www.swimming.ca/fr/")