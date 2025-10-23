import pytest

from scripts.config import wards_to_whitelist


def test_wards_in_whitelist():
    ward_string = "'ANAESTHETIC','Level 4'"
    allow_list = []
    output_lst = wards_to_whitelist.add_wards_to_allow_list(allow_list, ward_string)
    assert output_lst == [
        "ANAESTHETIC",
        "anaesthetic",
        "Anaesthetic",
        "Anaesthetic",
        "LEVEL 4",
        "level 4",
        "Level 4",
        "level 4",
    ]


def test_wards_in_whitelist_empty():
    ward_string = ""
    allow_list = []
    with pytest.raises(ValueError) as exc_info:
        output_lst = wards_to_whitelist.add_wards_to_allow_list(allow_list, ward_string)
    assert str(exc_info.value) == "No ward names to review"
