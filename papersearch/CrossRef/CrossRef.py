#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 19:22:29 2020

@author: alfonso


Query CrossReference APIs (no registration required) 

"""


import re
import requests
from time import sleep
import json

class CrossRef():
    
    def __init__(self):
        self.name = 'CrossReference'
        self.url = "https://api.crossref.org/works?query="
        
    def info(self):
        info = """CrossRef is a wrapper for papers on CrossReference. It returns:
            doi,
            authors (name only)
            full date
            venue/pub☻lisher
            
        It doesn't return full text, abstract, citations, references nor topics. """
        
        return info
        
    def get(self, query):
        """ 
        Get a paper or a list of papers from CrossReference from its (their) title(s).  
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
                sleep(3)
            
            return res
        
        else:
            print('CrossRef.get() requires a string or a list of strings as input')
            
        
        
           
    def __get_paper(self, title):
        """ Get a JSON object, a paper with title = 'title' from CrossReference. Uses APIs. """
        
        t = re.sub(r'[^a-zA-Z0-9 ]+', ' ', title)
        t = re.sub('[ ]+', '+', t)
        
        url = self.url + t + '&rows=1'
        
        try:
            req = requests.get(url, timeout = None)
            
        except Exception as e:
            print('CrossRef: Bad request with paper {}: {}'.format(title, e))
            return None
        
        try:
            p = json.loads(req.text)        
            p = p['message']['items'][0]
            
            if not self.__check_title(title, p['title'][0]):
                raise ValueError('titles are different!')
                
            print('Got "{}"'.format(title))
            return p
        except:
            print('CrossRef paper not found: "{}"'.format(title))
            return None
        
        
        
        
    def search(self, query, max_res = None, offset = 0):
        """ 
        Search a query on CrossReference. Uses APIs.
        No cursor needed, it navigates through pages with rows and offset.
        """
        
        chunk = 500
        
                   
        offset_ = offset
        res = []
        
        remaining = max_res if max_res != None else chunk
        
        
        while remaining > 0:
            
            chunk = min(remaining, chunk) if max_res != None else chunk 
            
            num, paper_list = self.__search_page(query, chunk, offset_)
            res += paper_list
            
            
            if max_res != None:
                remaining = min(int(num), max_res) - len(res)
            else:
                remaining = int(num) - len(res)  
                            
            offset_ = offset + len(res)
            
            print("Got {}/{} for q = {}".format(len(res), num, query))
            sleep(1)
                
        return res
        
    
    
    
    def search_size(self, query):
        """ Returns the number of results for the query in CrossReference. Uses APIs. """
        
        num, _ = self.__search_page(query, 1, 1)
        return int(num)
    
    
    
    
    def __search_page(self, query, n, offset):
        """ 
        Returns a chunk of the results of a query on CrossReference. Uses APIs.
        No cursoring is needed, it paginates through rows + offset.
        """
        
        q = re.sub(r'[^a-zA-Z0-9 ]+', '', query)
        q = re.sub('[ ]+', '+', q)

        q = "{}{}&rows={}&offset={}".format(self.url, q, n, offset)

        print(q)
        
        try:
            req = requests.get(q, timeout = None)
        except Exception as e:
            print('CrossRef > search \t Bad request with search {}: {}'.format(query, e))
            return None

        try:
            p = json.loads(req.text)
            q = p['message']['total-results']
            p = p['message']['items']
            
            return q, p
        
        except Exception as e:
            raise ValueError('"{}": paper not found.'.format(query))
            
            
            
    def __search_cursor(self, query, max_res):
        """ 
        Search a query on CrossReference. Uses APIs.
        It uses cursoring.
        """
        
        
        res = [] 
        cursor = '*'
        num = -1
        
        while cursor != '':
            
            q, cursor, paper_list = self.__search_page_cursoring(query, cursor, num)
            num = q
            
            if len(paper_list) == 0:
                break            
            
            res += paper_list
            
            print("Got {} for q = {}".format(len(res), query))
            sleep(1)
            
            if max_res != None and len(res) > max_res:
                break
                
        return res[:max_res]
        
    
    def __search_page_cursoring(self, query, cursor, total_results):
        """ 
        Returns a chunk of the results of a query on CrossReference. Uses APIs.
        It uses cursoring.
        """
        
        print('Cursoring: {}'.format(cursor))
        q = re.sub(r'[^a-zA-Z0-9 ]+', '', query)
        q = re.sub('[ ]+', '+', q)

        q = "{}{}&rows=100&cursor={}".format(self.url, q, cursor)
        
        try:
            req = requests.get(q, timeout = None)
        except Exception as e:
            print('CrossRef > search \t Bad request with search {}: {}'.format(query, e))
            return None
        
        try:
            
            p = json.loads(req.text)
            
            if total_results == -1:
                q = p['message']['total-results']
            else:
                q = total_results
                
            nc = p['message']['next-cursor']
            
            p = p['message']['items']
            
            
            return q, nc, p
        
        except Exception as e:
            print(e)
            raise ValueError('"{}": paper not found.'.format(query))
            
            
    def format(self, paper):
        p = {
        'id': '',
        'title': paper['title'][0],
        'abstract': '',
        'doi': paper['DOI'],
        'date': paper['created']['date-time'][:10],
        'authors': [{'name': paper['author'][i]['given'] + ' ' + paper['author'][i]['family'], 'id-internal': '', 'id-external': ''} for i in range(len(paper['author']))],
        'url': {'full': paper['URL'], 'pdf': ''},
        'publisher-venue': paper['publisher'],
        'type': paper['type'],
        'citations': paper['is-referenced-by-count'],
        'references': paper['references-count'],
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

#&cursor=*