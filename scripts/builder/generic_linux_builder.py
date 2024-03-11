from scripts.builder.abstract_builder import Fft_generic_builder
from scripts.datastorage import data_import, data_export
from scripts.splitter import sentence_split, rejoiner
from scripts.config import config_data, rgx_list
from sqlalchemy import create_engine
import urllib
import pandas as pd
from scripts.modeller import pred
from joblib import Parallel, delayed
from tqdm.notebook import tqdm
from scripts.autoredactor import (remove_html, clean_text,
                                 deidentif_presidio, final_check,
                                 keyword_dictionary)


class Linux_builder_deid(Fft_generic_builder):
    """
    Basic builder designed to work on the DRE interim environment.
    """
    def __init__(self, conn_str: str, conn_root: str, config_data: dict):
        extra_params = dict(fast_executemany=True)
        self.engine =  create_engine(conn_root + urllib.parse.quote_plus(conn_str), pool_pre_ping=True,
                                    **extra_params)
        self.config_data = config_data

    def query_database(self)  -> pd.DataFrame:
        predictions_table = self.config_data['default']["predictions_table"]
        wards = self.config_data['default']['wards']
        daysToRetrieve = self.config_data['default']['daysToRetrieve']
        sourceLocation = self.config_data['default']['sourceLocation']
        input_qry = f"select a1.* from (select a.[FILE_ID], a.[ChildFFTWhatWasBad] as FFTComment, 3 as CommentType from {sourceLocation}.[TBL_FBK_CASES] a where a.[ChildFFTWhatWasBad] is not null and a.[FILE_ID] not in (SELECT distinct [FILE_ID] FROM [FFT_NLP].[dbo].[{predictions_table}]) and a.[DEPARTMENT] in ({wards}) and datediff(d, a.ENTERED_DATE, getdate())<{daysToRetrieve}) as a1 union all select a2.* from (select a.[FILE_ID], a.[ChildFFTWhatWasGood] as FFTComment, 2 as CommentType from {sourceLocation}.[TBL_FBK_CASES] a where a.[ChildFFTWhatWasGood] is not null and a.[FILE_ID] not in (SELECT distinct [FILE_ID] FROM [FFT_NLP].[dbo].[{predictions_table}]) and a.[DEPARTMENT] in ({wards}) and datediff(d, a.ENTERED_DATE, getdate())<{daysToRetrieve}) as a2 union all select a3.* from (select a.[FILE_ID], a.[AdultFFTDescription] as FFTComment, 1 as CommentType from {sourceLocation}.[TBL_FBK_CASES] a left join [FFT_NLP].[dbo].[{predictions_table}] b on a.[FILE_ID] = b.[FILE_ID] where a.[AdultFFTDescription] is not null and b.[FILE_ID] is null and a.[FILE_ID] not in (SELECT distinct [FILE_ID] FROM [FFT_NLP].[dbo].[{predictions_table}]) and a.[DEPARTMENT] in ({wards}) and datediff(d, a.ENTERED_DATE, getdate())<{daysToRetrieve}) as a3;"
        df_query = data_import(input_qry, self.engine)
        return df_query

    def chunk(self, df_query: pd.DataFrame):
        n = 200  # chunk row size
        self.df_query_chunks = [df_query[i : i + n] for i in range(0, df_query.shape[0], n)]

    def clean_text(self):
        """
        Cleans and de-identifies text.
        """
        data = []
        cleaned_df = pd.DataFrame({})
        for chunk in self.df_query_chunks:
        # Process the chunk
            chunk["clean_text"] = Parallel(n_jobs=-1)(
                delayed(remove_html)(x)
                for x in tqdm(chunk["FFTComment"])
            )
            chunk["deident"] = Parallel(n_jobs=-1)(
                delayed(clean_text)(rgx_list, x)
                for x in tqdm(chunk["clean_text"])
            )
            chunk["deident_2"] = Parallel(n_jobs=-1)(
                delayed(deidentif_presidio)(x) for x in tqdm(chunk["deident"])
            )
            chunk["deident_3"] = Parallel(n_jobs=-1)(
                delayed(final_check)(keyword_dictionary, x)
                for x in tqdm(chunk["deident_2"])
            )
            chunk['deident_3'] = chunk['deident_3'].str.replace(r'<[^<>]*>', '', regex=True)
            data.append(chunk)
        self.cleaned_df = pd.concat(data)
        print("... finished autoredacting ...")

    def sentence_split(self):
        self.split_sentences = sentence_split(self.cleaned_df)
        print("... finished sentence splitting ...")

    def predict(self):
        self.predictions = pred(self.split_sentences[1])
        self._get_conf_scores_for_df()
        print("... finished predicting ...")

    def sentence_rejoin(self) -> pd.DataFrame:
        df_rejoined = rejoiner(self.split_sentences[1], self.predictions, self.split_sentences[0], self.split_sentences[2], self.split_sentences[3], self.split_sentences[4])
        df_for_export = df_rejoined.join(self.df_with_conf, lsuffix="_left", rsuffix="_right")
        df_for_export = df_for_export[["FILE_ID", "CommentType", "SentenceID", "Sentence", "sentiment", "topic", "Sentiment_consensus", "Theme_consensus"]]
        print("... finished rejoining ...")
        return df_for_export

    def export_predictions(self, df_for_export: pd.DataFrame):
        df_for_export["Pipeline_ver"] = 0.04
        df_for_export["DateRan"] = pd.Timestamp.now()
        data_export(df_for_export, self.engine)
        print(".... exported final view ...")
