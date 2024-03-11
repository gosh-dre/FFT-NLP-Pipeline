from abc import ABC, abstractmethod
from sqlalchemy.engine.base import Engine
import pandas as pd
import numpy as np

class Fft_generic_builder(ABC):
    """
    Generic base builder class for all others to inherit from. Contained abstract methods and methods to calculate
    confidence scores.
    """
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
    def _get_individual_confidence_scores(self, decision_function: np.ndarray, threshold: int):
        """
        Compute confidence scores based on decision function.

            Parameters:
            decision_function: list of values
            threshold: float brakpoint to determine how much decision values support the prediction

            Returns:
            confidence score
        """
        decision_function = decision_function.tolist()
        if decision_function:
            #get the maximum value that represents the predicted class
            max_value_decision_function = max(decision_function)
            #remove the maximum value from the list of decision function values
            decision_function.remove(max_value_decision_function)
            # get the number of values that are above the given threshold
            vals_above_threshold = len([float(max_value_decision_function-val) for val in decision_function if val >= threshold])
            #get the number of values that are below the threshold
            vals_below_threshold = len([float(max_value_decision_function-val) for val in decision_function if val < threshold])

            return self._grad_val_function(vals_above_threshold, vals_below_threshold)
        else:
            return 0.0

    def _grad_val_function(self, val_above_threshold: int, val_below_threshold: int):
            return float(1.0 / float(1.0 + val_above_threshold)) - float(1.0 / float(1.0 + val_below_threshold))

    def _get_conf_scores_for_df(self):
        df_pred = pd.DataFrame(self.predictions)
        df_pred_transposed = df_pred.T
        df_pred_transposed = df_pred_transposed.rename(columns={0: 'Sentiment', 1: 'Theme', 2: 'SentimentScores', 3: 'ThemeScores'})
        df_pred_transposed = df_pred_transposed[['SentimentScores', 'ThemeScores']]
        self.df_with_conf = df_pred_transposed.reset_index().rename(columns={'index': 'original_index'})

        col_list = ["SentimentScores","ThemeScores"]
        #need to add this in a config file
        threshold_themes = 0.5
        threshold_sentiment = 1.0
        print("... assigned column list ...")
        # create an Empty DataFrame object
        df_intermediate = pd.DataFrame()
        for col in col_list:
            print(col)
            arr=[]
            res = np.array(self.df_with_conf.loc[:, col])
            for i in (res):
                if col == "SentimentScores":
                    a = self._get_individual_confidence_scores(i, threshold_sentiment)
                    arr.append(a)
                    df_intermediate = pd.DataFrame(arr, columns = ["Sentiment_consensus"])
                else:
                    a = self._get_individual_confidence_scores(i, threshold_themes)
                    arr.append(a)
                    df_intermediate = pd.DataFrame(arr, columns = ["Theme_consensus"])
            self.df_with_conf = self.df_with_conf.join(df_intermediate, lsuffix="_left", rsuffix="_right")

    @abstractmethod
    def sentence_rejoin(self):
        pass
    @abstractmethod
    def export_predictions(self):
        """
        Comments exported back to FFT database
        """
        pass
