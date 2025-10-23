import pytest

from scripts.clean_text import (
    Reecombine_thank_you,
    add_and,
    clean_text,
    convert_emojis,
    remove_excess_punctuation,
    remove_html,
)
from scripts.config import rgx_list


def test_convert_emojis():
    comment = "enjoyed the flute player 😀"
    results = convert_emojis(comment)
    assert results == "enjoyed the flute player :grinning_face:"


def test_clean_text():
    comment = "I had a very nice cake on 25/12/1903"
    results = clean_text(rgx_list, comment)
    assert "[DATE]" in results
    assert "25/12/1903" not in results


def test_add_and():
    comment = "Very friendly &amp; Knowledgeable staff"
    results = add_and(comment)
    assert results == "Very friendly and Knowledgeable staff"


def test_remove_html_single_marker():
    comment = "as always, are brilliant<div>We got lost"
    results = remove_html(comment)
    assert results == "as always, are brilliant. We got lost"


def test_remove_html_multi_marker():
    comment = "Knowledgeable staff.</p><p><br></p><p>Clean Facilities</p><p><br></p><p>Swift servicing with minimal waiting.</p><p><br></p><p>(Hopefully the treatments received work! )"
    results = remove_html(comment)
    assert (
        results
        == "Knowledgeable staff. Clean Facilities Swift servicing with minimal waiting. (Hopefully the treatments received work! )"
    )


def test_index_containing_single_thank_you():
    lst = [
        "Staff were very helpful and friendly. ",
        "Room very clean and kitchen was useful. ",
        "Thank you!",
    ]
    output = Reecombine_thank_you.index_containing_substring(lst, "thank you")
    assert output == [2]


def test_index_containing_substring_thank_you_like_phrase():
    lst = [
        "Staff were very helpful and friendly. ",
        "THANK YOU ALL!",
        "Room very clean and kitchen was useful. ",
        "Thank you!",
    ]
    output = Reecombine_thank_you.index_containing_substring(lst, "thank you")
    assert output == [3]


def test_index_containing_substring_multiple_thank_you():
    lst = [
        "Staff were very helpful and friendly. ",
        "Thank you!",
        "Room very clean and kitchen was useful. ",
        "Thank you!",
    ]
    output = Reecombine_thank_you.index_containing_substring(lst, "thank you")
    assert output == [1, 3]


def test_index_containing_substring_empty_thank_you():
    lst = []
    output = Reecombine_thank_you.index_containing_substring(lst, "thank you")
    assert output == []


def test_combine_thank_you_single():
    index = 2
    lst = [
        "Staff were very helpful and friendly. ",
        "Room very clean and kitchen was useful. ",
        "Thank you!",
    ]
    output = Reecombine_thank_you.combine_thank_you_single(lst, index)
    assert output[1] == "Room very clean and kitchen was useful.  Thank you!"


def test_combine_thank_you_single_empty_lst():
    index = 2
    lst = []
    with pytest.raises(IndexError) as exc_info:
        output = Reecombine_thank_you.combine_thank_you_single(lst, index)
    assert str(exc_info.value) == "list index out of range"


def test_combine_thank_you_single_no_index():
    index = None
    lst = [
        "Staff were very helpful and friendly. ",
        "Room very clean and kitchen was useful. ",
        "Thank you!",
    ]
    with pytest.raises(TypeError) as exc_info:
        output = Reecombine_thank_you.combine_thank_you_single(lst, index)
    assert (
        str(exc_info.value) == "unsupported operand type(s) for -: 'NoneType' and 'int'"
    )


def test_does_list_have_thankyou():
    lst = [
        "Staff were very helpful and friendly. ",
        "THANK YOU ALL!",
        "Room very clean and kitchen was useful. ",
        "Thank you!",
    ]
    Reecombine_thank_you.does_list_have_thankyou(lst)
    assert lst == [
        "Staff were very helpful and friendly. ",
        "THANK YOU ALL!",
        "Room very clean and kitchen was useful.  Thank you!",
    ]


def test_does_list_have_no_thankyou():
    lst = [
        "Staff were very helpful and friendly. ",
        "THANK YOU ALL!",
        "Room very clean and kitchen was useful.",
    ]
    Reecombine_thank_you.does_list_have_thankyou(lst)
    assert lst == [
        "Staff were very helpful and friendly. ",
        "THANK YOU ALL!",
        "Room very clean and kitchen was useful.",
    ]


def test_does_list_have_no_thankyou_no_lst():
    lst = []
    Reecombine_thank_you.does_list_have_thankyou(lst)
    assert lst == []


def test_remove_excess_punctuation():
    comment = "the lawyers were mean!!.,"
    results = remove_excess_punctuation(comment)
    assert results == "the lawyers were mean!"


def test_remove_excess_punctuation_empty():
    comment = ""
    results = remove_excess_punctuation(comment)
    assert results == ""


def test_remove_excess_punctuation_numerical():
    comment = 1
    with pytest.raises(TypeError) as exc_info:
        results = remove_excess_punctuation(comment)
    assert str(exc_info.value) == "expected string or bytes-like object"
