#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('start.html')

@app.route('/analyze', methods=['GET'])
def analyze():
	if request.method == 'GET':
		URL = request.args.get('url')
		w = s(URL)
		return render_template('analyze.html', word = w)

def s(URL):
	res = requests.get(URL)
	html = BeautifulSoup(res.content, "html.parser")
	all_link = html.find_all("p")
	list_word = []
	word_counter = []
	size = 1

	for link in all_link: 
		word = link.text.split(' ')	
		for i in range(0,len(word)):
			word[i] = word[i].replace(",","")
			word[i] = word[i].replace(".","")
			word[i] = word[i].replace("\n","")
			word[i] = word[i].replace("!","")
			word[i] = word[i].replace("?","")
			word[i] = word[i].replace("(","")
			word[i] = word[i].replace(")","")
			word[i] = word[i].replace("[","")
			word[i] = word[i].replace("]","")
			word[i] = word[i].replace("{","")
			word[i] = word[i].replace("}","")
			word[i] = word[i].replace("\"","")
			word[i] = word[i].replace("'","")
			word[i] = word[i].replace("<","")
			word[i] = word[i].replace(">","")
			word[i] = word[i].replace(";","")
			word[i] = word[i].replace("-","")
			word[i] = word[i].replace("~","")
			word[i] = word[i].replace("`","")
			word[i] = word[i].replace(":","")
			word[i] = word[i].replace(";","")
			word[i] = word[i].lower()	
			judge = -1
			for j in range(0,len(list_word)):
				if(word[i] == list_word[j]):
					judge = j
					break
			if(judge == -1):
				list_word.append(word[i])
				word_counter.append(1)	
			else:
				word_counter[judge] += 1

	return list_word

if __name__ == '__main__':
    app.run(debug=False,host ="127.0.0.1",port ="5000")
