#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 11:49:16 2020

@author: alfonso


Queries to SemanticScholar are free (no registration required, nor limits),
but you can find a paper only if you know its ID.

We search "semanticscholar" + title of the paper on Google, using SERP API.
Check it on https://serpapi.com/playground and https://github.com/serpapi/google-search-results-python

"""

"""
Forse obsolete nella sintassi

from serpapi.google_search_results import GoogleSearchResults

"""

from serpapi.google_search import GoogleSearch
import requests
import json
from time import sleep
import re

class SemanticPaper:
    
    def __init__(self):
        self.name = 'Semantic Scholar'
        self.client = GoogleSearch({"serp_api_key": "147feb6adc2672a612ac3f8a902358036926a4c1f3f2abf1e04e01092fad2146", "num": 1})
        
    def info(self):
        info = """
        SemanticPaper is a wrapper for papers on SemanticScholar. It returns:
            doi
            abstract
            authors (Semantic id)
            citation list
            references list
            year
            venue.
            
        It doesn't return the full text nor the full date. """
        
        return info
        
    def get(self, query):
        """ 
        Get a paper from SemanticScholar from its (their) title(s).  
        """
        
        # If query is a single string
        if isinstance(query, str):
            S2_id = self.__get_Semantic_id(query) # get SS id from Google
            paper = self.__get_paper(S2_id, query) # get paper
                
            if paper != None:
                return paper
        
        
        # If query is a list
        elif isinstance(query, list):
            
            res = []
            
            for title in query:
                S2_id = self.__get_Semantic_id(title) 
                paper = self.__get_paper(S2_id, title) # get paper
                
                if paper != None:
                    res += [paper]
                
                sleep(1)
                
            return res
        
        
        else:
            print('SemanticPaper.get() requires a string or a list of strings as input')
            
            
    
    
    def __get_paper(self, S2_id, title):
        """ Get a JSON object, a paper with ID = S2_id from SemanticScholar. Uses APIs. """
        
        url = "https://api.semanticscholar.org/v1/paper/" + S2_id + '?include_unknown_references=true'
        
        try:
            req = requests.get(url, timeout = None)
            p =  json.loads(req.text)
            
            if not self.__check_title(title, p['title']): # check if retrieved paper is correct
                raise ValueError('titles are different!')
                
            print('Got "{}"'.format(title))
            return p
        
        except Exception as e:
            print('SemanticPaper paper not found for "{}": {}'.format(title, e))
            return None

    
    def get_by_doi(self, doi, verbose = True):
        """ Get a JSON object, a paper with ID = S2_id from SemanticScholar. Uses APIs. """
        
        url = "https://api.semanticscholar.org/v1/paper/" + doi + '?include_unknown_references=true'
        
        try:
            req = requests.get(url, timeout = None)
            p =  json.loads(req.text)
           
            if verbose:
                print('Got "{}"'.format(doi))
            return p
        
        except Exception as e:
            print('SemanticPaper paper not found for "{}": {}'.format(doi, e))
            return None
        
    
    def __get_Semantic_id(self, title):
        """ Search one title on Google and retrieve its SemanticScholar ID. """
        
        self.client.params_dict["q"] = "https://www.semanticscholar.org: " + title
        
        data = self.client.get_json()
        
        try:
                
            data = data['organic_results'][0]['link'].split('/')[-1] # it takes the first entry!
        
            print('Got SemanticScholar ID for "{}"'.format(title))
            return data
    
        except Exception as e:
            print('SemanticPaper ID not found for "{}": {}'.format(title, e))
            print(e)
            return None
    
    
    def search(self, query, max_res = None):
        """ Search a query on Google and retrieve their SemanticScholar ID. """
        
        chunk = 100 
        offset = 0
        res = []
        
        remaining = max_res if max_res != None else chunk
        
        
        while remaining > 0:
            
            chunk = min(remaining, chunk) if max_res != None else chunk 
            
            num, paper_list = self.__search_page(query, chunk, offset)
            res += paper_list
            
            
            if max_res != None:
                remaining = max_res - len(res)
            else:
                remaining = int(num) - len(res)  
                            
            offset = len(res)
            
            print("Got {}/{} for q = {}".format(len(res), num, query))
            sleep(1)
        
        res_ = []
        
        for p in res:
            res_ += [self.__get_paper(p['link'].split('/')[-1], p['title'].replace(' | Semantic Scholar', ''))]
            sleep(1)
            
        return res_
        
    
    def search_size(self, query):
        """ Returns the number of results for the query in Semantic Scholar. Uses APIs. """
        
        num, _ = self.__search_page(query, 1, 1)
        return int(num)
    
    
    def __search_page(self, query, num, start):
        """ Search a query on Google and retrieve SemanticScholar ids """
        
        
        self.client.params_dict["q"] = "https://www.semanticscholar.org: " + query
        self.client.params_dict["num"] = num
        self.client.params_dict["start"] = start
        
        
        data = self.client.get_json()
        
        try:
            q = int(data['search_information']['total_results'])
            data = [d for d in data['organic_results'] if 'semanticscholar' in d['link']]
            return q, data
    
        except Exception as e:
            print('SemanticPaper research failed for "{}": {}'.format(query, e))
            return None
    
    def format(self, paper):
        p = {
        'id': paper['paperId'],
        'title': paper['title'],
        'abstract': paper['abstract'],
        'doi': paper['doi'],
        'date': paper['year'],
        'authors': [{'name': paper['authors'][i]['name'], 'id-internal': paper['authors'][i]['authorId'], 'id-external': ''} for i in range(len(paper['authors']))],
        'url': {'full': paper['url'], 'pdf': ''},
        'publisher-venue': paper['venue'], 
        'type': '',       
        'citations': len(paper['citations']),
        'references': len(paper['references']),
        'citation-list': paper['citations'],
        'reference-list': paper['references']
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