# -*- coding: utf-8 -*-
"""Sentimental_Analysis_for_Tweets_using_CNN___RNN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1STAmUkQkW2HJOrLD0S9pf5_CF5iWU0b2
"""

#RECOMMENDED: open in GOOGLE COLAB to see important results

#You can skip this particular code of importing data
#This code is to import dataset directly from the kaggle server

import os
import sys
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from urllib.parse import unquote, urlparse
from urllib.error import HTTPError
from zipfile import ZipFile
import tarfile
import shutil

CHUNK_SIZE = 40960
DATA_SOURCE_MAPPING = 'sentimental-analysis-for-tweets:https%3A%2F%2Fstorage.googleapis.com%2Fkaggle-data-sets%2F1312443%2F2186313%2Fbundle%2Farchive.zip%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com%252F20240715%252Fauto%252Fstorage%252Fgoog4_request%26X-Goog-Date%3D20240715T150753Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D3895f5c8746ebd079538e2d2abcbbc16a961734b4ecaade429cd1dc0769f3bbeee15a459c93adaca723717867b9fac402d8c055e03cd050bd467d2c50040632811c53e097e3eb080fc06e0bfd81720c152cbb856bd1abaff430e2e75a2c0d3743058c917c15ed911002a093a740f8644e1439d4dc29fa2bcbb9be2d3a3309e03175791b18d1694a96d06dbdef07179fb0b7ffbaa1dd747dca446e2a9b6df274b466bc74f7835f747ac2db3064c764a29fa753321ac799c326df26df0f1de5ea843ed826edc675178f6e85e7262d0085ee607676e4623d7ff2552550f62589885a80ceb5fa1f89dc061d410120a0b266df7e4590f0c5d2e745958fbfeb5de3bae'

KAGGLE_INPUT_PATH='/kaggle/input'
KAGGLE_WORKING_PATH='/kaggle/working'
KAGGLE_SYMLINK='kaggle'

!umount /kaggle/input/ 2> /dev/null
shutil.rmtree('/kaggle/input', ignore_errors=True)
os.makedirs(KAGGLE_INPUT_PATH, 0o777, exist_ok=True)
os.makedirs(KAGGLE_WORKING_PATH, 0o777, exist_ok=True)

try:
  os.symlink(KAGGLE_INPUT_PATH, os.path.join("..", 'input'), target_is_directory=True)
except FileExistsError:
  pass
try:
  os.symlink(KAGGLE_WORKING_PATH, os.path.join("..", 'working'), target_is_directory=True)
except FileExistsError:
  pass

for data_source_mapping in DATA_SOURCE_MAPPING.split(','):
    directory, download_url_encoded = data_source_mapping.split(':')
    download_url = unquote(download_url_encoded)
    filename = urlparse(download_url).path
    destination_path = os.path.join(KAGGLE_INPUT_PATH, directory)
    try:
        with urlopen(download_url) as fileres, NamedTemporaryFile() as tfile:
            total_length = fileres.headers['content-length']
            print(f'Downloading {directory}, {total_length} bytes compressed')
            dl = 0
            data = fileres.read(CHUNK_SIZE)
            while len(data) > 0:
                dl += len(data)
                tfile.write(data)
                done = int(50 * dl / int(total_length))
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {dl} bytes downloaded")
                sys.stdout.flush()
                data = fileres.read(CHUNK_SIZE)
            if filename.endswith('.zip'):
              with ZipFile(tfile) as zfile:
                zfile.extractall(destination_path)
            else:
              with tarfile.open(tfile.name) as tarfile:
                tarfile.extractall(destination_path)
            print(f'\nDownloaded and uncompressed: {directory}')
    except HTTPError as e:
        print(f'Failed to load (likely expired) {download_url} to path {destination_path}')
        continue
    except OSError as e:
        print(f'Failed to load {download_url} to path {destination_path}')
        continue

print('Data source import complete.')

import tensorflow
from tensorflow import keras
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras import layers,Sequential
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

"""## Data Input"""

df=pd.read_csv('/content/sentiment_tweets3.csv')
df.head()

"""## Number of labels"""

df['label (depression result)'].unique()

X=df['message to examine']
y=df['label (depression result)']

df.describe()

df.info()

X

y

"""## Data split for training and testing"""

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

print('X_train :',len(X_train))
print('X_test :',len(X_test))
print('y_train :',len(y_train))
print('y_test :', len(y_test))

"""## Tokenizing  text"""

tokenizer=Tokenizer(num_words=999,filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n',lower=True,split=" ")

tokenizer.fit_on_texts(X)

X_train_tok=tokenizer.texts_to_sequences(X_train)
X_test_tok=tokenizer.texts_to_sequences(X_test)

X_train.head()

X_train_tok[0]

"""## Padding the tokenized text to create a consistent training input"""

X_train_pad=pad_sequences(X_train_tok,maxlen=100)
X_test_pad=pad_sequences(X_test_tok,maxlen=100)

X_train_pad[0]

X_test_pad[0]

"""## Number of words in the vocabulary"""

len(tokenizer.word_index)

"""## CNN model creation"""

cnn = Sequential([
     keras.layers.Embedding(len(tokenizer.word_index), 32, input_length=100),

     keras.layers.Conv1D(16,3,activation="relu"),
     keras.layers.MaxPool1D(2),

     keras.layers.Conv1D(32,3,activation="relu"),
     keras.layers.MaxPool1D(2),

     keras.layers.Flatten(),

     keras.layers.Dense(64,activation="relu"),
     keras.layers.Dense(1,activation="sigmoid")
 ])

"""## CNN model's parameters"""

cnn.compile(optimizer="adam",metrics=["accuracy"],loss=["binary_crossentropy"])

"""## CNN model training"""

cnn.fit(
    X_train_pad,
    y_train,
    epochs=10,
    validation_split=0.2
)

"""## CNN model predictions"""

results = cnn.predict(X_test_pad)

results = results.round()

y_test_np=np.asarray(y_test,dtype=np.int32)

cnn.evaluate(X_test_pad,y_test_np)

"""## RNN model creation"""

rnn = Sequential([
    keras.layers.Embedding(len(tokenizer.word_index), 32, input_length=100),

    keras.layers.LSTM(16,activation="tanh",dropout=0.2),

    keras.layers.Dense(64,activation="relu"),
    keras.layers.Dense(1,activation="sigmoid")
])

rnn.compile(optimizer="adam",metrics=["accuracy"],loss="binary_crossentropy")

rnn.fit(
    X_train_pad,
    y_train,
    epochs=10,
    validation_split=0.2
)

rnn.evaluate(X_test_pad,y_test_np)
