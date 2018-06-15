from django.shortcuts import render
from django.shortcuts import HttpResponse
import json
import logging
from django.template.context_processors import request
from email.policy import HTTP
from django.http.response import HttpResponse

import searchengine.views as a 
import searchengine1.views as b
import re

import os
import pandas as pd
import numpy as np
import jieba
import codecs
from gensim import corpora, models, similarities
# Create your views here.

temp1 = a.init_variable()
temp2 = b.init_variable()

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
def booksearch(request):
    return render(request,'searchpage.html',)
def resultdisplay(request):
    if request.method == "POST":
        bookinfo = request.POST.get('contact_name')
        language1 = request.POST.get('language')
        author =request.POST.get('author')
      #  temp = {'info':bookinfo}
        result = []
        if language1 == 'Chinese' and author =='book':
           result = a.title_search(10,bookinfo,temp1['df'],temp1['dictionary'],temp1['tfidf_vectors'],temp1['stopwords'])
        elif language1 == 'Chinese' and author =='author':
           result = a.writer_search(bookinfo,temp1['df'])
        elif language1 == 'English' and author =='book':
           result = b.title_search(10,bookinfo,temp2['df'],temp2['stopwords'],temp2['dictionary'],temp2['tfidf_vectors'])
        elif language1 == 'English' and author =='author':
           result = b.writer_search(bookinfo,temp2['df'])
        if result:
            return render(request,'display.html', {"data":result})
        else:
            return render(request,'nocontent.html')
def getstatus(request):
    if request.method == "POST":
        temp_name = request.POST.get('name')
        temp_id = request.POST.get('id')
        temp_author = request.POST.get('author')
        result = {"name":temp_name,"id":temp_id,"author":temp_author}
        #return render(request,'brief.html',{"data":list})
        return HttpResponse(json.dumps(result))
def getbrief(request):
    if request.method == "GET":
        p1 =request.GET.get('p1')
        p2 =request.GET.get('p2')
        p3 =request.GET.get('p3')
        match = zh_pattern.search(p2)
        """based on p1 p2 p3 return the abstract author name and comments :"""
        if match :
            display = a.Book(id = p1)
            temp = {"name":p2,"id":p1,'author':p3,'content':display.get_content(temp1['location']),'comments':display.generate_comment()}
        else:
            display = b.Book(id = p1)
            temp = {"name":p2,"id":p1,'author':p3,'content':display.get_content(),'comments':display.generate_comments()}
        return render(request,'brief.html',{"data":temp})
def getstatus1(request):
    if request.method == "POST":
        return HttpResponse(json.dumps({"status": '200'}))
def getdetail(request):
    if request.method =="GET":
        p1 =request.GET.get('p1')
        """ based on p1 return the full text :"""
        return render(request,'detail.html',)
    
    