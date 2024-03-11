from scripts.splitter import sentence_split
import pandas as pd
import pytest


@pytest.fixture()
def data():
    data = {'FILE_ID': [1,2,3,4,5,6,7,8,9, 10,11,12,13,14],
            'CommentType':[1,3,2,1,3,1,2,3,3, 3,3,1,2,2],
            'deident_3': ['John ate an apple for lunch. It was noce. But not chocolate.',
                          'Successfully installed accelerate-0 psutil-5 safetensors-0 tokenizers-0 transformers-4',
                          'Teh cat sat on the hat.', 'desk sofa apple list chickn dog', 'chair, table, coffee, -1',
                          'Frodo Baggins was extremely helpful explaining my daughters treatment to her',
                          'Always takes you through what is happening to your teeth. Very informative and amazing at the job. Highly recommend Greg to anyone',
                          'Pleasant welcome, precise care & treatment. Considerate, you are listened to, patient & understanding',
                          'All the staff and everyone is so  kind and helpful. Lovely. The dentists Tom Mason and Dominic Jerry are two of the best dentists I have ever seen',
                          'the lawyers were mean!',
                          'One thing my food came late.',
                          'My food wasnt nice, it was on top of the TV',
                          "I didn't like porridge&nbsp;",
                          'CatAlina DOING EEG WAS AMAZING'
                          ]
            }
    return data
@pytest.fixture()
def sentence_split_df(data):
    # based on comments from https://www.martinslanedental.com/fft-comments/
    df = pd.DataFrame(data)
    split_sentence = list(sentence_split(df))
    return split_sentence