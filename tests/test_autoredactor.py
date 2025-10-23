import pandas as pd
import pytest

from scripts.autoredactor import Redactor
from scripts.config import allow_list

redactor = Redactor(allow_list, "test")


def test_deidentif_presidio():
    comment = "Fake NHS number: 9435797881, Fake names: Harry Potter, Mohammed Ali"
    results = redactor.deidentif_presidio(comment)
    assert results == "Fake NHS number: [NUMBER], Fake names: [NAME], [NAME]"


def test_final_check():
    comment = "Catalina, Ezhaq, Taraben, jADE, NADINe"
    result = redactor.final_check(comment)
    assert result == "XXX, XXX, XXX, XXX, XXX"
