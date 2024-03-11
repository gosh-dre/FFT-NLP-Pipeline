"""
Module that handles the annonymization process of personal data contained in the patient/parent feedback.
Words that will be annonymized:
    - Name/Surnames, Dates (by default)
    - Pronouns, Gender.
    - Hospital names (may not need to be annonymized)
"""

# 0.1. Import libraries
import numpy as np
import pandas as pd
# import pyodbc
from itertools import zip_longest

from bs4 import BeautifulSoup

import sklearn
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import (
    accuracy_score,
    roc_curve,
    auc,
    f1_score,
    roc_auc_score,
    cohen_kappa_score,
)
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix

import re
import string
import nltk

import pickle
from pathlib import Path

project_path = Path(".")

import spacy
import spacy_cleaner
from spacy_cleaner.processing import removers, mutators

nlp = spacy.load("en_core_web_lg")

import pysbd

# 0.2. Sentence Splitting
def sentence_split(df_sentence):
    """Tokenizing (splitting the entire comment into tokens) the comments
    For consecutive sentences, split is at 75 characters
        - Sentences longer than 75 characters are split into separate sentences.
        - Sentences shorter than 75 characters are appended to the consecutive sentence.
    """

    comments1 = df_sentence["deident_3"]
    cum = []
    sentences_longer = []
    index_list = []
    index_o_long = []

    for i in range(len(df_sentence)):
        cumulative_sentence = ""
        tokenize_sentences = comments1[i]
        # aux_list = [sent.text for sent in nlp(tokenize_sentences).sents]
        seg = pysbd.Segmenter(language="en", clean=False)
        aux_list = seg.segment(tokenize_sentences)

        sentence_ids = []
        for j in range(len(aux_list)):
            sentence_ids.append(j)

        sentences = []
        for j in range(len(aux_list)):
            sentences.append(aux_list[j])

        sent_lengths = []
        for j in range(len(aux_list)):
            sent_lengths.append(len(aux_list[j]))

        sentences_dict = {id: (sent, length) for id, sent, length in zip_longest(sentence_ids, sentences, sent_lengths)}
        
        for k, v in sentences_dict.items():
            sentences_longer.append(v[0])
            index_o_long.append(i)

    # Combine to make a dataframe

    indexes_list = index_o_long
    sentences_list = sentences_longer
    aux_df = pd.DataFrame({"original_index":indexes_list,"tokenized_sentences":sentences_list})
    df_file_ids = df_sentence[["FILE_ID", "CommentType"]]
    df_file_ids = df_file_ids.reset_index()
    df_file_ids = df_file_ids.rename(columns={"index": "original_index"})
    aux_df = pd.merge(df_file_ids, aux_df, on=["original_index"])
    aux_df = aux_df.reset_index()
    aux_df = aux_df.rename(columns={"index": "sentence_order"})
    comments2 = aux_df["tokenized_sentences"]
    ids = aux_df.original_index
    sent_ids = aux_df.sentence_order
    commenttypes = aux_df.CommentType

    return ids, comments2, df_file_ids, commenttypes, sent_ids


# splitter.rejoiner(resultant[1], results, resultant[0], resultant[2])


# 0.3. Sentence Rejoining
def rejoiner(data, predictions, ids, df_file_ids, commenttypes, sent_ids):
    """
    Joins consecutive sentences if they share same FILE_ID, Theme and Sentiment.
    """
    comments2 = data
    results = predictions
    ids = ids
    df_file_ids = df_file_ids
    commenttypes = commenttypes
    sent_ids = sent_ids
    # initiate a list to record the empty columns
    recorder = []
    
    # rows with 'missing data' are identifies and '0' is added to those rows to recorder list adn '1' is added to rows with data to recorder list
    for comment in comments2:
        if (comment == "missing data") or (comment == "") or (comment == "None"):
            recorder.append(0)
        else:
            recorder.append(1)
    # when the rows have 'missing data ' theme and sentiment will be ''
    topics = []
    sentis = []
    for i in range(0, len(recorder)):
        if recorder[i] == 0:
            topics.append("")
            sentis.append("")
        else:
            topics.append(results[1][i])
            sentis.append(results[0][i])

    # Creating a dataframe with ids, comments,theme and sentiment
    f1 = {
        "sentence_order": sent_ids,
        "original_index": ids,
        "CommentType": commenttypes,
        "Sentence": comments2,
        "topic": topics,
        "sentiment": sentis
    }

    df1 = pd.DataFrame(data=f1)  # df1 is the output df with the tokenized comments

    # For sentences having same theme and sentiment in a FILE_ID of the same CommenType, combine
    grouped = df1.groupby(["sentence_order", "original_index", "CommentType", "topic", "sentiment"]).agg({'Sentence': list})
    grouped['Sentences'] = [' '.join(map(str, l)) for l in grouped['Sentence']]
    grouped = grouped.reset_index().drop(columns=['Sentence'])
    out = grouped.rename(columns={"Sentences": "Sentence"})
    out = pd.merge(df_file_ids, out, on=["original_index", "CommentType"])

    # 0.4. SentenceID Derivation
    out["SentenceID"] = out.groupby(["FILE_ID"]).cumcount() + 1

    # 0.5. Impute missing themes and sentiment, 0 for unclassified theme and -2 for No sentiment
    out['topic'] = out['topic'].replace(r'^\s*$', 0, regex=True)
    out['sentiment'] = out['sentiment'].replace(r'^\s*$', -2, regex=True)

    return out
