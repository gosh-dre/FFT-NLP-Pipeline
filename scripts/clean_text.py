import html as ihtml
import re
from typing import List

import emoji
from bs4 import BeautifulSoup


def convert_emojis(text):
    text = emoji.demojize(text)
    return text


def add_spaces(text):
    text = re.sub(r"[\.](?=[^ \W\d])", ". ", text)
    text = re.sub(r"[:](?=[^ \W\d])", ": ", text)
    return text


def remove_html(text):
    text = re.sub("(?<=[A-z])<[^<>]*>(?=[A-z])", ". ", text)
    text = re.sub("<[^>]*>", " ", text)
    text = re.sub("\s+", " ", text)
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = BeautifulSoup(ihtml.unescape(text), "lxml").text
    return text


def add_and(text):
    text = re.sub("&amp;", "and", text)
    return text


def remove_excess_punctuation(text):
    double_puctuation_regex = "(?<=[^!.,>$%&][!.,>$%&])[!.,>$%& ]+(?<! )"
    text = re.sub(double_puctuation_regex, "", text)
    return text


def clean_text(rgx_list, text):
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, "[DATE]", new_text, flags=re.IGNORECASE)
    return new_text


class Reecombine_thank_you:
    """
    A class to recombine thank you with the previous sentence."""

    @classmethod
    def does_list_have_thankyou(cls, comment_lst: List):
        thank_you_list = cls.index_containing_substring(comment_lst, "thank you")
        if len(thank_you_list) == 1:
            comment_lst = cls.combine_thank_you_single(comment_lst, thank_you_list[0])
        elif len(thank_you_list) > 1:
            for i in reversed(thank_you_list):
                comment_lst = cls.combine_thank_you_single(comment_lst, i)
        else:
            comment_lst = comment_lst

    @classmethod
    def index_containing_substring(cls, the_list: List, substring: str) -> int:
        index_lst = []
        for i, s in enumerate(the_list):
            if substring in s.lower() and len(s.split()) == 2:
                index_lst.append(i)
        return index_lst

    @classmethod
    def combine_thank_you_single(cls, lst: List, thank_you_index: int) -> List:
        previous_index = thank_you_index - 1
        if thank_you_index != -1 and previous_index > -1:
            combined_word = f"{lst[previous_index]} {lst[thank_you_index]}"
            lst[previous_index] = combined_word
            lst.pop(thank_you_index)
        return lst
