#!/usr/bin/python
# coding: utf-8
#authors: Pineau T. & Schopfer A.

import urllib2
import hashlib

def sourceCode(url):
    """Récupération du code source d'une URL"""
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0"}
    request = urllib2.Request(url, headers=headers)
    contents = urllib2.urlopen(request).read()
    return contents

def saveContent(data, filename):
    """Enregistrement de data dans un fichier filename"""
    with open(filename, 'wb+') as f:
        f.write(data)

def hasher(data):
    """fonction de hashage: md5"""
    h = hashlib.md5()
    h.update(data)
    return h.hexdigest()

   
s=sourceCode("http://ipsac.unil.ch/traces/")
print 'code source: ' +hasher(s)
saveContent(s, 'test.html')

"""
with open('test.html', 'rb') as f:
    buf = f.read()
print 'contenu du fichier: ' + hasher(buf)
"""
