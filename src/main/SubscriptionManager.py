'''
Created on 25.07.2010

@author: Foobar
'''
import threading,pickle,time
import BotConfig
from ThreadKeeper import ThreadKeeper
class SubscriptionManager(threading.Thread):
    def __init__(self,sendfunc,subscr_file,cycle_length,keeper_cycle,scheduler_cycle):
        threading.Thread.__init__(self)
        self.subscr_file = subscr_file
        self.chans = BotConfig.Chans
        self.keeper = ThreadKeeper(keeper_cycle,scheduler_length=scheduler_cycle)
        self.keeper.start()
        self.subscriptions = {}
        self.postcount = {}
        try:
            with open(subscr_file,"rb") as f:
                serial = pickle.load(f)
                for (key,value) in serial.iteritems():
                    (self.subscriptions[key],self.postcount[key]) = value
        except:
            pass
        self.sendfunc = sendfunc
        self.cycle_length = cycle_length
        self.subscriptionsLock = threading.Lock()
    def Serialize(self):
        serial = {}
        with self.subscriptionsLock:
            for key in self.subscriptions.keys():
                serial[key] = (self.subscriptions[key],self.postcount[key])
            with open(self.subscr_file,"wb") as f:
                pickle.dump(serial,f)
    def _Serialize(self):
        serial = {}
        for key in self.subscriptions.keys():
            serial[key] = (self.subscriptions[key],self.postcount[key])
        with open(self.subscr_file,"wb") as f:
            pickle.dump(serial,f)
    def AddSubscription(self,chan,board,thread,client,name,freq=1):
        (chan,board,thread) = (chan.lower(),board.lower(),thread.lower())
        if chan not in self.chans:
            return (False,"This chan is not supported")
        self.keeper.AddThread((chan,board,thread))
        with self.subscriptionsLock:
            if client in self.postcount:
                if (chan,board,thread) in self.postcount[client]:
                    return (False,"You are already subscribed on this thread!")
                else:
                    self.subscriptions[client].add((chan,board,thread))
                    self.postcount[client][(chan,board,thread)] = (0,name)
            else:
                self.subscriptions[client] = set([(chan,board,thread)])
                self.postcount[client] = {}
                self.postcount[client][(chan,board,thread)] = (0,name)
        self.Serialize()
        return (True,"Subscribed!")
    
    def GetSubscriptions(self,client):
        with self.subscriptionsLock:
            if client in self.subscriptions:
                result = (True,"You are subscribed on these threads:\n"+("\n".join(["http://%s/%s/res/%s %s"%(c,b,t,self.postcount[client][(c,b,t)][1]) for (c,b,t) in self.subscriptions[client]])))
            else:
                result = (False,"You are not subscribed on anything")
        return result
    def RemoveSubscription(self,chan,board,thread,client):
        (chan,board,thread) = (chan.lower(),board.lower(),thread.lower())
        if chan not in self.chans:
            return (False,"This chan is not supported")
        self.keeper.RemoveThread((chan,board,thread))
        with self.subscriptionsLock:
            if client in self.postcount:
                if (chan,board,thread) in self.postcount[client]:
                    del self.postcount[client][(chan,board,thread)]
                    self.subscriptions[client].remove((chan,board,thread))
                    if len(self.postcount[client])==0:
                        del self.postcount[client]
                        del self.subscriptions[client]
                    return (True,"You are unsubscribed from this thread!")
                else:
                    return (False,"You were not subscribed on this thread!")
            else:
                return (False,"I don't know you")
        self.Serialize()
           
    def _RemoveSubscription(self,chan,board,thread,client):
        (chan,board,thread) = (chan.lower(),board.lower(),thread.lower())
        if chan not in self.chans:
            return (False,"This chan is not supported")
        self.keeper.RemoveThread((chan,board,thread))
        if client in self.postcount:
            if (chan,board,thread) in self.postcount[client]:
                del self.postcount[client][(chan,board,thread)]
                self.subscriptions[client].remove((chan,board,thread))
                if len(self.postcount[client])==0:
                    del self.postcount[client]
                    del self.subscriptions[client]
                return (True,"You are unsubscribed from this thread!")
            else:
                return (False,"You were not subscribed on this thread!")
        else:
            return (False,"I don't know you")
        self._Serialize()

    def process_client(self,client,data):
        
        answer = ""
        update_threads = {}
        remove_subscr = set([])
        data = data.copy()
        for thr in data:
            anspart = ""
            try:
                (num,res,state) = self.keeper.GetPosts(thr,self.postcount[client][thr][0])               
            except KeyError:
                continue
            if state == "NONE":
                continue
            elif state=="DIED":
                if res:
                    anspart = res+"\n"
                anspart = anspart+("## Thread http://%s/%s/res/%s died\n"%(thr))
                remove_subscr.add(thr)
                #self._RemoveSubscription(thr[0],thr[1],thr[2],client)
            elif state=="OK":
                if res:
                    anspart = res
                else:
                    self.postcount[client][thr] = (num,self.postcount[client][thr][1])
            if num > self.postcount[client][thr][0]:
                    update_threads[(client,thr)] = num
            if anspart:
                answer = answer+"\n## Thread http://%s/%s/res/%s %s\n"%(thr[0],thr[1],thr[2],self.postcount[client][thr][1])+anspart
        if answer:
            if self.sendfunc(client,answer):
                for (k,v) in update_threads.iteritems():
                    (c,t) = k
                    self.postcount[c][t] = (v,self.postcount[c][t][1])
                for s in remove_subscr:
                    self._RemoveSubscription(s[0], s[1], s[2], client)
        self._Serialize()
            
                    
                    
                        
    def run(self):
        time.sleep(10) #wait for jabber to connect
        while True:
            with self.subscriptionsLock:
                temp =self.subscriptions.copy()
                for (client,v) in temp.iteritems():
                    self.process_client(client,v)
            time.sleep(self.cycle_length)
        