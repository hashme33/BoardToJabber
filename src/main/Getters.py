# -*- coding: utf-8 -*-
'''
Created on 09.07.2010

@author: Foobar
'''
import threading,urllib2

class DobrochanGetter(threading.Thread):
    def __init__(self,url,lock,resultdict):
        threading.Thread.__init__(self)
        self.burl = url
        self.url = "http://%s/%s/res/%s"%(url[0],url[1],url[2])
        self.lock = lock
        self.rd = resultdict
    def run(self):
        print "I'm downloading ",self.url
        try:
            data = urllib2.urlopen(self.url).read()
        except urllib2.HTTPError as err:
            data = str(err.code)
        except:
            data = ""
        with self.lock:
            self.rd[self.burl] = data
        
       
class TirechGetter(threading.Thread):
    def __init__(self,url,lock,resultdict):
        threading.Thread.__init__(self)
        self.burl = url
        self.url = "http://%s/%s/res/%s"%(url[0],url[1],url[2])
        self.lock = lock
        self.rd = resultdict
    def run(self):
        print "I'm downloading ",self.url
        try:
            data = urllib2.urlopen(self.url).read()
        except urllib2.HTTPError as err:
            data = str(err.code)
        except:
            data = ""
        with self.lock:
            self.rd[self.burl] = data
        
       