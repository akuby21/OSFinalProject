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
import urllib
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
app = Flask(__name__)
list_w = []
freq = []
results = []
URLlength = {}
URL = []
URL_form = ["https://"]
@app.route('/')
def index():
	return render_template('start.html')

@app.route('/analyze', methods=['GET','POST'])
def analyze():
	idNum = 0
	WordList = []
	ExecuteTime = []
	ex_url = []
	strings = ""
	if request.method == 'POST':
		status = []
		f = request.files['FileName']
		filename = secure_filename(f.filename)
		urls = f.readlines()
		for i in urls:
			start = time.time()
			i = i.decode('utf-8').rstrip()
			URL.append(i)

			if(is_valid_url(i)):
				try:
					RES = urlopen(i)
					w = init(i,idNum)
					end = time.time()
					ex_url.append(i)
					WordList.append(len(w))
					status.append("성공")
					ExecuteTime.append(round(end-start,2))
				except HTTPError as e:
					end = time.time()
					WordList.append(0);
					status.append("실패")
					ExecuteTime.append(round(end-start,2))
			else:
				end = time.time()
				WordList.append(0);
				status.append("실패")
				ExecuteTime.append(round(end-start,2))
			idNum = idNum + 1
		for i in range(len(urls)) :
			for j in range(i+1 , len(urls)):
				if(urls[i] == urls[j]):
					status[j] = "중복"
		for i in range(len(ex_url)):
			strings += repr(i)+"="+str(ex_url[i])+"&"
		return render_template('analyze.html',num = len(WordList),urls =URL,test1 = WordList,test2 = ExecuteTime,status = status,full_url = strings)
	if request.method == 'GET':
		status = []
		URLP = []
		url = request.args.get('url')
		print(is_valid_url(url))
		if(is_valid_url(url)):
			try:
				RES = urlopen(url)
				start = time.time()
				w = init(url,0)
				if (w == 0):
					strings = "0=" + url + "&"
					return render_template('analyze.html',num=1,urls=URL,test1=0,test2=0,status="실패",full_url = strings);
				end = time.time()
				t = round(end -start,2)
				WordList.append(len(w))
				URL.append(url)
				status.append("성공")
				ExecuteTime.append(t)
			except HTTPError as e:
				start = time.time()
				URL.append(url)
				status.append("실패")
				WordList = []
				end = time.time()
				t = round(end -start,2)
				ExecuteTime.append(t)
		else:
			start = time.time()
			URL.append(url)
			status.append("실패")
			WordList = []
			end = time.time()
			t = round(end -start,2)
			ExecuteTime.append(t)
		strings = "0=" + url + "&"
		URLP.append(url)
		return render_template('analyze.html', num = 1,urls=URLP,test1 = WordList,test2 = ExecuteTime, status = status,full_url = strings)

@app.route('/button1', methods = ['GET'])
def button1():
	w = []
	CONTER = 1;
	URL = request.args.get('url')
	start = time.time()

	search = es.search(index="web",body={'from':0,'size':URLlength[URL],'query':{'match':{'url':URL}}})
	for result in search['hits']['hits']:
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
	status = []
	non_overlap_status = []
	overlap_size = 0
	JUDGE = 0
	start = time.time()
	while(1):
		url = request.args.get(str(i))
		if url == None:
			break
		URLS.append(url)
		i += 1
	main_url = request.args.get('main_url')
	URLS.remove(main_url)
	txt_size = len(URLS)
	SEARCH = es.search(index="web",body={'from':0,'size':URLlength[main_url],'query':{'match':{'url':main_url}}})
	for i in range(txt_size) :
		status.append([])
		status[i].append(URLS[i])
		status[i].append("성공")
	for i in range(txt_size) :
		for j in range(i+1 , txt_size):
			if(status[i][0] == status[j][0]):
				status[i][1] = "중복"
				status[j][1] = "중복"
			if(status[i][0] == main_url):
				status[i][1] = "메인과중복"
			if(status[j][0] == main_url):
				status[j][1] = "메인과중복"
	for result in SEARCH['hits']['hits']:
		temp1.append(result['_source']['value'])
	for j in range(txt_size):
		temp2 = []
		up = 0
		down1 = 0
		down2 = 0
		SEARCH = es.search(index="web",body={'from':0,'size':URLlength[URLS[j]],'query':{'match':{'url':URLS[j]}}})
		for result in SEARCH['hits']['hits']:
			temp2.append(result['_source']['value'])
		if(len(temp1) < len(temp2)):
			text_size = len(temp1)
		else:
			text_size = len(temp2)
		for i in range(text_size):
			up += (temp1[i] * temp2[i])
			down1 += (temp1[i] * temp1[i])
			down2 += (temp2[i] * temp2[i])
		NUM = round(up / math.sqrt(down1) / math.sqrt(down2) * 100,2)
		r.append(NUM)
		d_r[URLS[j]] = r[j]
	d_r = sorted(d_r.items(), key = operator.itemgetter(1),reverse = True)
	for i in range(len(d_r)):
		JUDGE = 0
		for j in range(txt_size):
			if((JUDGE == 0) and (d_r[i][0] == status[j][0])):
				non_overlap_status.append(status[j][1])
				JUDGE = 1
	end = time.time()

	return render_template('button2.html', simi = d_r, main = main_url , size = len(d_r), time = round(end - start,2),status = non_overlap_status)

def is_valid_url(url):
   regex = re.compile(
      r'^https?://'  # http:// or https://
      r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
      r'localhost|'  # localhost...
      r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
      r'(?::\d+)?'  # optional port
      r'(?:/?|[/?]\S+)$', re.IGNORECASE)
   return url is not None and regex.search(url)

def init(URL,n):
   splits = []
   sub_splits = []
   final = []
   result = []
   res = requests.get(URL)
   frequency = {}
   html = BeautifulSoup(res.content, "html.parser")
   if html == None:
	   return 0;
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
      final[index] = 0
   URLlength[URL] = len(frequency)
   return frequency

if __name__ == '__main__':
    es = Elasticsearch()
    app.run(debug=False,host ="127.0.0.1",port ="5000")

