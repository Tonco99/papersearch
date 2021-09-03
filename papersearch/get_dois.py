#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 18:59:32 2020

@author: alfonso
"""

import json
from SemanticPaper import SemanticPaper
from time import sleep
import pickle

semantic = SemanticPaper()

with open('/Users/anton/Downloads/fn_ditinco.json', 'r') as fr:
    fn = json.load(fr)
    
doi_list = [f['DOI'] for f in fn if 'DOI' in f.keys()]
res = []

for data in fn:
    print(data.keys())
"""

for i, doi in enumerate(doi_list):
    
    paper = semantic.get_by_doi(doi, verbose = False)
    
    if paper:
        res += [paper]
        
    if i != 0 and (i % 100) == 0:
        sleep(5*60 + 1)
        print("Got {}/{} papers. Taking 5...".format(len(res), i))
        
with open('/Users/anton/Downloads/semantic_refn.json', 'w') as fw:
    json.dump(res, fw)
"""