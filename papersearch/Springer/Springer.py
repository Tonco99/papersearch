#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 10:08:40 2020

@author: alfonso
"""


import re
import requests
from time import sleep
import json

class Springer():
    
    def __init__(self):
        self.name = 'Springer Nature'
        self.url = 'http://api.springer.com/meta/v2/json?api_key=2586e9475a3de6c6a749a63e41618238&q='
        
    def info(self):
        info = """Springer is a wrapper for papers on Springer Nature. It returns:
            doi (and isbn),
            abstract,
            authors (name only)
            full date
            venue.
            
        It doesn't return full text, citations, references nor topics. """
        
        return info
    
    def get(self, query):
        """ 
        Get a paper or a list of papers from Springer Nature by its(their) title(s).  
        """
        
        # If query is a single string
        if isinstance(query, str):
            paper = self.__get_paper(query)
            
            if paper != None:
                return paper
        
        elif isinstance(query, list):
            
            res = []
            
            for title in query:
                paper = self.__get_paper(title)
                
                if paper != None:
                    res += [paper]
                sleep(1)
            
            return res
        
        else:
            print('Springer.get() requires a string or a list of strings as input')
            
        
        
           
    def __get_paper(self, title):
        """ Get a JSON object, a paper with the requested title from Springer Nature. Uses APIs. """
        
        t = re.sub(r'[^a-zA-Z0-9 ]+', ' ', title.lower())
        t = re.sub('[ ]+', '%20', t)
        t = 'title:%22' + t + '%22'

        url = self.url + t + '&s=1&p=1'
        
        try:
            req = requests.get(url, timeout = None)
            
        except Exception as e:
            print('Springer: Bad request with paper {}: {}'.format(title, e))
            return None
        
        p = json.loads(req.text)
    
        try:
            p = p['records'][0]
            
            if not self.__check_title(title, p['title']):
                raise ValueError('titles are different!')
                
            print('Got "{}"'.format(title))
            return p
        except:
            print('Springer paper not found: "{}"'.format(title))
            return None
        
        
        
        
    def search(self, query, max_res = None):
        """ Search a query on Springer Nature. Uses APIs. """
        
        chunk = 100 
        offset = 0
        res = []
        
        remaining = max_res if max_res != None else chunk
        
        
        while remaining > 0:
            
            chunk = min(remaining, chunk) if max_res != None else chunk 
            
            paper_list = self.__search_page(query, chunk, offset)
            
            answers = len(paper_list)
            if answers == 0:
                break
            
            res += paper_list
            
            
            if max_res != None:
                remaining = max_res - len(res)  
                            
            offset = len(res)
            
            print("Got {} for q = {}".format(len(res), query))
            sleep(1)
        
            
        return res
        
    
    def search_size(self, query):
        """ Returns the number of results for the query in Springer Nature. Uses APIs. """
        
        print("Springer Nature can't return the number of hits for a given query.")
        return 0

   
        
    def __search_page(self, query, n, offset):
        """ Returns a chunk of the results of a query on Springer Nature. Uses APIs. """
        
        t = re.sub(r'[^a-zA-Z0-9 ]+', ' ', query.lower())
        t = re.sub('[ ]+', '%20', t)
        t = 'title:%22' + t + '%22'

        q = self.url + t + '&s={}&p={}'.format(offset, n)
        
        try:
            req = requests.get(q, timeout = None)
        except Exception as e:
            print('Springer > search \t Bad request with search {}: {}'.format(query, e))
            return None
        
        
        p = json.loads(req.text)
    
        try:
            p = p['records']
            return p
        
        except Exception as e:
            raise ValueError('"{}": paper not found.'.format(query))
            
            
    def format(self, paper):
        p = {
        'id': '',
        'title': paper['title'],
        'abstract': paper['abstract'],
        'doi': paper['doi'],
        'date': paper['publicationDate'],
        'authors': [{'name': paper['creators'][i]['creator'], 'id-internal': '', 'id-external': ''} for i in range(len(paper['creators']))],
        'url': {'full': paper['url'][0]['value'], 'pdf': paper['url'][1]['value']},
        'publisher-venue': paper['publisher'],
        'type': paper['publicationType'],
        'citations': '',
        'references': '',
        'citation-list': [],
        'reference-list': []
        }
        
        return p
        
        
            
    def __check_title(self, Sa, Sb):
        
        Sa = re.sub('[^a-z0-9]', '', Sa.lower())
        Sa = ''.join(sorted(Sa))
        
        Sb = re.sub('[^a-z0-9]', '', Sb.lower())
        Sb = ''.join(sorted(Sb))
        
        L = min(len(Sa), len(Sb))
        
        Sa = Sa[:L]
        Sb = Sb[:L]
        
        return Sa == Sb

