from typing import Union

import pandas as pd

from scripts.builder.abstract_builder import Fft_generic_builder
from scripts.utils.logger import LogGen


class Fft_director:
    """
    Class to run builder classes as part of a builder design pattern.
    Note: any builder object can be used Fft_generic_builder is being used as a type hint to represent this.
    """

    def __init__(self, builder: Fft_generic_builder, test: bool = False):
        """
        Init function to load class object.

        Parameters:
            builder: builder class object
            test: boolean variable to indicate if unit tests are being run. Default is False.
        """
        logger = LogGen.loggen("director")
        logger.info("Creating builder class")
        self.builder = builder
        self.test = test

    def run_builder(self, test_data: pd.DataFrame = None) -> Union[pd.DataFrame, None]:
        """
        Function to run builder. Can either be run in production or as a test. Test does not contain
        query database as this can't be tested in the dev env. Note only returns a dataframe if being
        used for tests.

        Parameters:
            test_data: pandas dataframe of test data. Default is None.
        """
        if self.test is not True:
            df_query = self.builder.query_database()
            self.builder.chunk(df_query)
            self.builder.clean_text("")
            self.builder.sentence_split()
            self.builder.predict()
            df_for_export = self.builder.sentence_rejoin()
            self.builder.export_predictions(df_for_export)
        else:
            self.builder.chunk(test_data)
            self.builder.clean_text("test")
            self.builder.sentence_split()
            self.builder.predict()
            df_for_export = self.builder.sentence_rejoin()
            return df_for_export
