from sys import argv
from datasets import load_dataset
import gensim
import numpy as np
import pandas as pd
import sys


dataset = load_dataset("shunk031/wrime", name="ver1")

train_writer_score = dataset["train"]["writer"]
test_writer_score = dataset["test"]["writer"]
train_avg_score =  dataset["train"]["avg_readers"]
test_avg_score =  dataset["test"]["avg_readers"]

writer_score = train_writer_score+ test_writer_score
avg_score = train_avg_score + test_avg_score

#モデルの読み込み
args = sys.argv
EMO = args[1]
model_path = f"emotion_model/{EMO}/chive-1.2-mc5.finetuned-mc3.kv"
chive = gensim.models.KeyedVectors.load(model_path)

# テキストをベクトルに変換するメソッド
"""
入力: 単語ごとに分割されている文章ごとのリスト
出力: 文章に含まれている単語のベクトルをすべて合計したベクトル(ここでは文章ベクトルと呼ぶ) 
"""
def text2vec(norms: str, vectorizer=chive):
    word_vecs = np.array([vectorizer[n] for n in norms if n in vectorizer])
    text_vec = np.sum(word_vecs, axis=0)
    return text_vec


path = "./preprocessing_dataset/last_text_coupas.txt"
with open(path) as f:
    text_wakati_list_not_stopword = [s.rstrip() for s in f.readlines()]
coupas_list = text_wakati_list_not_stopword[:42000]

path = "./preprocessing_dataset/coupus_text.txt"
with open(path, mode='w') as f:
    for text in coupas_list:
        f.write(text+"\n")

path = "./preprocessing_dataset/coupus_text.txt"
with open(path) as f:
    text_coupus = [s.rstrip() for s in f.readlines()]


new_text_coupus= []
for a in text_coupus:
    a = a.split()
    new_text_coupus.append(a)

vec_coupus = []
for i in new_text_coupus:
    if i == []: #前処理ですべての単語が消去されている文章がある。text2vec()関数で空リストを引数にすると0.0が返ってくるが、これは都合が悪いので[0,0,0 ...]のリストに置き換える。
        text_vec = [0 for _ in range(300)]
    else:
        text_vec = text2vec(i).tolist()
    if type(text_vec) != list: # chive内に語彙がない場合の対処
        text_vec = [0 for _ in range(300)]
    vec_coupus.append(text_vec)

df = pd.DataFrame(vec_coupus)

#writer_scoreのデータをdfに追加できるような形に変換する
emotion = ['joy', 'sadness','anticipation', 'surprise', 'anger', 'fear', 'disgust', 'trust']
writer_score_list =[]
for i in writer_score:
    tmp = []
    for emo in emotion:
        tmp.append(i[emo])
    writer_score_list.append(tmp)

#avg_scoreのデータをdfに追加できるような形に変換する
emotion = ['joy', 'sadness','anticipation', 'surprise', 'anger', 'fear', 'disgust', 'trust']
avg_score_list =[]
for i in avg_score:
    tmp = []
    for emo in emotion:
        tmp.append(i[emo])
    avg_score_list.append(tmp)

df_writer = pd.DataFrame(writer_score_list)
df_avg = pd.DataFrame(avg_score_list)

# カラムを作成する
writer_colums = []
avg_colums = []
for i in emotion:
    writer_colums.append(f"writer_{i}")
    avg_colums.append(f"avg_{i}")

# カラムを書き換える
df_writer = df_writer.set_axis(writer_colums, axis=1)
df_avg = df_avg.set_axis(avg_colums, axis=1)

df_writer_avg = pd.concat([df_writer,df_avg ], axis=1)

df = pd.concat([df , df_writer_avg], axis=1)

import os
save_folder_path = f"./vector_and_score/{EMO}"
os.makedirs(save_folder_path)
df.to_csv(f"{save_folder_path}/vec_{EMO}.csv",index=False)