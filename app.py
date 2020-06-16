#!/usr/bin/python
#-*- coding: utf-8 -*-

import operator
import sys
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import time
import math


app = Flask(__name__)

@app.route('/')
def index():
	return render_template('start.html')

@app.route('/analyze', methods=['GET','POST'])
def analyze():
	if request.method == 'POST':
		WordList = []
		URL = []
		ExecuteTime = []
		f = request.files['FileName']
		filename = secure_filename(f.filename)
		urls = f.readlines()
		for i in urls:
			start = time.time()
			i = i.decode('utf-8')
			URL.append(i)
			WordList.append(len(s(i)))
			end = time.time()
			ExecuteTime.append(round(end-start,2))
		return render_template('analyze.html',num = len(WordList),urls =URL,test1 = WordList,test2 = ExecuteTime)
	if request.method == 'GET':
		URL = request.args.get('url')
		w = s(URL)
		t = round(end -start,2)
		return render_template('analyze.html', num = 1,urls=URL,test1 = len(w),test2 = t)




@app.route('/button1', methods = ['GET'])
def button1():
	URL = request.args.get('url')
	w = s2(URL)
	return render_template('button1.html',W = w)

def s(URL):
   frequency = {}
   splits = []
   res = requests.get(URL)
   html = BeautifulSoup(res.content, "html.parser")
   all_link = html.find_all("p")

   for t in all_link:
      splits = re.sub('<sup.*?>.*?</sup>','',str(t),0)
      splits = re.sub('<.+?>','',splits,0)
      splits = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','',splits).lower().split()
      for i in splits:
         try:
            cnt = frequency[i]
            frequency[i] = cnt + 1
         except KeyError:
            frequency[i] = 1

   frequency = list(sorted(frequency.items(),key=operator.itemgetter(1),reverse = True))
   return frequency

def s2(URL):
   frequency = {}
   splits = []
   sub_splits = []
   final = []
   result = []
   res = requests.get(URL)
   html = BeautifulSoup(res.content, "html.parser")
   all_link = html.find_all("p")
   total_sentance = 0
   max_freq = 0
   judge = 0
   N = 0
   for t in all_link:
      total_sentance += 1
      splits = re.sub('<sup.*?>.*?</sup>','',str(t),0)
      splits = re.sub('<.+?>','',splits,0)
      splits = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','',splits).lower().split()
      for i in splits:
         try:
            cnt = frequency[i]
            frequency[i] = cnt + 1
         except KeyError:
            frequency[i] = 1
   frequency = list(sorted(frequency.items(),key=operator.itemgetter(1),reverse = True))
   for i in frequency:
      judge = 0
      if i[1] > max_freq :
         max_freq = i[1]
      for j in all_link:
         sub_splits = re.sub('<sup.*?>.*?</sup>','',str(j),0)
         sub_splits = re.sub('<.+?>','',sub_splits,0)
         sub_splits = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','',sub_splits).lower().split()
         if i[0] in sub_splits:
            judge += 1
      final.append(0.5 * i[1] / max_freq * math.log10(total_sentance / judge))
   
   for i in range(10) :
      index = final.index(max(final)) 
      result.append(frequency[index][0])
      result.append(frequency[index][1])
      result.append(round(final[index],5))
      final.pop(index)
   print(result)
   return result 

if __name__ == '__main__':
    app.run(debug=False,host ="127.0.0.1",port ="5000")
