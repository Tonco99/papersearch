#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  6 13:00:25 2021

@author: alfonso
"""
import logging


def init_log(file):
    """ Initialise Logger. """
    
    logger = logging.getLogger('Log')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(file, mode = 'w')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger