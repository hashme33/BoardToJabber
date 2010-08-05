# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from SubscriptionManager import SubscriptionManager
import BotConfig
from JabberBot import JabberBot,botcmd
import threading,time
import re
class MyBot(JabberBot):
    def __init__(self, username, password, nickname="BoardBot1", res=None, debug=False):
        JabberBot.__init__(self,username,password,nickname,res,debug)
        self.thread_re = re.compile(r"http://(.+)/(.+)/res/([a-zA-Z0-9\.].+)")
        self.watcher = SubscriptionManager(self.sf,BotConfig.SubscriptionsFile,cycle_length=BotConfig.ClientUpdatePeriod,keeper_cycle=BotConfig.UpdateThreadsPeriod,scheduler_cycle=BotConfig.ThreadDownloadPeriod)
        self.watcher.start()
            
    def sf(self,client,mess):
        if not self.IsOnline(client):
            return False
        self.send(client,mess)
        return True
    @botcmd
    def info(self,mess,args):
        (result,text) = self.watcher.GetSubscriptions(str(mess.getFrom()))
        return text
    @botcmd
    def add(self,mess,args):
        """Subscribes you on a thread, usage:
    add thread-url [name]
    You can specify the name for this thread using name parameter"""
        if len(args)>=1:
            thread = args[0]
            try:
                data = self.thread_re.findall(thread)[0]
                name = ""
                if len(args)>=2:
                    name = " ".join(args[1:])
                chan = data[0]
                board = data[1]
                thr = data[2]
                (result,text) = self.watcher.AddSubscription(chan, board, thr, str(mess.getFrom()),name)
                return text
            except:
                return ""
    @botcmd
    def remove(self,mess,args):
        if len(args)>=1:
            thread = args[0]
            try:
                data = self.thread_re.findall(thread)[0]
                #print data
                chan = data[0]
                board = data[1]
                thr = data[2]
                (result,text) = self.watcher.RemoveSubscription(chan, board, thr, str(mess.getFrom()))
                return text
            except:
                return ""

bot = MyBot("bot_test@jabber.ru","12345")
bot.serve_forever()