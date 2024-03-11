"""
Module that handles multiclass classification tasks for the tow target variables: Sentiment and Theme.
It uses models that were pickled from initial training by data from multiple NHS trusts including Imperial College London NHS Trust.
Uses Support Vector Machine classifier.

Prediction Confidence:
    - SVM lacks probA function, which locates probabilities for classification.
    - we propose a confidence score function using the distance score from the one-vs-rest approach.
"""

import os
import numpy as np
import pandas as pd
import regex as re
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
from scripts.config import config_data

import pickle

def pred(comments):
    # create a list to append comments
    comm = []
    # preprocessing of text. each comment is converted to lowercase, punctuations and numbers were removed and white spaces were removed before prediction
    for text in comments:
        text = text.strip().lower()
        text = text.strip()
        text = re.sub("[0-9]+", "", text)
        comm.append(text)
    # unpickle the features ,tfidftransformer,classifier pickle files
    loaded_vec1 = CountVectorizer(
        decode_error="replace",
        vocabulary=pickle.load(
            open(os.path.join(config_data['default']['models_path'], "feature_sentiment.pkl"), "rb")
        ),
    )
    tfidftransformer1 = pickle.load(
        open(
            os.path.join(config_data['default']['models_path'], "tfidftransformer_sentiment.pkl"), "rb"
        )
    )
    temp1 = loaded_vec1.transform(comm)
    test_tfidf1 = tfidftransformer1.transform(temp1)
    with open(
        os.path.join(config_data['default']['models_path'], "sentiment-classifier.pkl"), "rb"
    ) as clf2_file:
        qsenti = pickle.load(clf2_file)
    # predict sentiments for the comments using unpickled classifier
    y_pred1 = qsenti.predict(test_tfidf1)
    # unpickle the features ,tfidftransformer,
    loaded_vec2 = CountVectorizer(
        decode_error="replace",
        vocabulary=pickle.load(
            open(os.path.join(config_data['default']['models_path'], "feature_theme.pkl"), "rb")
        ),
    )
    tfidftransformer2 = pickle.load(
        open(os.path.join(config_data['default']['models_path'], "tfidftransformer_theme.pkl"), "rb")
    )
    temp2 = loaded_vec2.transform(comm)
    test_tfidf2 = tfidftransformer2.transform(temp2)
    with open(
        os.path.join(config_data['default']['models_path'], "theme-classifier.pkl"), "rb"
    ) as clf2_file:
        qtopic = pickle.load(clf2_file)

    # predict theme for each comment
    y_pred2 = qtopic.predict(test_tfidf2)

    y_decid1 = qsenti.decision_function(test_tfidf1)
    y_decid2 = qtopic.decision_function(test_tfidf2)

    return y_pred1, y_pred2, y_decid1, y_decid2  #
