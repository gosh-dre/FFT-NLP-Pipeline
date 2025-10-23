"""
Module that handles the annonymization process of personal data contained in the patient/parent feedback.
Words that will be annonymized:
    - Name/Surnames, Dates (by default)
    - Pronouns, Gender.
    - Hospital names (may not need to be annonymized)
"""

from flashtext import KeywordProcessor

# 0.1. Import libraries
from nltk import ngrams
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from scripts.config import app_data, wards_to_whitelist
from scripts.utils.logger import LogGen

logger = LogGen.loggen("autoredactor")


class Redactor:
    def __init__(self, allow_list, test=""):
        self.keyword_dictionary = app_data["keyword_dictionary"]
        self.logger = logger
        self.allow_list = wards_to_whitelist.add_element_wards_to_allow_list(
            allow_list, test
        )

    def tokenize_maintain(self, text):
        token = text.split(" ")
        bigrams = ngrams(token, 2)
        new_bigrams = []
        c = 0
        while c < len(token) - 1:
            new_bigrams.append((token[c], token[c + 1]))
            c += 1
        return new_bigrams

    def get_text_to_maintain(self, text):
        arr = text.split()
        arr = arr[0]
        bigrams = self.tokenize_maintain(text)
        out_text = []
        aux_replace = []
        for i in range(len(bigrams)):
            aux = " ".join(bigrams[i])
            if aux.lower() in self.allow_list:
                try:
                    out_text.pop()
                except IndexError as e:
                    print(e)
                    logger.debug(e)
                out_text.append("[")
                aux_replace.append(aux)
            else:
                out_text.append(bigrams[i][1])
            i = i + 1
        out_text.insert(0, arr)
        return aux_replace, " ".join(out_text)

    def deidentif_presidio(self, sequence):
        sequence = sequence.replace("~", " ")
        sequence = sequence.replace(" ~", " ")
        sequence = sequence.replace(" ~ ", " ")
        aux_replace, sequence = self.get_text_to_maintain(sequence)
        analyzer = AnalyzerEngine(supported_languages=["en", "es"])
        analyzer_results = analyzer.analyze(
            text=sequence,
            entities=["PERSON", "US_BANK_NUMBER"],
            language="en",
            allow_list=self.allow_list,
        )
        anonymizer = AnonymizerEngine()

        anonymized_results = anonymizer.anonymize(
            text=sequence,
            analyzer_results=analyzer_results,
            operators={
                "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
                "US_BANK_NUMBER": OperatorConfig("replace", {"new_value": "[NUMBER]"}),
            },
        )
        sequence_2 = anonymized_results.text
        out = []
        for token in sequence_2.split():
            if token == "~":
                out.append(aux_replace[0])
                aux_replace.pop(0)
                continue
            else:
                out.append(token)

        sequence_out = " ".join(out)
        return sequence_out

    def final_check(self, input_text):
        processor = KeywordProcessor(case_sensitive=False)
        processor.add_keywords_from_dict(self.keyword_dictionary)
        found = processor.replace_keywords(input_text)
        return found
