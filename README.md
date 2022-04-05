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

For an unknown language pair https://en.wikipedia.org/wiki/Volodymyr_Zelenskyy and https://fr.wikipedia.org/wiki/Volodymyr_Zelenskyy the similarity scores are..
Cross translation cosine simularity score 0.8465454251707962
Third language  cosine simularity score 0.8049446044663335

For an unknown language pair https://en.wikipedia.org/wiki/Julius_Caesar and https://fr.wikipedia.org/wiki/Jules_C%C3%A9sar the similarity scores are...
Cross translation cosine similarity score 0.9862126663559044
Third language  cosine similarity score 0.9851069958143371

For an unknown language pair https://en.wikipedia.org/wiki/Luge and https://fr.wikipedia.org/wiki/Luge_de_course the similarity scores are...
Cross translation cosine similarity score 0.9524338067111711
Third language  cosine similarity score 0.9568057253944731

The similarity scores between https://en.wikipedia.org/wiki/Charles_de_Gaulle and https://fr.wikipedia.org/wiki/Charles_de_Gaulle are...
Cross translation cosine similarity score 0.9720285201437084
Third language  cosine similarity score 0.9817729334831262

The similarity scores between https://en.wikipedia.org/wiki/Charles_de_Gaulle and https://fr.wikipedia.org/wiki/Volodymyr_Zelenskyy are...
Cross translation cosine similarity score 0.8374814823757809
Third language  cosine similarity score 0.7720316873804012

The similarity scores between https://en.wikipedia.org/wiki/Charles_de_Gaulle and https://fr.wikipedia.org/wiki/Luge_de_course are...
Cross translation cosine similarity score 0.894891527608239
Third language  cosine similarity score 0.9013083156340581