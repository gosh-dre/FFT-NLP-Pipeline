"""
Module that handles the annonymization process of personal data contained in the patient/parent feedback.
Words that will be annonymized:
    - Name/Surnames, Dates (by default)
    - Pronouns, Gender.
    - Hospital names (may not need to be annonymized)
"""

from itertools import zip_longest

import numpy as np

# 0.1. Import libraries
import pandas as pd
import pysbd

from scripts.clean_text import Reecombine_thank_you

# 0.2. Sentence Splitting


class Sentence_processing:
    @classmethod
    def make_split_sentence_df(cls, df_sentence):
        """Tokenizing (splitting the entire comment into tokens) the comments into a df."""
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
            Reecombine_thank_you.does_list_have_thankyou(aux_list)

            sentence_ids = []
            for j in range(len(aux_list)):
                sentence_ids.append(j)

            sentences = []
            for j in range(len(aux_list)):
                sentences.append(aux_list[j])

            sent_lengths = []
            for j in range(len(aux_list)):
                sent_lengths.append(len(aux_list[j]))

            sentences_dict = {
                id: (sent, length)
                for id, sent, length in zip_longest(
                    sentence_ids, sentences, sent_lengths
                )
            }

            for k, v in sentences_dict.items():
                sentences_longer.append(v[0])
                index_o_long.append(i)

        # Combine to make a dataframe

        indexes_list = index_o_long
        sentences_list = sentences_longer
        cls.aux_df = pd.DataFrame(
            {"original_index": indexes_list, "tokenized_sentences": sentences_list}
        )
        df_file_ids = df_sentence[["FILE_ID", "CommentType"]]
        cls.df_file_ids = df_file_ids.reset_index()
        cls.df_file_ids = cls.df_file_ids.rename(columns={"index": "original_index"})
        cls.aux_df = pd.merge(cls.df_file_ids, cls.aux_df, on=["original_index"])
        cls.aux_df = cls.aux_df.reset_index()
        cls.aux_df = cls.aux_df.rename(columns={"index": "sentence_order"})

    @classmethod
    def get_sentence_split_v2(cls, df_sentence):
        """Returns dataframe with tokenised comments."""
        cls.make_split_sentence_df(df_sentence)
        return cls.aux_df

    @staticmethod
    def rejoiner_v2(input_df):
        """
        Joins consecutive sentences if they share same FILE_ID, Theme and Sentiment.
        """

        input_df = input_df.replace(np.nan, 0)

        # For sentences having same theme and sentiment in a FILE_ID of the same CommenType, combine
        grouped = input_df.groupby(
            ["sentence_order", "original_index", "CommentType", "topic", "sentiment"]
        ).agg({"Sentence": list})
        grouped["Sentences"] = [" ".join(map(str, l)) for l in grouped["Sentence"]]
        grouped = grouped.reset_index().drop(columns=["Sentence"])
        out = grouped.rename(columns={"Sentences": "Sentence"})
        out = pd.merge(
            input_df, out, on=["original_index", "sentence_order", "CommentType"]
        )
        out = out.rename(
            columns={
                "sentiment_x": "sentiment",
                "topic_x": "topic",
                "Sentence_x": "Sentence",
            }
        )

        # 0.4. SentenceID Derivation
        out["SentenceID"] = out.groupby(["FILE_ID"]).cumcount() + 1

        # 0.5. Impute missing themes and sentiment, 0 for unclassifiethd eme and -2 for No sentiment
        out["topic"] = out["topic"].replace(r"^\s*$", 0, regex=True)
        out["sentiment"] = out["sentiment"].replace(r"^\s*$", -2, regex=True)

        return out
