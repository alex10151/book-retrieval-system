from django.shortcuts import render

# Create your views here.
import os
import pandas as pd
import numpy as np
import jieba
import codecs
from gensim import corpora, models, similarities
import re
import random
comments = ['好文章，赞一个！', '很棒！', '签到水经验', '挺好看的本书', 
            '又一个别人家的娃！', '签到签到了', '作者加油！', '加更可还行，难得难得。']
def ID2dir():
    l = os.listdir(r'/Volumes/zhz/WSM_project/CH')
    dic = {}
    for dir in l:
        temp = re.split('_', dir)
        dic[re.split('\.', temp[-1])[0]] = dir
    return dic
class Book(object):
    def __init__(self, id='', title='', cat='', writer='', writer_id=''):
        self.id = id
        self.title = title
        self.cat = cat
        self.writer = writer
        self.writer_id = writer_id
    def id(self):
        return self.id
    def title(self):
        return self.title
    def cat(self):
        return self.cat
    def writer(self):
        return self.writer
    def writer_id(self):
        return self.writer_id
    def get_content(self,location):
        path = location[str(self.id)]
        try:
            fp = open(r'/Volumes/zhz/WSM_project/CH/'+path, 
                      encoding='gbk')
            content = fp.read()
            fp.close()
        except:
            fp = open(r'/Volumes/zhz/WSM_project/CH/'+path,encoding='utf-8')
            content = fp.read()
            content.replace('\n', '&#10')
        fp.close()
        return content
    def generate_comment(self):
        k = random.randint(1,8)
        idx = random.sample(range(8), k)
        result = []
        for i in range(k):
            result.append(comments[idx[i]])
        return result
        
def merge_info():
    t=0
    df_dw = pd.read_csv(r'/Volumes/zhz/WSM_project/CH/short_stories_chinese_article_info.csv',
                        error_bad_lines=False, sep=',')
    
    df_dw = df_dw.drop(['time', 'url'], axis=1)
    for i in df_dw.columns:
        print(i)
        for j in range(df_dw.shape[0]):
            try:
                np.isnan(df_dw[i][j])
            except:
               t+1 
            else:
                if np.isnan(df_dw[i][j]):
                    df_dw = df_dw.drop(j)
    
    df_dw['id'] = df_dw['id'].astype('int')
    
    df_qd = pd.read_csv(r'/Volumes/zhz/WSM_project/CH/qidian_chinese_novel_info.csv',
                        error_bad_lines=False, sep=',')
    for i in range(df_qd.shape[0]):
        try:
            int(df_qd['id'][i])
        except:
            df_qd = df_qd.drop(i)
    df_qd['id'] = df_qd['id'].astype('int')
    
    df_qd = df_qd.drop(['url'], axis=1)
    for i in df_qd.columns:
        print(i)
        for j in range(df_qd.shape[0]):
            try:
                np.isnan(df_qd[i][j])
            except:
               t+1 
            else:
                if np.isnan(df_qd[i][j]):
                    df_qd = df_qd.drop(j)
    
    
    df = df_dw.append(df_qd, ignore_index=True)
    #df.sort_values(by='id', ascending=True, inplace=True)
    #df['id'] = df['id'].rank(method='dense')
    df.sort_values(by='writer_id', ascending=True, inplace=True)
    df['writer_id'] = df['writer_id'].rank(method='dense')
    #df['id'] = df['id'].astype('int')
    df['writer_id'] = df['writer_id'].astype('int')
    return df
def tokenization(i,df,stopwords):
    result = []
    text = df['title'][i]
    words = jieba.cut_for_search(text)
    for word in words:
        if word not in stopwords:
            result.append(word)
    return result
def token_query(query,stopwords):
    result = []
    words = jieba.cut_for_search(query)
    for word in words:
        if word not in stopwords:
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
        df['cat'][rank[i]],df['writer_name'][rank[i]],df['writer_id'][rank[i]]))
    return result
def title_search(k,query,df,dictionary,tfidf_vectors,stopwords):
    dictionary,tfidf_vectors = build_index(df,stopwords)
    rank = Query(query,dictionary,tfidf_vectors,stopwords)
    result = Result(k, rank,df)
    return result
def writer_search(writer_name,df):
    result = []
    table = df[df.writer_name==writer_name]
    for i in table.index:
        result.append(Book(df['id'][i],df['title'][i],
        df['cat'][i],df['writer_name'][i],df['writer_id'][i]))
    return result

def init_variable():
    df = pd.read_csv('/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/ch_info.csv', sep=',')
    stop_words = r'/Users/hsw/Desktop/notebookworkdir/searchsystem/searchsystem/resource/stop_words_for_CH.txt'
    stopwords = codecs.open(stop_words,'r',encoding='utf8').readlines()
    stopwords = [ w.strip() for w in stopwords ]
    dictionary,tfidf_vectors = build_index(df,stopwords)
    location = ID2dir()
    temp = {'df':df,'stopwords':stopwords,'dictionary': dictionary,'tfidf_vectors':tfidf_vectors,'location':location}
    return temp
    #result = title_search(10,'王者荣耀')
#result = writer_search('严笏心')