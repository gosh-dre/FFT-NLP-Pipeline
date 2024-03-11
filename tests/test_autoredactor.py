import pytest
import pandas as pd
from scripts.autoredactor import (clean_text, deidentif_presidio, final_check,
        rgx_list, keyword_dictionary)

def test_clean_text(data):
    comment = "I had a very nice cake on 25/12/1903"
    results = clean_text(rgx_list, comment)
    assert "[DATE]" in results
    assert "25/12/1903" not in results

def test_deidentif_presidio():
    comment = "Fake NHS number: 9435797881, Fake names: Harry Potter, Mohammed Ali"
    results = deidentif_presidio(comment)
    assert results == "Fake NHS number: [NUMBER], Fake names: [NAME], [NAME]"

def test_final_check():
    comment = "Catalina, Ezhaq, Taraben, jADE, NADINe"
    result = final_check(keyword_dictionary, comment)
    assert result == 'XXX, XXX, XXX, XXX, XXX'