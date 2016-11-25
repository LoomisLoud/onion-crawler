#!/usr/bin/python
# coding: utf-8
#authors: Pineau T. & Schopfer A.

import urllib2
import requests #pip install requests

    
def requestsSC(url):
    """Récupération du code source d'une URL via requests"""
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0"}
    r = requests.get(url, headers=headers)
    contents = r.content
    return contents

def urllibSC(url):
    """Récupération du code source d'une URL via urllib2"""
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0"}
    request = urllib2.Request(url, headers=headers)
    contents = urllib2.urlopen(request).read()
    return contents

def saveContent(data, filename):
    """Enregistrement de data dans un fichier filename"""
    with open(filename, 'wb+') as f:
        f.write(data)
    print 'done'

s=requestsSC("http://ipsac.unil.ch/traces/")
#s=urllibSC("http://ipsac.unil.ch/traces/")

print s


#saveContent(s, 'test.html')
