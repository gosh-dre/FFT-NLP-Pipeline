import os
import urllib
from itertools import chain
from typing import List

import yaml
from sqlalchemy import create_engine

config_path = os.path.join(os.getcwd(), "config.yaml")

with open(config_path, "r") as file:
    config_data = yaml.safe_load(file)
    config_data["default"]["models_path"] = os.path.join(
        os.getcwd(), config_data["default"]["models_path"]
    )
    config_data["default"]["app_data_path"] = os.path.join(
        os.getcwd(), config_data["default"]["app_data_path"]
    )
    wards = config_data["default"]["wards"]

app_data_path = os.path.join(config_data["default"]["app_data_path"], "app_data.yaml")

with open(app_data_path, "r") as file:
    app_data = yaml.safe_load(file)


class wards_to_whitelist:
    """
    Class to take the ward list from the config and add all likely permutations
    of the ward name to the presidio whitelist
    """

    @classmethod
    def add_wards_to_allow_list(cls, allow_list: List, wards: str) -> List:
        if wards == "":
            raise ValueError("No ward names to review")
        wards = cls._ward_string_to_list(wards)
        just_ward_names = cls._remove_description_from_name(wards)
        all_names = list(sorted(set(wards + just_ward_names)))
        nested_ward_list = [cls._get_versions_of_word(x) for x in all_names]
        full_allowed_list = list(chain.from_iterable(nested_ward_list))
        full_allowed_list = allow_list + full_allowed_list
        return full_allowed_list

    @classmethod
    def _remove_description_from_name(cls, wards: List) -> List:
        just_names = [
            x.replace("WARD", "").replace("Unit", "").replace("UNIT", "").strip()
            for x in wards
        ]
        return just_names

    @classmethod
    def _get_versions_of_word(cls, i: List) -> List:
        output_lst = []
        output_lst.append(i.upper())
        output_lst.append(i.lower())
        output_lst.append(i.title())
        output_lst.append(i.title().capitalize())
        return output_lst

    @classmethod
    def _ward_string_to_list(cls, ward_string: str) -> List:
        ward_list = ward_string.split("',")
        ward_list = [x.strip("'") for x in ward_list]
        return ward_list


def make_engine():
    extra_params = dict(fast_executemany=True)

    conn_str = "" ""
    conn_root = ""

    engine = create_engine(
        conn_root + urllib.parse.quote_plus(conn_str),
        pool_pre_ping=True,
        **extra_params
    )
    return engine


class wards_to_whitelist:
    """
    Class to take the ward list from the config and add all likely permutations
    of the ward name to the presidio whitelist
    """

    @classmethod
    def add_wards_to_allow_list(cls, allow_list: List, wards: str) -> List:
        if wards == "":
            raise ValueError("No ward names to review")
        wards = cls._ward_string_to_list(wards)
        just_ward_names = cls._remove_description_from_name(wards)
        all_names = list(sorted(set(wards + just_ward_names)))
        nested_ward_list = [cls._get_versions_of_word(x) for x in all_names]
        full_allowed_list = list(chain.from_iterable(nested_ward_list))
        full_allowed_list = allow_list + full_allowed_list
        return full_allowed_list

    @classmethod
    def add_element_wards_to_allow_list(cls, allow_list: List, test: str) -> List:
        if test == "test":
            wards = ["Ward"]
        else:
            wards = cls._wards_based_on_Elementlist()
        full_allowed_list = allow_list + wards
        return full_allowed_list

    @classmethod
    def _remove_description_from_name(cls, wards: List) -> List:
        just_names = [
            x.replace("WARD", "").replace("Unit", "").replace("UNIT", "").strip()
            for x in wards
        ]
        return just_names

    @classmethod
    def _get_versions_of_word(cls, i: List) -> List:
        output_lst = []
        output_lst.append(i.upper())
        output_lst.append(i.lower())
        output_lst.append(i.title())
        output_lst.append(i.title().capitalize())
        return output_lst

    @classmethod
    def _ward_string_to_list(cls, ward_string: str) -> List:
        ward_list = ward_string.split("',")
        ward_list = [x.strip("'") for x in ward_list]
        return ward_list

    @classmethod
    def _wards_based_on_Elementlist(cls) -> List:
        engine = make_engine()
        # select ward names that need to be whitelisted
        qry = "SELECT Matching FROM FFT_NLP.dbo.udf_ElementAll('FAF Wards')"
        result = engine.execute(qry)
        wards = [row[0] for row in result]
        return wards


allow_list = app_data["allow_list"]

rgx_list = [r"\d{2}/\d{2}/\d{4}", r"\d{2}-\d{2}-\d{4}"]
