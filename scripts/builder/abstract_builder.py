from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from scripts.utils.logger import LogGen


class Fft_generic_builder(ABC):
    """
    Generic base builder class for all others to inherit from. Contained abstract methods and methods to calculate
    confidence scores.
    """

    def __init__():
        self.logger = LogGen.loggen()

    @abstractmethod
    def query_database(self):
        """
        Handles querying of the FFT database based on config information.
        """
        pass

    @abstractmethod
    def chunk(self):
        """
        Breaks the query into chunks to make it more managable
        """
        pass

    @abstractmethod
    def clean_text(self):
        """
        Cleans chunked text. Note this can also involve de-identification in some builders.
        """
        pass

    @abstractmethod
    def sentence_split(self):
        """
        FFT comment split into individual sentences
        """
        pass

    @abstractmethod
    def predict(self):
        pass

    @abstractmethod
    def sentence_rejoin(self):
        pass

    @abstractmethod
    def export_predictions(self):
        """
        Comments exported back to FFT database
        """
        pass
