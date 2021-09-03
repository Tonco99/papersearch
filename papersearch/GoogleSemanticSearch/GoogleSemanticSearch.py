#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 11:56:15 2020

@author: alfonso
"""

"""
Forse obsolete nella sintassi

from serpapi.google_search_results import GoogleSearchResults
from serpapi.google_scholar_search_results import GoogleScholarSearchResults

"""

from serpapi.google_search import GoogleSearch
from time import sleep
import re
from queue import Queue
from datetime import datetime
from serpapi.google_scholar_search import GoogleScholarSearch


class GoogleSemanticSearch:

    def __init__(self):
        self.client = GoogleSearch({"serp_api_key": "bea2cfe79899deac6b5bdbd78b1efc1719383fc80792a11bb39656384339db88", "num": 1})
        self.client_scholar = GoogleScholarSearch({"serp_api_key": "bea2cfe79899deac6b5bdbd78b1efc1719383fc80792a11bb39656384339db88"})


    def get_Semantic(self, title):
        """ Search one title on SemanticScholar (through Google) and retrieve its ID. """

        self.client.params_dict["q"] = "https://www.semanticscholar.org: " + title

        try:
            data = self.client.get_json()
        except Exception as e:
            print('GoogleSearch > get_Semantic_id \t Failed to search {}: {}'.format(title, e))
            return None

        return data['organic_results'][0]['link'].split('/')[-1] # it takes the first entry!


    def get_Semantic_list(self, title_list, asynchronous = False):
        """ 
        Search a list of titles on SemanticScholar (through Google) and retrieve their IDs. 
        This is a wrapper.
        If asynchronous == False, just iterate over title_list and perform a query per time.
        If asynchronous == True, use the endpoint of GoogleSearch for batch queries. 
        """

        if asynchronous:
            return self.__get_Semantic_bulk(title_list)

        else:
            return self.__get_Semantic_list_iterate(title_list)




    def __get_Semantic_list_iterate(self, title_list):
        """ Search a list of titles on SemanticScholar (through Google) and retrieve their IDs. """

        data = []
        for title in title_list:
            data += [self.get_Semantic(title)]
            print('Got SemanticScholar ID for "{}"'.format(title))
        return data




    def __get_Semantic_bulk(self, title_list):
        """ Search a list of titles on SemanticScholar (through asynchronous search) and retrieve their IDs. """

        # store searches
        search_queue = Queue()

        for title in title_list:

            print("execute async search: q = {}".format(title))

            # Serp API client
            client = GoogleSearch({
                  "q": "https://www.semanticscholar.org: " + title,
                  "async": True,
                  "no_cache": True,
                  "serp_api_key": self.serp_api_key,
                  "num": 1
                  })

            search = client.get_json()
            search_queue.put(search)

        print("wait until all search statuses are cached or success")

        while not search_queue.empty():
            # Create regular client
            client = GoogleSearch({"async": True,
                                          "serp_api_key": self.serp_api_key})
            search = search_queue.get()
            search_id = search['search_metadata']['id']


            search_archived =  client.get_search_archive(search_id)
            now = datetime.now()
            print("{}:{}:{}: status = {}".format(now.hour, now.minute, now.second, search_archived['search_metadata']['status']))

            # check status
            if re.search('Cached|Success', search_archived['search_metadata']['status']):
                print(search_id + ": search done with p = " + search_archived['search_parameters']['start'])
            else:
                # requeue search_queue
                search_queue.put(search)

            # wait 
            sleep(2)

        # self.assertIsNotNone(results["local_results"][0]["title"])
        print('all searches completed')
        return search_archived


    def get_Scholar_Search(self, q, num_results = 20):
        """ Search a paper on Google Scholar and return its json. """

        data = []
        page = 0
        for skip in range(0, num_results, 20):
            page += 1

            self.client_scholar.params_dict["q"] = q
            self.client_scholar.params_dict["num"] = min(20, num_results - skip)
            self.client_scholar.params_dict["start"] = skip

            data += [self.client_scholar.get_json()]


            sleep(2)

        return data


