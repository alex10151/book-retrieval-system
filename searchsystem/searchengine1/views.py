from django.shortcuts import render

# Create your views here.
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 19:26:59 2018

@author: zhz
"""

import os
import pandas as pd
import numpy as np
import jieba
import codecs
from gensim import corpora, models, similarities
import json
import random

comments = ['I read this as my Kindle First selection', 'This book is all hype and let down. I had such high hopes for this story because the premise is very interesting',
            'I was completely drawn into the story',' it\'s characters and complexity. I\'m impressed and will be reading more from this new-to-me author.', 
            'Had my nose deep in it, until the end.', 'I used this book as an all natural sleep aide. Read one page and lights out.', 
            'Took me a while to decide if I liked this book, and suddenly I found I was totally captivated.', 
            'Great book that makes the reader want to know what comes next! ']
class Book(object):
    def __init__(self, id, title='', cat='', writer=''):
        self.id = id
        self.title = title
        self.cat = cat
        self.writer = writer
    def id(self):
        return self.id
    def title(self):
        return self.title
    def cat(self):
        return self.cat
    def writer(self):
        return self.writer
    def generate_comment(self):
        idx = random.sample(range(8), 3)
        result = []
        for i in range(3):
            result.append(comments[idx[i]])
        return result
    def get_content(self):
        path = str(self.id)
        try:
            fp = open(r'/Volumes/zhz/WSM_project/EN/'+path+'.txt', 
                      encoding='utf-8')
        except:
            path = str(self.id) + '-0'
            try:
                fp = open(r'/Volumes/zhz/WSM_project/EN/'+path+'.txt', 
                      encoding='utf-8')
            except:
                path = str(self.id) + '-8'
                fp = open(r'/Volumes/zhz/WSM_project/EN/'+path+'.txt', 
                      encoding='utf-8')                
        content = fp.read()
        content.replace('\n', '&#10')
        fp.close()
        return content
    def generate_comments(self):
        k =random.randint(1,8)
        idx = random.sample(range(8), k)
        result = []
        for i in range(k):
            result.append(comments[idx[i]])
        return result

def set_info():
    t=0
    B = json.load(open(r'/Volumes/zhz/WSM_project/guttenberg_english_ebook_info.json',
                       encoding='utf-8'))
    title = []
    for i in range(1, len(B)):
        title.append(B[i]['title'])
    df_t = pd.DataFrame(title, columns = ['title'])
    id = []
    for i in range(1, len(B)):
        id.append(B[i]['id'])
    df_i = pd.DataFrame(id, columns = ['id'])
    writer = []
    for i in range(1, len(B)):
        writer.append(B[i]['writer_name'])
    df_w = pd.DataFrame(writer, columns = ['writer'])
    cat = []
    for i in range(1, len(B)):
        cat.append(str(B[i]['cat']))
    df_c = pd.DataFrame(cat, columns = ['cat'])
    df = pd.concat([df_i, df_t, df_w, df_c], axis=1) 
    df.to_csv(r'/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/eninfo.csv', sep='\t', 
              index=False, encoding='utf-8')
    df = pd.read_csv(r'/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/eninfo.csv', sep='\t')
    for i in df.columns:
        print(i)
        for j in range(df.shape[0]):
            try:
                np.isnan(df[i][j])
            except:
               t+1 
            else:
                if np.isnan(df[i][j]):
                    df = df.drop(j)       
    df.to_csv(r'/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/eninfo.csv', sep='\t', 
              index=False, encoding='utf-8')
def tokenization(i,df,stopwords):
    result = []
    text = df['title'][i]
    words = jieba.cut_for_search(text)
    for word in words:
        if word not in stopwords and word != ' ':
            result.append(word)
    return result
def token_query(query,stopwords):
    result = []
    words = jieba.cut_for_search(query)
    for word in words:
        if word not in stopwords and word != ' ':
            result.append(word)
    return result
def build_index(df,stopwords):
    corpus = []
    for i in range(df.shape[0]):
        corpus.append(tokenization(i,df,stopwords))  
    dictionary = corpora.Dictionary(corpus)          
    doc_vectors = [dictionary.doc2bow(text) for text in corpus]
    tfidf = models.TfidfModel(doc_vectors)
    tfidf_vectors = tfidf[doc_vectors]  
    return dictionary,tfidf_vectors

def Query(query,dictionary,tfidf_vectors,stopwords):
    query = token_query(query,stopwords)          
    query_bow = dictionary.doc2bow(query)
    index = similarities.MatrixSimilarity(tfidf_vectors)
    sims = index[query_bow]
    #a = np.sort(-sims)
    rank = np.argsort(-sims)
    return rank
def Result(k, rank,df):
    result = []
    for i in range(k):
        result.append(Book(df['id'][rank[i]],df['title'][rank[i]],
        df['cat'][rank[i]],df['writer'][rank[i]]))
    return result
def title_search(k,query,df,stopwords,dictionary,tfidf_vectors):
    """>>>>>>>>"""  
    rank = Query(query,dictionary,tfidf_vectors,stopwords)
    result = Result(k, rank,df)
    return result
def writer_search(writer_name,df):
    result = []
    table = df[df.writer==writer_name]
    for i in table.index:
        result.append(Book(df['id'][i],df['title'][i],
        df['cat'][i],df['writer'][i]))
    return result
#set_info()
comments = ['I read this as my Kindle First selection', 'This book is all hype and let down. I had such high hopes for this story because the premise is very interesting',
            'I was completely drawn into the story',' it\'s characters and complexity. I\'m impressed and will be reading more from this new-to-me author.', 
            'Had my nose deep in it, until the end.', 'I used this book as an all natural sleep aide. Read one page and lights out.', 
            'Took me a while to decide if I liked this book, and suddenly I found I was totally captivated.', 
            'Great book that makes the reader want to know what comes next! ']
def init_variable():
    df = pd.read_csv(r'/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/eninfo.csv', sep='\t')
    stop_words = r'/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/stop_words_for_EN.txt'
    stopwords = codecs.open(stop_words,'r',encoding='utf8').readlines()
    stopwords = [ w.strip() for w in stopwords ]
    dictionary,tfidf_vectors = build_index(df,stopwords)
    temp = {'df':df,'stopwords':stopwords,'dictionary': dictionary,'tfidf_vectors':tfidf_vectors}
    return temp
#result = title_search(10,'The Declaration of Independence of the United States of America')
#result = writer_search('严笏心')