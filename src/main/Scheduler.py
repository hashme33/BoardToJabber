# -*- coding: utf-8 -*-
'''
Created on 09.07.2010

@author: Foobar
'''
import threading,time

class Scheduler(threading.Thread):
    def __init__(self,cycle_length):
        threading.Thread.__init__(self)
        self.taskLock = threading.Lock()  
        self.resultLock = threading.Lock()
        self.cycle_length = cycle_length    
        self._tasks = {}
        self._taskfreq = {}
        self._tasksresult = {}
        self._taskcount = {}
    def AddTask(self,task,getter,freq=3):
        with self.taskLock:
            try:
                self._taskcount[task] = self._taskcount + 1
                return
            except:
                self._taskcount[task] = 1
            self._tasks[task] = getter
            self._tasksresult[task] = ""
            self._taskfreq[task] = (freq-1,freq)
    def GetFreq(self,task):
        with self.taskLock:
            try:
                res = self._taskfreq[task][1]
            except:
                res = 1
        return res
    def RemoveTask(self,task):
        with self.taskLock:
            if task in self._tasks:
                if self._taskcount[task] == 1:
                    with self.resultLock:
                        try:
                            del self._taskresult[task]
                        except:
                            pass
                    del self._tasks[task]
                    del self._taskfreq[task]
                else:
                    self._taskcount[task] = self._taskcount[task]-1
    def TotallyRemove(self,task):
        with self.taskLock:
            if task in self._tasks:
                with self.resultLock:
                    try:
                        del self._taskresult[task]
                    except:
                        pass
                del self._tasks[task]
                del self._taskfreq[task]
    def GetResult(self,task):
        with self.resultLock:
            if task in self._tasksresult:
                result = self._tasksresult[task]
            else:
                result ="404"
        return result
    def update_time(self):
        with self.taskLock:
            for k in self._taskfreq.keys():
                (t,f) = self._taskfreq[k]
                if t==0:
                    t = f-1
                else:
                    t = t-1
                self._taskfreq[k] = (t,f)
    
    def run(self):
        time_step = -1
        tasklist = []
        while True:
            if time_step < 0:
                with self.taskLock:
                    lt = len([True for t in self._tasks if self._taskfreq[t][0]==0])
                if not lt:
                    time_step = -1
                    self.update_time()
                    time.sleep(self.cycle_length)
                    continue
                else:
                    time_step = self.cycle_length / lt
                    with self.taskLock:
                        for (k,v) in self._tasks.iteritems():
                            if self._taskfreq[k][0]==0:
                                tasklist.append((k,v))
                    self.update_time()
            else:
                r = 0
                (u,l) = tasklist[-1]
                tasklist = tasklist[:-1]
                with self.taskLock:
                    if u in self._tasks:
                        self._tasks[u](u,self.resultLock,self._tasksresult).start()
                        r = 1
                if r==1:
                    time.sleep(time_step)
                if not tasklist:
                    time_step = -1