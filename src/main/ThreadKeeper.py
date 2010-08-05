# -*- coding: utf-8 -*-
'''
Created on 10.07.2010

@author: Foobar
'''
import threading,os,time,pickle
from Scheduler import Scheduler
import BotConfig
class ThreadKeeper(threading.Thread):
    def __init__(self,cycle_length,scheduler_length):
        threading.Thread.__init__(self)
        self.folder = BotConfig.KeeperFolder
        self.folderpath = ""
        self.configfile = BotConfig.KeeperConfigFile
        self.cycle_length=cycle_length
        if self.folder:
            try:
                os.mkdir(self.folder)
            except:
                pass
            self.folderpath = self.folder + "/"
        self.configfile = self.folderpath+self.configfile
        self.chans = BotConfig.Chans
        self.threads = {}
        self.threadcnt = {}
        self.threadfiles = {}
        self.threadstates = {}
        self.threadLock = threading.Lock()
        self.scheduler = Scheduler(scheduler_length)
        self.scheduler.start()
        self.Restore()
    def Restore(self):
        serial = None
        try:
            with open(self.configfile,"rb") as f:
                serial = pickle.load(f)
        except:
            pass
        if not serial:
            return
        for (item,value) in serial.iteritems():
            (self.threadfiles[item],self.threadcnt[item],self.threadstates[item]) = value
            (parser,getter) = self.chans[item[0]]
            try:
                with open(value[0],"rb") as f:
                    p = parser.Thread()
                    x = f.read()
                    if not p.DeserializeXml(x):
                        self.threadstates[item] = "NONE"     
                    else:
                        self.threadstates[item] = "OK"           
                    self.threads[item] = p
            except:
                p = parser.Thread()
                self.threadstates[item] = "NONE"
                self.threads[item] = p 
            self.scheduler.AddTask(item,getter,freq=1)

    def GetPath(self,chan,board,thr):
        try:
            os.mkdir(self.folderpath+chan)
        except:
            pass
        try:
            os.mkdir(self.folderpath+chan+"/"+board)
        except:
            pass
        return self.folderpath+chan+"/"+board+"/"+thr
    def AddThread(self,thread,freq=1):
        (chan,board,thr) = thread
        if not (chan in self.chans):
            return False
        tpath = self.GetPath(chan,board,thr)
        with self.threadLock:
            if thread in self.threads:
                self.threadcnt[thread] = self.threadcnt[thread] + 1
            else:
                self.threadcnt[thread] = 1
                self.threadfiles[thread] = tpath 
                (parser,getter) = self.chans[chan]
                self.threads[thread] = parser.Thread()
                self.threadstates[thread] = "NONE"
                self.scheduler.AddTask(thread,getter,freq=1)
            self.Serialize()
        return True
    def Serialize(self):
        with open(self.configfile,"wb") as f:
                serial = {}
                for item in self.threads.keys():
                    serial[item] = (self.threadfiles[item],self.threadcnt[item],self.threadstates[item])
                pickle.dump(serial,f)
    def RemoveThread(self,thread):
        with self.threadLock:
            if thread in self.threads:
                if self.threadcnt[thread] == 1:
                    del self.threadcnt[thread]
                    del self.threadfiles[thread]
                    del self.threads[thread]
                    del self.threadstates[thread]
                    self.scheduler.RemoveTask(thread)
                else:
                    self.threadcnt[thread] = self.threadcnt[thread] - 1
                self.Serialize()

    def GetPosts(self,thread,afternumber=0):
        with self.threadLock:
            state = self.threadstates[thread]
            if afternumber==0:
                if state == "OK":
                    res = (self.threads[thread].GetLastPostNumber(),"","OK")
                elif state == "DIED":
                    res = (self.threads[thread].GetLastPostNumber(),"","DIED")
                else:
                    res = (0,"","NONE")
            else:
                if state == "OK":
                    res = (self.threads[thread].GetLastPostNumber(),self.threads[thread].GetPostsAfter(afternumber),"OK")
                elif state == "DIED":
                    res = (self.threads[thread].GetLastPostNumber(),self.threads[thread].GetPostsAfter(afternumber),"DIED")
                else:
                    res = (0,"","NONE")
        return res
    
    def _UpdateThread(self,url,data):
        thr = self.threads[url]
        (parser,getter) = self.chans[url[0]]
        temp = parser.Thread(data)
        thr.Reload(temp)
        self.threadstates[url] = "OK"
        del temp
        del data
        with open(self.threadfiles[url],"wb") as f:
            thr.SerializeXml(f)
        self.Serialize()
    def run(self):
        while True:
            with self.threadLock:
                for url in self.threads.keys():
                    result = self.scheduler.GetResult(url)
                    if result == "404":
                        self.threadstates[url] = "DIED"
                    elif result:
                        self._UpdateThread(url,result)
            time.sleep(self.cycle_length)