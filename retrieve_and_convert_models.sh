#!/bin/sh

# Delete some working directories
rm -rf ./models
rm -rf ./out

# Download the requireded models from HuggingFace
git clone https://huggingface.co/Helsinki-NLP/opus-mt-fr-en ./models/fr-en
git clone https://huggingface.co/Helsinki-NLP/opus-mt-fr-es ./models/fr-es
git clone https://huggingface.co/Helsinki-NLP/opus-mt-en-es ./models/en-es
git clone https://huggingface.co/Helsinki-NLP/opus-mt-en-fr ./models/en-fr


# Convert the model to ONNX
python3 convert.py ./models/fr-en -o ./out/fr-en
python3 convert.py ./models/fr-es -o ./out/fr-es
python3 convert.py ./models/en-fr -o ./out/en-fr
python3 convert.py ./models/en-es -o ./out/en-es



