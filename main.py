# Load libraries

import pandas as pd

from scripts.builder.director import Fft_director
from scripts.builder.linux_builder_v2 import Linux_builder_deid_v2

pd.options.mode.chained_assignment = None  # default='warn'
from tqdm.notebook import tqdm

tqdm.pandas()
from scripts.config import config_data

# Database connection using Windows Authentication

conn_str = ""
conn_root = ""

"""
Executes the whole FFT NLP pipeline:
1. Imports new comments from RL6 database.
2. Autoredacts identifiers: names, phone numbers and email addresses.
3. Splits sentences as GOSH comments tend to have more than one sentence.
4. Predict Sentiment and Theme of each sentence.
5. Rejoin sentences if they have they have same FILE_ID, Sentiment and Theme.
"""

builder = Linux_builder_deid_v2(conn_str, conn_root, config_data)
director = Fft_director(builder=builder)
director.run_builder()
