import sys

import pandas as pd
from joblib import Parallel, delayed
from tqdm.auto import tqdm

from scripts.autoredactor import Redactor
from scripts.builder.abstract_builder import Fft_generic_builder
from scripts.clean_text import (
    add_and,
    add_spaces,
    clean_text,
    convert_emojis,
    remove_excess_punctuation,
    remove_html,
)
from scripts.config import allow_list, make_engine, rgx_list
from scripts.datastorage import data_export, data_import
from scripts.modeller import Prediction
from scripts.splitter import Sentence_processing
from scripts.utils.logger import LogGen, data_summary_for_logs


class Linux_builder_deid_v1(Fft_generic_builder):
    """
    Basic builder designed to work on the DRE interim environment.
    """

    def __init__(self, conn_str: str, conn_root: str, config_data: dict):
        self.logger = LogGen.loggen("linux builder")
        extra_params = dict(fast_executemany=True)
        self.engine = make_engine()
        self.config_data = config_data

    def query_database(self) -> pd.DataFrame:
        predictions_table = self.config_data["default"]["predictions_table"]
        wards = self.config_data["default"]["wards"]
        daysToRetrieve = self.config_data["default"]["daysToRetrieve"]
        sourceLocation = self.config_data["default"]["sourceLocation"]
        # add query to database here
        input_qry = (
            f"select a.[DEPARTMENT], a.ENTERED_DATE, a.[FILE_ID], a.[ChildFFTWhatWasBad] as FFTComment, 3 as CommentType "
            f"from {sourceLocation}.[TBL_FBK_CASES] a "
            f"inner join {sourceLocation}.[TBL_ALT_FILE_INFO] c on c.file_id = a.FILE_ID and file_state not in ('Deleted','Deleted-Inc') "
            f"left outer join [FFT_NLP].[dbo].[{predictions_table}] p on p.FILE_ID = a.FILE_ID and p.FILE_ID is null "
            f"left outer join [FFT_NLP].[dbo].udf_ElementList ('FAF Wards','Ex',1) el on DEPARTMENT=el.Matching "
            f"inner join  [FFT_NLP].[RL6_PRODUCTION].[TBL_FBK_UDFS] u  on u.FEEDBACK_ID = a.FEEDBACK_ID "
            f"where nullif([PUBLICSUBVALIDFILE],'Yes') is null "
            f"and datediff(d, a.ENTERED_DATE, getdate())<{daysToRetrieve} "
            f"and el.Matching is null and a.[ChildFFTWhatWasBad] is not null "
            f"and a.[DEPARTMENT] is not null "
            f"and a.[FILE_ID] not in (SELECT distinct [FILE_ID] FROM [FFT_NLP].[dbo].[{predictions_table}]) "
            f"union all "
            f"select a.[DEPARTMENT], a.ENTERED_DATE, a.[FILE_ID], a.[ChildFFTWhatWasGood] as FFTComment, 2 as CommentType "
            f"from {sourceLocation}.[TBL_FBK_CASES] a "
            f"inner join {sourceLocation}.[TBL_ALT_FILE_INFO] c on c.file_id = a.FILE_ID and file_state not in ('Deleted','Deleted-Inc') "
            f"left outer join [FFT_NLP].[dbo].[{predictions_table}] p on p.FILE_ID = a.FILE_ID and p.FILE_ID is null "
            f"left outer join [FFT_NLP].[dbo].udf_ElementList ('FAF Wards','Ex',1) el on DEPARTMENT=el.Matching "
            f"inner join  [FFT_NLP].[RL6_PRODUCTION].[TBL_FBK_UDFS] u  on u.FEEDBACK_ID = a.FEEDBACK_ID "
            f"where nullif([PUBLICSUBVALIDFILE],'Yes') is null "
            f"and datediff(d, a.ENTERED_DATE, getdate())<{daysToRetrieve} "
            f"and el.Matching is null "
            f"and a.[ChildFFTWhatWasGood] is not null "
            f"and a.[DEPARTMENT] is not null "
            f"and a.[FILE_ID] not in (SELECT distinct [FILE_ID] FROM [FFT_NLP].[dbo].[{predictions_table}]) "
            f"union all "
            f"select a.[DEPARTMENT], a.ENTERED_DATE, a.[FILE_ID], a.[AdultFFTDescription] as FFTComment, 1 as CommentType "
            f"from {sourceLocation}.[TBL_FBK_CASES] a "
            f"inner join {sourceLocation}.[TBL_ALT_FILE_INFO] c on c.file_id = a.FILE_ID and file_state not in ('Deleted','Deleted-Inc') "
            f"left outer join [FFT_NLP].[dbo].[{predictions_table}] p on p.FILE_ID = a.FILE_ID and p.FILE_ID is null "
            f"left outer join [FFT_NLP].[dbo].udf_ElementList ('FAF Wards','Ex',1) el on DEPARTMENT=el.Matching "
            f"inner join  [FFT_NLP].[RL6_PRODUCTION].[TBL_FBK_UDFS] u  on u.FEEDBACK_ID = a.FEEDBACK_ID "
            f"where nullif([PUBLICSUBVALIDFILE],'Yes') is null "
            f"and datediff(d, a.ENTERED_DATE, getdate())<{daysToRetrieve} "
            f"and el.Matching is null "
            f"and a.[AdultFFTDescription] is not null "
            f"and a.[DEPARTMENT] is not null "
            f"and a.[FILE_ID] not in (SELECT distinct [FILE_ID] FROM [FFT_NLP].[dbo].[{predictions_table}]);"
        )
        df_query = data_import(input_qry, self.engine)
        data_sum = data_summary_for_logs(df_query)
        self.logger.info(f"data_sum: {data_sum}")
        return df_query

    def chunk(self, df_query: pd.DataFrame):
        n = 200  # chunk row size
        self.df_query_chunks = [
            df_query[i : i + n] for i in range(0, df_query.shape[0], n)
        ]

    def clean_text(self, test: str):
        """
        Cleans and de-identifies text.
        """
        redactor = Redactor(allow_list, test)
        data = []
        cleaned_df = pd.DataFrame({})
        for chunk in self.df_query_chunks:
            # Process the chunk
            chunk["clean_text"] = Parallel(n_jobs=-1)(
                delayed(convert_emojis)(x) for x in tqdm(chunk["FFTComment"])
            )
            chunk["clean_text"] = Parallel(n_jobs=-1)(
                delayed(add_and)(x) for x in tqdm(chunk["clean_text"])
            )
            chunk["clean_text"] = Parallel(n_jobs=-1)(
                delayed(remove_html)(x) for x in tqdm(chunk["clean_text"])
            )
            chunk["clean_text"] = Parallel(n_jobs=-1)(
                delayed(add_spaces)(x) for x in tqdm(chunk["clean_text"])
            )
            chunk["clean_text"] = Parallel(n_jobs=-1)(
                delayed(remove_excess_punctuation)(x) for x in tqdm(chunk["clean_text"])
            )
            chunk["deident"] = Parallel(n_jobs=-1)(
                delayed(clean_text)(rgx_list, x) for x in tqdm(chunk["clean_text"])
            )
            chunk["deident_2"] = Parallel(n_jobs=-1)(
                delayed(redactor.deidentif_presidio)(x) for x in tqdm(chunk["deident"])
            )
            chunk["deident_3"] = Parallel(n_jobs=-1)(
                delayed(redactor.final_check)(x) for x in tqdm(chunk["deident_2"])
            )
            chunk["deident_3"] = chunk["deident_3"].str.replace(
                r"<[^<>]*>", "", regex=True
            )
            chunk["deident_3"] = chunk["deident_3"].str.replace(
                "[\.](?=[^ \W\d])", ". ", regex=True
            )
            chunk["deident_3"] = chunk["deident_3"].str.replace(
                "[:](?=[^ \W\d])", ": ", regex=True
            )
            data.append(chunk)
        try:
            self.cleaned_df = pd.concat(data)
            self.logger.info("Finished autoredacting")
            print("... finished autoredacting ...")
        except (ValueError):
            self.logger.warning("Nothing to concatenate")
            print("Nothing to concatenate")
            sys.exit(1)

    def sentence_split(self):
        self.split_sentences = Sentence_processing.get_sentence_split_v1(
            self.cleaned_df
        )
        self.logger.info("Finished sentence splitting")
        print("... finished sentence splitting ...")

    def predict(self):
        self.predictions = Prediction.run_pred_v1(self.split_sentences)
        self._get_conf_scores_for_df()
        self.logger.info("Finished predicting")

    def sentence_rejoin(self) -> pd.DataFrame:
        df_for_export = Sentence_processing.rejoiner_v1(self.predictions)
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
        df_for_export["Pipeline_ver"] = 0.1
        df_for_export["DateRan"] = pd.Timestamp.now()
        data_export(df_for_export, self.engine)
        self.logger.info("Exported final view")
        print(".... exported final view ...")

    def _add_child_text_label(self, CommentType, Sentence):
        if CommentType == 3:
            Sentence = f"BAD: {Sentence}"
        if CommentType == 2:
            Sentence = f"GOOD: {Sentence}"
        return Sentence
