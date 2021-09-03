#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 15:35:00 2020

@author: alfonso
"""
import hashlib

"""

Query dblp APIs (no registration required) 

"""

import re
import xmltodict
import requests
from time import sleep
import json

class Dblp():
    
    def __init__(self):
        self.name = 'DBLP'
        self.url = "https://dblp.org/search/publ/api?q="
        
    def info(self):
        info = """Dblp is a wrapper for papers on dblp. It returns:
            doi
            authors (Dblp id)
            year
            venue.
            
        It doesn't return the full text, the abstract, the citations, the references, the topics, the full date. """
        
        return info
 
        
    def get(self, query):
        """ 
        Get a paper or a list of papers from DBPL from its (their) title(s).  
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
            print('Dblp.get() requires a string or a list of strings as input')
            
        
        
           
    def __get_paper(self, title):
        """ Get a JSON object, a paper with title = 'title' from DBPL. Uses APIs. """
        
        t = re.sub(r'[^a-zA-Z0-9 ]+', ' ', title)
        t = re.sub('[ ]+', '_', t)
        
        url = self.url + t + '&h=1'
        
        try:
            req = requests.get(url, timeout = None)
            
        except Exception as e:
            print('Dblp: Bad request with paper {}: {}'.format(title, e))
            return None
        
        p = xmltodict.parse(req.text)
        p = json.loads(json.dumps(p['result']))
        
        try:
            p = p['hits']['hit']
            
            if not self.__check_title(title, p['info']['title']):
                raise ValueError('titles are different!')
                
            print('Got "{}"'.format(title))
            return p
        except:
            print('Dblp paper not found: "{}"'.format(title))
            return None
        
        
        
        
    def search(self, query, max_res):
        """ Search a query on DBPL. Uses APIs. """
        
        chunk = 500 
        offset = 0
        res = []
        failures = 0
        remaining = max_res if max_res != None else chunk

        while remaining > 0:

            chunk = min(remaining, chunk) if max_res != None else chunk
            
            num, paper_list, failures = self.__search_page(query, chunk, offset, failures)
            if num != -1:
                res += paper_list

                if max_res != None:
                    remaining = min(int(num), max_res) - len(res)
                else:
                    remaining = int(num) - len(res)

                offset = len(res)

                # print("Got {}/{} for q = {}".format(len(res), num, query))
            else:
                print("Error: ", failures)
            sleep(1)

            if failures > 5:
                remaining=0
            
        return res
        
    def search_size(self, query):
        """ Returns the number of results for the query in Dblp. Uses APIs. """
        failures = 0
        num, _, failures = self.__search_page(query, 1, 1, failures)
        if failures == 0:
            return int(num)
        else:
            return failures

    def __search_page(self, query, n, offset, failures):
        """ Returns a chunk of the results of a query on DBPL. Uses APIs. """
        
        q = re.sub(r'[^a-zA-Z0-9 ]+', ' ', query)
        q = re.sub('[ ]+', '_', q)
        q = "{}{}&h={}&f={}".format(self.url, q, n, offset)
        
        try:
            req = requests.get(q, timeout = None)
        except Exception as e:
            print('dblp > search \t Bad request with search {}: {}'.format(query, e))
            return None
        
        p = xmltodict.parse(req.text)
        p = json.loads(json.dumps(p['result']))
        
        try:
            
            p = p['hits']
            return p['@total'], p['hit'], failures
        
        except Exception as e:
            print("Error_DBLP: ", e)
            failures += 1
            return -1, None, failures
            
            
    
    def format(self, paper):
        if 'authors' in paper['info'].keys():
            var = [{'name': paper['info']['authors']['author'][i]['#text'],
                     'id-internal': paper['info']['authors']['author'][i]['@pid'],
                    'id-external': ''} for i in range(len(paper['info']['authors']['author']))] if type(paper['info']['authors']['author']) is list else {'name': paper['info']['authors']['author']['#text'] ,
                     'id-internal': paper['info']['authors']['author']['@pid'],
                    'id-external': ''}
        else:
            var = {'name': '', 'id-internal': '', 'id-external': ''}
        p = {
        'id': int(hashlib.blake2s("{}{}".format(paper['@id'],paper['info']['title']).encode(), digest_size = 4).hexdigest(),base=16),
        'title': paper['info']['title'],
        'abstract': '',
        'doi': paper['info']['doi'].lower() if 'doi' in paper['info'].keys() else '',
        'date': paper['info']['year'],
        'authors': var,
        'url': {'full': paper['url'], 'pdf': ''},
        'publisher-venue': paper['info']['venue'] if 'venue' in paper['info'].keys() else '',
        'type': paper['info']['type'],
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

