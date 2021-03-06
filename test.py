'''
Run the application against some web pages for testing.
'''

import translationcompare

def testtranslation(description, englishpage, frenchpage, languagemodels, datarate=1.0):
    # Step through collection, translation and comparison steps.

    print("\n\n\n" + description)

    # Collect Web Page
    english=translationcompare.webpage(englishpage, "en", languagemodels)
    french=translationcompare.webpage(frenchpage, "fr", languagemodels)

    # Remove a percentage of the sentences for one page
    french.reduce(datarate)

     # Translate with Local Translator
    print("Translate with Local Services")
    translated_english=translationcompare.localtranslate(english)
    translated_french=translationcompare.localtranslate(french)

    #  Compare page content
    throwaway = translationcompare.textcompare(english, french)

    print("+++++++++++++++++++\n\n")

# Initialize language model_inputs
languagemodels=translationcompare.languagemodels()

# Test 
testtranslation("Full test data", "https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/ic98-1/tax-collections-policies.html", "https://www.canada.ca/fr/agence-revenu/services/formulaires-publications/publications/ic98-1/politiques-recouvrement-impot.html", languagemodels, 1.0)

# # Test 
# testtranslation("50% test data", "https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/ic98-1/tax-collections-policies.html", "https://www.canada.ca/fr/agence-revenu/services/formulaires-publications/publications/ic98-1/politiques-recouvrement-impot.html", languagemodels)

# Test
testtranslation("Hockey Canada landing page", "https://www.hockeycanada.ca/en-ca/home", "https://www.hockeycanada.ca/fr-ca/home", languagemodels)

# # Test
# testtranslation("Contrasting content", "https://www.hockeycanada.ca/en-ca/home", "https://fencing.ca/fr/", languagemodels)

# # Test
# testtranslation("Contrasting Content 2", "http://slashdot.org", "https://fencing.ca/fr/", languagemodels)

#  # Test
# testtranslation("Fencing Canada Federation", "https://fencing.ca/", "https://fencing.ca/fr/", languagemodels)

# # Test
# testtranslation("Swimming Canada", "https://www.swimming.ca/en/", "https://www.swimming.ca/fr/", languagemodels)

# # Test
# testtranslation("Volleyball Canada", "https://volleyball.ca/en/news/canada-edged-by-germany-in-vnl", "https://volleyball.ca/fr/actualites/le-canada-subit-une-defaite-serree-contre-l-allemagne-en-ligue-des-nations", languagemodels)

# # Test
# testtranslation("Swimming Canada", "https://www.swimming.ca/en/", "https://www.swimming.ca/fr/", languagemodels)
