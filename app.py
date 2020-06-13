#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import time

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('start.html')

@app.route('/analyze', methods=['GET'])
def analyze():
	if request.method == 'GET':
		start = time.time()
		URL = request.args.get('url')
		w = s(URL)
		end = time.time()
		t = round(end -start,2)
		return render_template('analyze.html', url=URL,word_num = len(w),time = t)

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

if __name__ == '__main__':
    app.run(debug=False,host ="127.0.0.1",port ="5000")
