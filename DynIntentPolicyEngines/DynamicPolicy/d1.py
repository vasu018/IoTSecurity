'''
Created on Mar 19, 2017

@author: Mahendra
'''
import re
from os import walk
from collections import OrderedDict

def convert_to_dict(policy):
    subparts = policy.split(".")
    retlist ={}
    for part in subparts:
        result = re.search('(.*){(.*)}',part)
        retlist[result.group(1)] = result.group(2) 
    return retlist

def handleReaction(p):
    reactions = OrderedDict()
    elements = p.split(">>>>")
    sources = []
    sdict = convert_to_dict(elements[0])
    print(sdict)
    for act in elements[1]:
        for a in act.split(">"):
            t = a.split(":")
            parts = t[1].split("=")
            reactions[t[0]] = {parts[0]:parts[1]}
            #reactions[parts[0]] = parts[1]
        

def handleBlock(p):
    pass

def handleWhiteList(p):
    pass

if __name__ == '__main__':
    policies = []
    for (dirpath, dirnames, filenames) in walk("Policies"):
        policies.extend(filenames)
        break
    
    for pfiles in policies:
        for pline in open("Policies/"+pfiles):
            if pline.count("!=>") > 0 :
                handleBlock(pline)
            elif pline.count("=>") > 0 :
                handleWhiteList(pline)
            elif pline.count(">>>>") > 0 :
                handleReaction(pline)