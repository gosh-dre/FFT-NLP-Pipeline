"""
Module that handles the annonymization process of personal data contained in the patient/parent feedback.
Words that will be annonymized:
    - Name/Surnames, Dates (by default)
    - Pronouns, Gender.
    - Hospital names (may not need to be annonymized)
"""

# 0.1. Import libraries
import pandas as pd
from transformers import AutoTokenizer, BertForTokenClassification
import regex as re
import nltk
from nltk import word_tokenize
from nltk.util import ngrams
from flashtext import KeywordProcessor
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from joblib import Parallel, delayed
from scripts.config import app_data, rgx_list

import os
import re
import html as ihtml
import pandas as pd
from bs4 import BeautifulSoup

#####MODIFICATIONS HAVE BEEN MADE HERE
allow_list = app_data["allow_list"]
keyword_dictionary = app_data["keyword_dictionary"]



def remove_html(text):
    # text = text.replace("</p>", ".</p>")
    # text = text.replace("<p><br>.</p>", "<p> </p>")
    # text = text.replace(".&nbsp;", "&nbsp;")
    # text = text.replace("&nbsp; ", ". ")
    text = BeautifulSoup(ihtml.unescape(text), "lxml").text
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


#####MODIFICATIONS HAVE BEEN MADE HERE
def clean_text(rgx_list, text):
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, "[DATE]", new_text, flags=re.IGNORECASE)
    return new_text


def tokenize_maintain(text):
    token = text.split(" ")
    bigrams = ngrams(token, 2)
    new_bigrams = []
    c = 0
    while c < len(token) - 1:
        new_bigrams.append((token[c], token[c + 1]))
        c += 1
    return new_bigrams


#####MODIFICATIONS HAVE BEEN MADE HERE
def get_text_to_maintain(text):
    arr = text.split()
    arr = arr[0]
    bigrams = tokenize_maintain(text)
    out_text = []
    aux_replace = []
    for i in range(len(bigrams)):
        aux = " ".join(bigrams[i])
        if(aux.lower() in allow_list):
            out_text.pop()
            out_text.append("[")
            aux_replace.append(aux)
        else:
            out_text.append(bigrams[i][1])
        i = i + 1
    out_text.insert(0, arr)
    return aux_replace, " ".join(out_text)


#####MODIFICATIONS HAVE BEEN MADE HERE
def deidentif_presidio(sequence):
    sequence = sequence.replace("~", " ")
    sequence = sequence.replace(" ~", " ")
    sequence = sequence.replace(" ~ ", " ")
    aux_replace, sequence = get_text_to_maintain(sequence)
    analyzer = AnalyzerEngine(supported_languages=["en", "es"])
    analyzer_results = analyzer.analyze(
        text=sequence, entities=["PERSON", "US_BANK_NUMBER"], language="en", allow_list = allow_list
    )
    anonymizer = AnonymizerEngine()

    anonymized_results = anonymizer.anonymize(
        text=sequence,
        analyzer_results=analyzer_results,
        operators={
            "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
            "US_BANK_NUMBER": OperatorConfig("replace", {"new_value": "[NUMBER]"}),
        },
    )
    sequence_2 = anonymized_results.text
    out = []
    for token in sequence_2.split():
        if token == "~":
            out.append(aux_replace[0])
            aux_replace.pop(0)
            continue
        else:
            out.append(token)

    sequence_out = " ".join(out)
    return sequence_out


def final_check(keyword_dictionary, input_text):
    processor = KeywordProcessor(case_sensitive=False)
    processor.add_keywords_from_dict(keyword_dictionary)
    found = processor.replace_keywords(input_text)
    return found
