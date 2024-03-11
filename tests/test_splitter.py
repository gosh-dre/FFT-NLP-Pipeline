import pytest
import pandas as pd
from scripts.splitter import sentence_split, rejoiner

def test_sentence_split_sentence_splits(sentence_split_df):
    split_sentence = sentence_split_df
    split_list = split_sentence[1].to_list()
    assert split_list[0] == 'John ate an apple for lunch. '
    assert split_list[1] == 'It was noce. '
    assert split_list[2] == 'But not chocolate.'

def test_sentence_split_string_doesnt_split(sentence_split_df):
    split_sentence = sentence_split_df
    split_list = split_sentence[1].to_list()
    assert split_list[3] == 'Successfully installed accelerate-0 psutil-5 safetensors-0 tokenizers-0 transformers-4'

def test_sentence_split_list_doesnt_split(sentence_split_df):
    split_sentence = sentence_split_df
    split_list = split_sentence[1].to_list()
    assert split_list[6] == 'chair, table, coffee, -1'