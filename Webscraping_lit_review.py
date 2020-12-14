import openpyxl
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium import webdriver
import re
import requests
from lxml import html
from lxml import etree
import urllib
import re   
import unicodedata
import time
from Bio import Entrez
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

myquery = '"Solid dispersion"'
Entrez.email = 'peterjanverheij@gmail.com'
Entrez.api_key = "417972f25a202935478dc4fa188577ebe008"

titles = []
aims = []
mms = []
ress = []
concs = []
refs = []
abs = []
pmids = []
cited_by = []
mymax = 100
nodes = []
edges = []
new_ids = []
chunk_size = 50  # whatever you like

def search(query,mymax):
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax=str(mymax),
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

def fetch_details_2(id):
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=id)
    results = Entrez.read(handle)
    return results


results = search(myquery,mymax)
id_list = results['IdList'] # list of UIDs

chunk_size = 50 # whatever you like   
for chunk_i in range(0, len(id_list), chunk_size):
    chunk = id_list[chunk_i:chunk_i + chunk_size]
 
    papers = fetch_details(chunk)
    for i, paper in enumerate(papers['PubmedArticle']):
      try:
          data = paper.get('PubmedData')
          data2 = paper.get('MedlineCitation')
          article = data2.get('Article')
          title = article.get('ArticleTitle')
          abstr = article.get('Abstract')
          abstr = abstr.get('AbstractText')
          ref = data.get('ReferenceList')
          refs.append(ref)
          pmids.append(data2.get('PMID'))
          cited_by.append('')
          try:
            aim = abstr[0]
            MM = abstr[1]
            res = abstr[2]
            conc = abstr[3]
            titles.append(title)
            aims.append(aim)
            mms.append(MM)
            ress.append(res)
            concs.append(conc)
            abs.append('')
          except:
            abs.append(abstr[0])
            titles.append(title)
            aims.append('')
            mms.append('')
            ress.append('')
            concs.append('')
      except:
          pass


data = {'title': titles, 'id':pmids,'abs':abs,'aims':aims,'MM':mms,'res':ress,'concl':concs} 
df2 = pd.DataFrame(data) 

for i in range(len(refs)):
  temp = refs[i]
  name=str(pmids[i])
  if temp:
    if name not in nodes:
      nodes.append(name)
    temp2 = temp[0]
    A = temp2.get('Reference')
    for j in range(len(A)):
      temp3 = A[j].get('ArticleIdList')
      try:
        name2 = str(temp3[0])
        if name2 not in nodes:
          nodes.append(name2)
          new_ids.append(name2)

        edges.append((name,name2))
      except:
        pass

g = nx.Graph()
g.add_nodes_from(nodes)
for i in range(len(edges)):
  B = edges[i]
  g.add_edge(B[0], B[1])

color_map = []
for node in nodes:
    if node in pmids:
        color_map.append('blue')
    else:
        color_map.append('red')
plt.subplot(121)

nx.draw(g,node_size=100, node_color=color_map,alpha=0.5)
plt.show()

id_list = new_ids # list of UIDs

for chunk_i in range(0, len(id_list), chunk_size):
    chunk = id_list[chunk_i:chunk_i + chunk_size]
 
    papers = fetch_details(chunk)
    for i, paper in enumerate(papers['PubmedArticle']):
      try:
          data = paper.get('PubmedData')
          data2 = paper.get('MedlineCitation')
          article = data2.get('Article')
          title = article.get('ArticleTitle')
          abstr = article.get('Abstract')
          abstr = abstr.get('AbstractText')
          ref = data.get('ReferenceList')
          refs.append(ref)
          pmids.append(data2.get('PMID'))
          cited_by.append(str(g.degree(str(data2.get('PMID')))))
          try:
            aim = abstr[0]
            MM = abstr[1]
            res = abstr[2]
            conc = abstr[3]
            titles.append(title)
            aims.append(aim)
            mms.append(MM)
            ress.append(res)
            concs.append(conc)
            abs.append('')
          except:
            abs.append(abstr[0])
            titles.append(title)
            aims.append('')
            mms.append('')
            ress.append('')
            concs.append('')
      except:
          pass
data = {'title': titles, 'id':pmids,'abs':abs,'aims':aims,'MM':mms,'res':ress,'concl':concs,'degree':cited_by} 
df2 = pd.DataFrame(data) 


df2.to_excel('output.xlsx') 
conn = sqlite3.connect('TestDB1.db')
c = conn.cursor()
query = 'CREATE TABLE {queryname} {values}'
#c.execute(query.format(queryname=myquery,values=tuple(data.keys())))
conn.commit()
df2.to_sql(myquery, conn, if_exists='replace', index=False)
