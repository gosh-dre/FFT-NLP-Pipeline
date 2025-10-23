"""
Module that handles multiclass classification tasks for the tow target variables: Sentiment and Theme.
It uses models that were pickled from initial training by data from multiple NHS trusts including Imperial College London NHS Trust.
Uses Support Vector Machine classifier.

Prediction Confidence:
    - SVM lacks probA function, which locates probabilities for classification.
    - we propose a confidence score function using the distance score from the one-vs-rest approach.
"""

import os

import regex as re
from setfit import SetFitModel
from sklearn.feature_extraction.text import CountVectorizer
from transformers import pipeline

from scripts.config import config_data
from scripts.utils.logger import LogGen

logger = LogGen.loggen("moddler")

import pickle


class Prediction:
    @classmethod
    def clean_df(cls):
        cls.pred_df[
            "tokenized_sentences_for_predict"
        ] = cls.pred_df.tokenized_sentences.str.lower()
        cls.pred_df["tokenized_sentences_for_predict"] = cls.pred_df[
            "tokenized_sentences_for_predict"
        ].str.strip()
        cls.pred_df["tokenized_sentences_for_predict"] = cls.pred_df[
            "tokenized_sentences_for_predict"
        ].replace("[0-9]+", "", regex=True)

    @classmethod
    def get_scores(cls):
        print("... processing theme consensus ...")
        logger.info("Processing theme consensus")
        cls.pred_df["Theme_consensus"] = list(
            map(
                cls._get_label_based_attr_score,
                cls.pred_df["tokenized_sentences_for_predict"],
                cls.pred_df["topic"],
            )
        )
        print("... processing sentiment consensus ...")
        logger.info("Processing sentiment consensus")
        cls.pred_df["Sentiment_consensus"] = list(
            map(
                cls._get_label_based_attr_score,
                cls.pred_df["tokenized_sentences_for_predict"],
                cls.pred_df["sentiment"],
            )
        )
        cls.pred_df = cls.pred_df.rename(columns={"tokenized_sentences": "Sentence"})

    @classmethod
    def get_predictions(cls):
        sentiment_model = SetFitModel.from_pretrained(cls.sentiment_model_file)
        theme_model = SetFitModel.from_pretrained(cls.theme_model_file)
        cls.pred_df["sentiment"] = sentiment_model.predict(cls.sentences)
        cls.pred_df["topic"] = theme_model.predict(cls.sentences)

    @classmethod
    def run_pred_v2(cls, pred_df):
        cls.sentiment_model_file = "/app/ext_models/Sentiment.BEST.balanced.4epochs"
        cls.theme_model_file = "/app/ext_models/Theme.BEST.imbal.2eps"

        sentiment_model = SetFitModel.from_pretrained(cls.sentiment_model_file)
        theme_model = SetFitModel.from_pretrained(cls.theme_model_file)

        cls.pred_df = pred_df
        cls.clean_df()
        cls.sentences = cls.pred_df["tokenized_sentences_for_predict"].to_list()
        cls.get_predictions()
        cls.get_scores()
        return cls.pred_df

    @classmethod
    def _get_label_based_attr_score(cls, text, label):
        pipe = pipeline(
            "text-classification", model="/app/ext_models/deberta-base-long-nli"
        )
        nli_output = pipe(dict(text=text, text_pair="{}".format(label)))
        nli_output = nli_output["score"]
        return nli_output
