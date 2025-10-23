import pandas as pd
import pytest

from scripts.splitter import Sentence_processing


def test_sentence_split_sentence_splits(sentence_split_df):
    split_sentence = sentence_split_df
    split_list = split_sentence[1].to_list()
    assert split_list[0] == "John ate an apple for lunch. "
    assert split_list[1] == "It was noce. "
    assert split_list[2] == "But not chocolate."


def test_sentence_split_string_doesnt_split(sentence_split_df):
    split_sentence = sentence_split_df
    split_list = split_sentence[1].to_list()
    assert (
        split_list[3]
        == "Successfully installed accelerate-0 psutil-5 safetensors-0 tokenizers-0 transformers-4"
    )


def test_sentence_split_list_doesnt_split(sentence_split_df):
    split_sentence = sentence_split_df
    split_list = split_sentence[1].to_list()
    assert split_list[6] == "chair, table, coffee, -1"


def test_sentence_join_v2(prediction_output):
    joined_df = Sentence_processing.rejoiner_v2(prediction_output)
    joined_lst = joined_df["Sentence"].to_list()
    expected_lst = [
        "[name] ate an apple for lunch.",
        "it was noce.",
        "but not chocolate.",
        "successfully installed accelerate- psutil- safetensors- tokenizers- transformers-",
        "teh cat sat on the hat.",
        "desk sofa apple list chickn dog",
        "chair, table, coffee, -",
        "[name] was extremely helpful explaining my daughters treatment to her",
        "always takes you through what is happening to your teeth.",
        "very informative and amazing at the job.",
        "highly recommend [name] to anyone",
        "pleasant welcome, precise care & treatment.",
        "considerate, you are listened to, patient & understanding",
        "all the staff and everyone is so kind and helpful.",
        "lovely.",
        "the dentists [name] and [name] are two of the best dentists i have ever seen",
        "the lawyers were mean!",
        "one thing my food came late.",
        "my food wasnt nice, it was on top of the tv",
        "i didn't like porridge",
        "xxx doing eeg was amazing",
        "friendly service, staff always smiling and advising on waiting times etc.",
        "liked the concept of the transition cards also enjoyed the flute player [name] to do : potentially a small tuc shop / vending machine with any profits going back in to the gosh funds.",
        "staff were really polite!",
        ":) already pretty good :)",
        "staff, as always, are brilliant.",
        "we got lost so many times : d",
        "cheese & carrots were a wierd meal",
        "very friendly & knowledgeable staff.",
        "clean facilities swift servicing with minimal waiting.",
        "(hopefully the treatments received work! )",
        "always takes you through what is happening to your teeth.",
        "very informative and amazing at the job: highly recommend [name] to anyone",
    ]
    assert set(list(prediction_output.columns)).issubset(set(list(joined_df.columns)))
    assert set(["topic_y", "sentiment_y", "Sentence_y", "SentenceID"]).issubset(
        set(list(joined_df.columns))
    )
    assert joined_lst == expected_lst
