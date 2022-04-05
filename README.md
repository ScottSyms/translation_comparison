Script checks compares French and English websites and generates a metric to see how similar they are.

Conda requirements are in **requirements.yml**.

Build the conda translation environment with the following

conda env create --file requirements.yml

Switch to the conda environment with the following

conda activate translations.yml

Requires Azure Translation service.  Documentation to come.

The service does two comparisons.

In the Cross translation cosine simularity score, French is translated to English and English to French.  Like languages are compared for simularity and the individual scores averaged.

In the Third language cosine similarity score, both pages are translated to Spanish, and the Spanish translations are compared.

RESULTS

Compare French and Engish wikipedia pages

The similarity scores between https://en.wikipedia.org/wiki/Volodymyr_Zelenskyy and https://fr.wikipedia.org/wiki/Volodymyr_Zelenskyy are...
Cross translation cosine similarity score 0.8447698618403967
Third language  cosine similarity score 0.8035030124314274
Raw language BERT cosine similarity score 0.49295646
Cross translation language BERT cosine similarity score 0.5602318048477173
Third language BERT cosine similarity score 0.5461247

The similarity scores between https://en.wikipedia.org/wiki/Julius_Caesar and https://fr.wikipedia.org/wiki/Jules_C%C3%A9sar are...
Cross translation cosine similarity score 0.9862126663559044
Third language  cosine similarity score 0.9851200136003984
Raw language BERT cosine similarity score 0.505359
Cross translation language BERT cosine similarity score 0.6329710483551025
Third language BERT cosine similarity score 0.6914114

The similarity scores between https://en.wikipedia.org/wiki/Luge and https://fr.wikipedia.org/wiki/Luge_de_course are...
Cross translation cosine similarity score 0.9524500203203897
Third language  cosine similarity score 0.9567756281212567
Raw language BERT cosine similarity score 0.5010763
Cross translation language BERT cosine similarity score 0.475641131401062
Third language BERT cosine similarity score 0.43394098

The similarity scores between https://en.wikipedia.org/wiki/Charles_de_Gaulle and https://fr.wikipedia.org/wiki/Charles_de_Gaulle are...
Cross translation cosine similarity score 0.9720288881264448
Third language  cosine similarity score 0.9817530406510517
Raw language BERT cosine similarity score 0.60305756
Cross translation language BERT cosine similarity score 0.6425055265426636
Third language BERT cosine similarity score 0.61636186

The similarity scores between https://en.wikipedia.org/wiki/Charles_de_Gaulle and https://fr.wikipedia.org/wiki/Luge_de_course are...
Cross translation cosine similarity score 0.894891527608239
Third language  cosine similarity score 0.9013119327737523
Raw language BERT cosine similarity score 0.32892394
Cross translation language BERT cosine similarity score 0.3530624508857727
Ignored unknown kwarg option direction
Third language BERT cosine similarity score 0.30099398