#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 15:29:29 2020

@author: alfonso

SemanticPaper gets meta, abstract, cite/reference; it doesn't get full text; it's very expensive
Dblp gets meta;

No one gets day/month, year only

"""
import hashlib
import json
import os
import fnlogger

from SemanticPaper.SemanticPaper import SemanticPaper
from Dblp.Dblp import Dblp
from ArXiv.Arxiv import Arxiv
from CrossRef.CrossRef import CrossRef
from Springer.Springer import Springer

semantic = SemanticPaper()
dblp = Dblp()
arxiv = Arxiv()
cross = CrossRef()
springer = Springer()
logger = fnlogger.init_log('log.log')


def length_doi(list):
    dois = [len(doi) for doi in list]
    dois = {l: dois.count(l) for l in set(dois)}
    return dois


def count(list):
    count = 0
    for doc in list:
        count += 1
    return count


def search_DBLP(keyword):
    if os.path.exists('Dblp/data/dblp_' + keyword + '.json'):
        with open('Dblp/data/dblp_' + keyword + '.json', 'r') as fr:
            fn_dblp = json.load(fr)
        dblp_c = count(fn_dblp)
    else:
        dblp_c = 0

    if dblp.search_size(keyword) != dblp_c:
        fakes_dblp = dblp.search(keyword, max_res=5000)
        with open('Dblp/data/dblp_' + keyword + '.json', 'w') as fw:
            json.dump(fakes_dblp, fw)
    else:
        fakes_dblp = fn_dblp
    return fakes_dblp


def search_ArXiv(keyword):
    if os.path.exists('ArXiv/data/arXiv_' + keyword + '.json'):
        with open('ArXiv/data/arXiv_' + keyword + '.json', 'r') as fr:
            fn_arXiv = json.load(fr)
        arxiv_c = count(fn_arXiv)
    else:
        arxiv_c = 0

    if arxiv.search_size(keyword) != arxiv_c:
        fakes_arXiv = arxiv.search(keyword, max_res=5000)
        with open('ArXiv/data/arXiv_' + keyword + '.json', 'w') as fw:
            json.dump(fakes_arXiv, fw)
    else:
        fakes_arXiv = fn_arXiv
    return fakes_arXiv


def format_dblp(fakes_dblp, common_doi, list_of_id_dblp):
    commond = []
    new_fakes_dblp = []
    for paper in fakes_dblp:
        if paper['@id'] not in list_of_id_dblp:
            if 'doi' in paper['info'].keys():
                if paper['info']['doi'].lower() not in common_doi:
                    new_fakes_dblp.append(dblp.format(paper))
                else:
                    commond.append(dblp.format(paper))
            else:
                new_fakes_dblp.append(dblp.format(paper))
    return new_fakes_dblp, commond


def format_arXiv(fakes_arXiv, common_doi, list_of_id_arXiv):
    commona = []
    new_fakes_arXiv = []
    for paper in fakes_arXiv:
        if paper['id'] not in list_of_id_arXiv:
            if 'arxiv:doi' in paper.keys():
                if paper['arxiv:doi']['#text'].lower() not in common_doi:
                    new_fakes_arXiv.append(arxiv.format(paper))
                else:
                    commona.append(arxiv.format(paper))
            else:
                new_fakes_arXiv.append(arxiv.format(paper))
    return new_fakes_arXiv, commona


def merge_common(commona, commond):
    list_common = []
    for ca in commona:
        for cd in commond:
            if ca['doi'] == cd['doi']:
                if ca['publisher-venue'] == '':
                    ca['publisher-venue'] = cd['publisher-venue']
                if ca['type'] == '':
                    ca['type'] = cd['type']
                list_common.append(ca)
    return list_common


def save_merged(merged, flag):
    if flag == 0:
        with open('assets/data/raw/fn.json', 'w') as fw:
            json.dump(merged, fw)
    else:
        with open('assets/data/raw/fn.json', 'a') as fw:
            json.dump(merged, fw)


if __name__ == '__main__':
    try:
        # plos only by author
        engines = [semantic, dblp, arxiv, cross, springer]

        # print([(e.name, e.search_size('disinformation')) for e in engines])

        titles = ['Disinformation on the web: Impact, characteristics, and detection of wikipedia hoaxes',
                  'Ha ha ha ah...',
                  'Factitious - Large Scale Computer Game to Fight Fake News and Improve News Literacy.',
                  'Fact-checking effect on viral hoaxes: A model of misinformation spread in social networks',
                  'Do Sentence Interactions Matter? Leveraging Sentence Level Representations for Fake News Classification',
                  'Italian Populism and Fake News on the Internet: A New Political Weapon in the Public Discourse']

        keywords = ['fake news', 'misinformation', 'disinformation', 'hoax', 'hoaxes', 'fact checkers', 'fact checking',
                    'infodemic', 'information disorder']

        list_of_id_dblp = []
        list_of_id_arXiv = []
        flag = 0

        for keyword in keywords:
            fakes_dblp = search_DBLP(keyword)
            fakes_arXiv = search_ArXiv(keyword)

            list_of_doi_dblp = [fakes['info']['doi'].lower() for fakes in fakes_dblp if 'doi' in fakes['info'].keys()]
            list_of_doi_arXiv = [fakes['arxiv:doi']['#text'].lower() for fakes in fakes_arXiv if
                                 'arxiv:doi' in fakes.keys()]
            common_doi = set(list_of_doi_dblp) & set(list_of_doi_arXiv)

            new_fakes_dblp, commond = format_dblp(fakes_dblp, common_doi, list_of_id_dblp)
            new_fakes_arXiv, commona = format_arXiv(fakes_arXiv, common_doi, list_of_id_arXiv)

            merged = new_fakes_dblp + new_fakes_arXiv + merge_common(commond, commona)

            save_merged(merged, flag)
            flag = 1

            list_of_id_dblp.extend([fakes['@id'] for fakes in fakes_dblp if '@id' in fakes.keys()])
            list_of_id_arXiv.extend([fakes['id'].split('/')[1] for fakes in fakes_arXiv if 'id' in fakes.keys()])

            with open('update_log.log', 'w') as fw:
                fw.write('pyMERGE DONE')

    except Exception as e:

        logger.error('Exception in pyMERGE')
        logger.error(e)
