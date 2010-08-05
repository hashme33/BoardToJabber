'''
Created on 25.07.2010

@author: Foobar
'''
ThreadDownloadPeriod = 10.0
UpdateThreadsPeriod = 10.0
ClientUpdatePeriod = 10.0
KeeperFolder = "threads"
KeeperConfigFile = "options.txt"
SubscriptionsFile = "subscriptions.txt"
import sys
sys.path.append("parsers")
from DobrochanParser import DobrochanParser
from TirechParser import TirechParser
from Getters import DobrochanGetter,TirechGetter
Chans = {"2-ch.ru":(TirechParser,TirechGetter),
         "dobrochan.ru":(DobrochanParser,DobrochanGetter)}