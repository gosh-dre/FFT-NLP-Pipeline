import pandas as pd
import pytest

from scripts.modeller import Prediction
from scripts.splitter import Sentence_processing


def test_pred_v2(sentence_split_df):
    predictions = Prediction.run_pred_v2(sentence_split_df[1])
    df_pred = pd.DataFrame(predictions)
    df_pred_transposed = df_pred.T
    df_pred_transposed = df_pred_transposed.rename(
        columns={0: "Sentiment", 1: "Theme", 2: "SentimentScores", 3: "ThemeScores"}
    )
    df_rejoined = Sentence_processing.rejoiner_v1(
        sentence_split_df[1],
        df_pred_transposed,
        sentence_split_df[0],
        sentence_split_df[2],
        sentence_split_df[3],
        sentence_split_df[4],
    )
    df_t = df_pred_transposed
    assert df_t.Sentiment.tolist()[0] == -1
    assert df_t.Theme.tolist()[0] == 0
    assert df_t.SentimentScores.tolist()[0].tolist() == [
        2.145477641458471,
        0.9895262002024194,
        -0.14197920407795084,
    ]
    assert df_t.ThemeScores.tolist()[0].tolist() == [
        9.271888050385755,
        6.230908319360409,
        2.856598415538362,
        3.8683274881814196,
        7.262601169332564,
        0.731018750339703,
        -0.2913869962551327,
        2.7809620872114835,
        3.9560467300860265,
        8.269364303573912,
    ]
