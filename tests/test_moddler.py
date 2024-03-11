import pytest
import pandas as pd
from scripts.modeller import pred

def test_pred(sentence_split_df):
    results = pred(sentence_split_df[1])
    df_results = pd.DataFrame(results)
    df_t = df_results.T
    df_t = df_t.rename(columns={0: 'Sentiment', 1: 'Theme', 2: 'SentimentScores', 3: 'ThemeScores'})
    assert df_t.Sentiment.tolist()[0] == -1
    assert df_t.Theme.tolist()[0] == 0
    assert df_t.SentimentScores.tolist()[0].tolist() == [2.145477641458471, 0.9895262002024194, -0.14197920407795084]
    assert df_t.ThemeScores.tolist()[0].tolist() == [9.271888050385755, 6.230908319360409, 2.856598415538362, 3.8683274881814196, 7.262601169332564, 0.731018750339703, -0.2913869962551327, 2.7809620872114835, 3.9560467300860265, 8.269364303573912]

def test_pred_no_input():
    with pytest.raises(TypeError) as exc_info:
        results = pred()
    assert str(exc_info.value) == "pred() missing 1 required positional argument: 'comments'"

def test_pred_wrong_input(sentence_split_df):
    with pytest.raises(AttributeError) as exc_info:
        results = pred(sentence_split_df[0])
    assert str(exc_info.value) == "'int' object has no attribute 'strip'"