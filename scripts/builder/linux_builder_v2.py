import urllib

import pandas as pd
from sqlalchemy import create_engine

from scripts.builder.linux_builder_v1 import Linux_builder_deid_v1
from scripts.config import config_data, rgx_list
from scripts.datastorage import data_export
from scripts.modeller import Prediction
from scripts.splitter import Sentence_processing
from scripts.utils.logger import (
    LogGen,
    sentiment_prediction_summary_for_logs,
    theme_prediction_summary_for_logs,
)


class Linux_builder_deid_v2(Linux_builder_deid_v1):
    """
    Basic builder designed to work on the DRE interim environment.
    """

    def __init__(self, conn_str: str, conn_root: str, config_data: dict):
        self.logger = LogGen.loggen("linux builder v1")
        extra_params = dict(fast_executemany=True)
        self.engine = create_engine(
            conn_root + urllib.parse.quote_plus(conn_str),
            pool_pre_ping=True,
            **extra_params,
        )
        self.config_data = config_data

    def sentence_split(self):
        self.split_sentences = Sentence_processing.get_sentence_split_v2(
            self.cleaned_df
        )
        self.logger.info("Finished sentence splitting")
        print("... finished sentence splitting ...")

    def predict(self):
        self.predictions = Prediction.run_pred_v2(self.split_sentences)
        self.logger.info("Finished predicting")
        print("... finished predicting ...")

    def sentence_rejoin(self) -> pd.DataFrame:
        df_for_export = Sentence_processing.rejoiner_v2(self.predictions)
        df_for_export = df_for_export[
            [
                "FILE_ID",
                "CommentType",
                "SentenceID",
                "Sentence",
                "sentiment",
                "topic",
                "Sentiment_consensus",
                "Theme_consensus",
            ]
        ]
        df_for_export["Sentence"] = list(
            map(
                self._add_child_text_label,
                df_for_export["CommentType"],
                df_for_export["Sentence"],
            )
        )
        self.logger.info("Finished rejoining")
        print("... finished rejoining ...")
        return df_for_export

    def export_predictions(self, df_for_export: pd.DataFrame):
        df_for_export["Pipeline_ver"] = 0.2
        df_for_export["DateRan"] = pd.Timestamp.now()
        theme_sum = theme_prediction_summary_for_logs(df_for_export)
        self.logger.info(f"predicted_theme: {theme_sum}")
        sent_sum = sentiment_prediction_summary_for_logs(df_for_export)
        self.logger.info(f"predicted_sent: {sent_sum}")
        data_export(df_for_export, self.engine)
        self.logger.info("Exported final view")
        print(".... exported final view ...")
