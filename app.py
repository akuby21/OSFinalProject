#!/usr/bin/python
#-*- coding: utf-8 -*-

import operator
import sys
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from elasticsearch import Elasticsearch
import time
import math
app = Flask(__name__)
list_w = []
freq = []
results = []
URLlength = {}
URL = []
@app.route('/')
def index():
	return render_template('start.html')

@app.route('/analyze', methods=['GET','POST'])
def analyze():
	idNum = 0
	WordList = []
	ExecuteTime = []
	if request.method == 'POST':
		f = request.files['FileName']
		filename = secure_filename(f.filename)
		urls = f.readlines()
		for i in urls:
			start = time.time()
			i = i.decode('utf-8').rstrip()
			URL.append(i)
			WordList.append(len(init(i,idNum)))
			end = time.time()
			ExecuteTime.append(round(end-start,2))
			idNum = idNum + 1
		return render_template('analyze.html',num = len(WordList),urls =URL,test1 = WordList,test2 = ExecuteTime)
	if request.method == 'GET':
		url = request.args.get('url')
		start = time.time()
		w = init(url)
		end = time.time()
		t = round(end -start,2)
		WordList.append(len(w))
		URL.append(url)
		ExecuteTime.append(t)
		return render_template('analyze.html', num = 1,urls=URL,test1 = WordList,test2 = ExecuteTime)

@app.route('/button1', methods = ['GET'])
def button1():
	w = []
	CONTER = 1;
	URL = request.args.get('url')
	start = time.time()
	
	search = es.search(index="web",body={'from':0,'size':URLlength[URL],'query':{'match':{'url':URL}}})
	for result in search['hits']['hits']:
		print(CONTER)
		w.append(result['_source']['wword'])
		w.append(result['_source']['frequency'])
		w.append(result['_source']['value'])
		CONTER = CONTER + 1
	end = time.time()
	return render_template('button1.html',W = w,time = round(end-start,2))

@app.route('/button2', methods = ['GET'])
def button2():
	URLS = []
	i = 0
	temp1 = []
	up = 0
	down1 = 0
	down2 = 0
	r = []
	d_r = {}
	txt_size = 0
	text_size = 0
	start = time.time()
	while(1):
		url = request.args.get(str(i))
		if url == None:
			break
		URLS.append(url)
		i += 1
	main_url = request.args.get('main_url')
	#URLS.remove(main_url)
	txt_size = len(URLS)
	SEARCH = es.search(index="web",body={'from':0,'size':URLlength[main_url],'query':{'match':{'url':main_url}}})
	for result in SEARCH['hits']['hits']:
		temp1.append(result['_source']['value'])
	
	for j in range(txt_size):	
		temp2 = []		
		SEARCH = es.search(index="web",body={'from':0,'size':URLlength[URLS[j]],'query':{'match':{'url':URLS[j]}}})
		for result in SEARCH['hits']['hits']:
			temp2.append(result['_source']['value'])
		if(len(temp1) > len(temp2)):
			text_size = len(temp1)
		else:
			text_size = len(temp2)
		for i in range(text_size):
			up += (temp1[i] * temp2[i])
			down1 += (temp1[i] * temp1[i])
			down2 += (temp2[i] * temp2[i])
		r.append(round(up / math.sqrt(down1) / math.sqrt(down2) * 100,2))
		d_r[URLS[j]] = r[j]
		
	d_r = sorted(d_r.items(), key = operator.itemgetter(1),reverse = True)
	end = time.time()
	return render_template('button2.html', simi = d_r, main = main_url , size = txt_size, time = round(end - start,2))

def init(URL,n):
   splits = []
   sub_splits = []
   final = []
   result = []
   res = requests.get(URL)
   frequency = {}
   html = BeautifulSoup(res.content, "html.parser")

   all_link = html.find_all("p")
   total_sentance = 0
   max_freq = 0
   judge = 0

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
      if i[1] > max_freq :
         max_freq = i[1]
   for i in frequency:
      judge = 0
      for j in all_link:
         sub_splits = re.sub('<sup.*?>.*?</sup>','',str(j),0)
         sub_splits = re.sub('<.+?>','',sub_splits,0)
         sub_splits = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','',sub_splits).lower().split()
         if i[0] in sub_splits:
            judge += 1
      final.append(0.5 * i[1] / max_freq * math.log10(total_sentance / judge))

   for i in frequency :
      index = final.index(max(final))
      doc = {'url':URL,'wword':frequency[index][0],'frequency':frequency[index][1],'value':round(final[index],5)}
      res = es.index(index="web",doc_type='word',body=doc)
      print(res)
      final[index] = 0
   URLlength[URL] = len(frequency)
   return frequency

if __name__ == '__main__':
    es = Elasticsearch()
    #if es.indices.exists(index="web"):
    #    es.indices.delete(index="web")
    #print(es.indices.create(index="web"))    
    app.run(debug=False,host ="127.0.0.1",port ="5000")
