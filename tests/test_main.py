import pandas as pd
import pytest

from scripts.builder.director import Fft_director
from scripts.builder.linux_builder_v2 import Linux_builder_deid_v2


def test_main_test_data(data):
    df_out = pd.DataFrame(data)
    df_out.rename(columns={"deident_3": "FFTComment"}, inplace=True)
    conn_str = "" ""
    conn_root = ""
    config_data = {"config_data": "config_data"}
    builder = Linux_builder_deid_v2(conn_str, conn_root, config_data)
    director = Fft_director(builder=builder, test=True)
    df_output = director.run_builder(df_out)
    assert df_output.Sentence.tolist() == [
        "[NAME] ate an apple for lunch. ",
        "It was noce. ",
        "But not chocolate.",
        "Successfully installed accelerate-0 psutil-5 safetensors-0 tokenizers-0 transformers-4",
        "Teh cat sat on the hat.",
        "desk sofa apple list chickn dog",
        "chair, table, coffee, -1",
        "[NAME] was extremely helpful explaining my daughters treatment to her",
        "Always takes you through what is happening to your teeth. ",
        "Very informative and amazing at the job. ",
        "Highly recommend [NAME] to anyone",
        "Pleasant welcome, precise care & treatment. ",
        "Considerate, you are listened to, patient & understanding",
        "All the staff and everyone is so kind and helpful. ",
        "Lovely. ",
        "The dentists [NAME] and [NAME] are two of the best dentists I have ever seen",
        "the lawyers were mean!",
        "One thing my food came late.",
        "My food wasnt nice, it was on top of the TV",
        "I didn't like porridge",
        "XXX DOING EEG WAS AMAZING",
    ]
    assert df_output.topic.tolist() == [
        0,
        9,
        0,
        0,
        4,
        0,
        4,
        3,
        2,
        3,
        0,
        1,
        1,
        1,
        9,
        4,
        4,
        9,
        9,
        9,
        9,
    ]
    assert df_output.Sentiment_consensus.tolist() == [
        0.6666666666666667,
        0.6666666666666667,
        0.0,
        0.6666666666666667,
        0.0,
        0.0,
        0.6666666666666667,
        0.0,
        0.0,
        0.6666666666666667,
        0.0,
        0.6666666666666667,
        0.6666666666666667,
        0.6666666666666667,
        0.0,
        0.6666666666666667,
        0.6666666666666667,
        0.0,
        0.0,
        0.0,
        0.6666666666666667,
    ]
    assert df_output.Theme_consensus.tolist() == [
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.3888888888888889,
        -0.9,
        -0.3888888888888889,
    ]
