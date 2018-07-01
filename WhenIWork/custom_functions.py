# -*- coding: utf-8 -*-
import re

'''
Math
convtime: converts t (in hh:mm:ss) to time in hours [0] or minutes [1]
w_avg: returns weighted average; values = list of values, 
        weights = list of weights, if weights=None then computes standard average
w_stdev: returns weighted standard deviation, values = list of values
'''
def convtime(t) :
    h,m,s = re.split(':',t)
    _hrs = int(h) + int(m)/60 + int(s)/3600
    _min = int(h)*60 + int(m) + int(s)/60
    return '{:.3f}'.format(_hrs),'{:.3f}'.format(_min)

def w_avg(values,weights=None) :
    numer = 0
    if weights is None :
        weights = np.ones(len(values))
    for v,w in zip(values,weights):
        numer += w*v
        denom = sum(weights)
    return float(numer/denom)

def w_stdev(values,weights,avg) :
    numer = 0
    m = sum([int(bool(i)) for i in weights])
    for v,w in zip(values,weights):
        numer += w*(np.square(v - avg))
        denom = ((m - 1)/m)*sum(weights)
    return(np.sqrt(numer/denom))

'''
Email
get_body: retrieves email html
search: searches for emails based on keywords.
        key = where to search (e.g. Subject)
        value = string searching for
        conn = connection (e.g. mail)
get_emails: retrieves encoded email
'''
def get_body(msg) :
    if msg.is_multipart() :
        return get_body(msg.get_payload(1))
    else :
        return msg.get_payload(None,True)

def search(key,value,conn) :
    result, data = conn.search(None,key,'"{}"'.format(value))
    return data

def get_emails(result_bytes) :
    msgs = []
    for num in result_bytes[0].split() :
        typ, data = conn.fetch(num, '(RFC822)')
        msgs.append(data)
        return msgs