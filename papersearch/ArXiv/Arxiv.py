#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:03:58 2020

@author: alfonso
"""
import hashlib

"""
Query arxiv APIs (no registration required) 

"""

import re
import xmltodict
import requests
from time import sleep
import json

class Arxiv():

    def __init__(self):
        self.name = 'Arxiv'
        self.url = "http://export.arxiv.org/api/query?search_query="

    def info(self):
        info = """Arxiv is a wrapper for papers on arxiv. It returns:
            full text (link),
            abstract,
            authors (name only)
            full date
            venue.
            
        It doesn't return doi, citations, references nor topics. """

        return info

    def get(self, query):
        """ 
        Get a paper or a list of papers from Arxiv by its(their) title(s).  
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
        """ Get a JSON object, a paper with the requested title from Arxiv. Uses APIs. """

        t = re.sub(r'[^a-zA-Z0-9 ]+', ' ', title.lower())
        t = re.sub('[ ]+', '+', t)

        url = self.url + t + '&max_results=1'

        try:
            req = requests.get(url, timeout = None)

        except Exception as e:
            print('Dblp: Bad request with paper {}: {}'.format(title, e))
            return None

        p = xmltodict.parse(req.text)
        p = json.loads(json.dumps(p))

        try:
            p = p['feed']['entry']

            if not self.__check_title(title, p['title']):
                raise ValueError('titles are different!')

            print('Got "{}"'.format(title))
            return p
        except:
            print('Arxiv paper not found: "{}"'.format(title))
            return None




    def search(self, query, max_res):
        """ Search a query on Arxiv. Uses APIs. """

        chunk = 500
        offset = 0
        res = []
        failures = 0
        remaining = max_res if max_res != None else chunk

        while remaining > 0:

            # inserire numero massimo di tentativi

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
        """ Returns the number of results for the query in Arxiv. Uses APIs. """
        failures = 0
        num, _, failures = self.__search_page(query, 1, 1,failures)
        if failures == 0:
            return int(num)
        else:
            return failures


    def __search_page(self, query, n, offset, failures):
        """ Returns a chunk of the results of a query on Arxiv. Uses APIs. """

        q = re.sub(r'[^a-zA-Z0-9 ]+', ' ', query.lower())
        q = re.sub('[ ]+', '+', q)
        qf = '"' + q + '"'

        q = "{}{}&max_results={}&start={}".format(self.url, qf, n, offset)

        try:
            req = requests.get(q, timeout = None)
        except Exception as e:
            print('arXiv > search \t Bad request with search {}: {}'.format(query, e))
            return None

        p = xmltodict.parse(req.text)
        p = json.loads(json.dumps(p))

        try:
            q = p['feed']['opensearch:totalResults']['#text']
            p = p['feed']['entry']
            return q, p, failures

        except Exception as e:
            print("Error_Arxiv: ", e)
            failures += 1
            return -1, None, failures



    def format(self, paper):
        if 'authors' in paper.keys():
            var = [{'name': paper['author'][i]['name'],
                     'id-internal': '',
                     'id-external': ''} for i in range(len(paper['author']))] if type(paper['author']) is list else {'name': paper['author']['name'] ,
                     'id-internal': '',
                    'id-external': ''}
        else:
            var = {'name': '', 'id-internal': '', 'id-external': ''}

        p = {
        'id': int(hashlib.blake2s("{}{}".format(paper['id'].split('/')[1],paper['title']).encode(), digest_size = 4).hexdigest(),base=16),
        'title': paper['title'],
        'abstract': paper['summary'],
        'doi': paper['arxiv:doi']['#text'].lower() if 'arxiv:doi' in paper.keys() else '',
        'date': paper['published'][:10],
        'authors': var,
        'url': {'full': paper['id'], 'pdf': ''},
        'publisher-venue': re.search("Accepted at [^']+", str(paper)).group(0).replace('Accepted at ', '') if 'Accepted at ' in str(paper) else '',
        'type': '',
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

