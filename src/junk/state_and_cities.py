#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 11:44:25 2018

@author: stealth
"""
import os,sys
try:
    home = os.path.abspath(os.path.dirname(__file__))
except:
    home = '/home/shubham/devel/analytics/src/NLP_utils'

import joblib
from bs4 import BeautifulSoup as BS
import requests

states=[]
cities=[]
urls=[]
response=requests.get('http://districts.nic.in/')
soup=BS(response.text,'lxml')
clas=soup.find('div',{'class':'uppersec'})
for url in clas.findAll('a'):
    urls.append(url['href'])
    states.append(url.getText())
    
print ("states done")

for link in urls:
    response=requests.get(link)
    soup=BS(response.text,'lxml')
    clas=soup.find('div',{'class':'statesec'})
    for url in clas.findAll('a'):
        cities.append(url.getText())
print ("cities done")

joblib.dump(cities,home+'/../../data/cities.txt')
joblib.dump(states,home+'/../../data/states.txt')
print('writing done')