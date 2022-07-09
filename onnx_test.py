'''
Run the application against some web pages for testing.
'''

import onnx_translationcompare

def testtranslation(description, englishpage, frenchpage):
    # Step through collection, translation and comparison steps.

    print("\n\n\n" + description)

    # Collect Web Page
    english=onnx_translationcompare.webpage(englishpage, "en")
    french=onnx_translationcompare.webpage(frenchpage, "fr")

     # Translate with Local Translator
    print("Translate with Local Services")
    translated_english=onnx_translationcompare.localtranslate(english)
    translated_french=onnx_translationcompare.localtranslate(french)

    #  Compare page content
    throwaway = onnx_translationcompare.textcompare(english, french)

    print("+++++++++++++++++++\n\n")

# Test 1
testtranslation("Hockey Canada landing page", "https://www.hockeycanada.ca/en-ca/home", "https://www.hockeycanada.ca/fr-ca/home")

# # Test 2
# testtranslation("Contrasting content", "https://www.hockeycanada.ca/en-ca/home", "https://fencing.ca/fr/")

# # Test 3
# testtranslation("Contrasting Content 2", "http://slashdot.org", "https://fencing.ca/fr/")

#  # Test 3
# testtranslation("Fencing Canada Federation", "https://fencing.ca/", "https://fencing.ca/fr/")

# # Test 3
# testtranslation("Swimming Canada", "https://www.swimming.ca/en/", "https://www.swimming.ca/fr/")

# # Test 4
# testtranslation("Volleyball Canada", "https://volleyball.ca/en/news/canada-edged-by-germany-in-vnl", "https://volleyball.ca/fr/actualites/le-canada-subit-une-defaite-serree-contre-l-allemagne-en-ligue-des-nations")

# # Test 5
# testtranslation("Swimming Canada", "https://www.swimming.ca/en/", "https://www.swimming.ca/fr/")
