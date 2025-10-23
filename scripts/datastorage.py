"""
Module that handles interfacing with RL6 SQL database, where data is imported from and exported to.
Data Import: FFT comments are taken from the [RL6_PRODUCTION].[TBL_FBK_CASES] table in the [FFT_NLP]
database, this is a replica of the [TBL_FBK_CASES] in the production database: [RL6_PRODUCTION].

Data Export: Predictions on multi class labels: sentiment and theme are sent back to the [FFT_NLP]
development database. Records are at sentence level, and each sentence is assigned an ID to
indicate its split within a FILE_ID.
"""
# 0.1. Data wrangling and import
import pandas as pd
from tqdm.auto import tqdm

tqdm.pandas()
import sys

import sqlalchemy

from scripts.config import config_data
from scripts.utils.logger import LogGen

logger = LogGen.loggen("datastorage")


def data_import(dbsrc, dbcxn):
    """Handles the data import"""
    try:
        df_sentence = pd.read_sql(dbsrc, dbcxn)
        return df_sentence
    except (sqlalchemy.exc.DBAPIError):
        logger.debug("Could not connect to database")
        sys.exit(1)


def data_export(dbsrc, dbcxn):
    """ "
    Handles the data export to RL6 test instance
    Only exports sentences with FILE_IDs that do not yet exist in the output table.
    """
    temptable = "final_temp_tbl"
    schema_name = "dbo"
    table = f"[FFT_NLP].[dbo].[{config_data['default']['predictions_table']}]"
    key = ["FILE_ID", "CommentType", "SentenceID"]
    dbsrc.to_sql(
        name=temptable, con=dbcxn, schema=schema_name, index=False, if_exists="append"
    )
    conn = dbcxn.connect()
    transfersql = f"""insert into {table} ({",".join(dbsrc.columns)})
                    select * from {temptable} t
                    where not exists
                        (select 1 from {table} m
                        where {"and".join([f" t.{col} = m.{col} " for col in key])}
                   )"""
    conn.execute(transfersql)
    conn.execute(f"drop table {temptable}")
    conn.close()
