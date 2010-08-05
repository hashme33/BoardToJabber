# -*- coding: utf-8 -*-
'''
Created on 09.07.2010

@author: Foobar
'''
import re,htmlentitydefs,urllib2
class Parser:
    class Thread:
        def __init__(self,thread=None,lastpost=None):
            self.thread = thread
            self.postnumbers = set()
            self.lastpost = lastpost
            self.postnumbers_dict = {}

        def update(self,thread):
            if not(thread is None):
                self.thread = thread
            self.number = None
            self.posts = []
            self.update_specifics()
            for i in range(len(self.posts)):
                self.postnumbers_dict[self.posts[i].GetNumber()] = i
                self.postnumbers.add(self.posts[i].GetNumber())
            
        def update_specifics(self):
            return False
        def GetPost(self,post):
            if post in self.postnumbers_dict:
                return self.posts[self.postnumbers_dict[post]]
        def GetPostsAfter(self,lastnumber):
            pl = [self.posts[self.postnumbers_dict[i]].Serialize() for i in sorted(self.postnumbers) if i > lastnumber]
            if pl:
                return "%s"%("\n\n".join(pl))
            else:
                return ""
        def Reload(self,thread):
            deleted_posts = self.postnumbers - thread.postnumbers
            new_posts = thread.postnumbers - self.postnumbers
            self.number = thread.number
            for post in deleted_posts:
                self.posts[self.postnumbers_dict[post]].SetDeleted()
            for post in new_posts:
                self.posts.append(thread.posts[thread.postnumbers_dict[post]]._copy())
                self.postnumbers_dict[post] = len(self.posts)-1
                self.postnumbers.add(post)
        def SerializeXml(self,f):
            sp = sorted(self.postnumbers)
            f.write("<thread><number>%d</number>\n<posts>"%self.GetNumber())
            for i in sorted(self.postnumbers):
                f.write(self.posts[self.postnumbers_dict[i]].SerializeXml()+"\n")
            f.write("</posts></thread>")
        def CreatePost(self):
            return Parser.Post()
        def DeserializeXml(self,value):
            try:
                try:
                    self.number = int(re.findall(r"""<number>(\d+)</number>""",value)[0])
                except :
                    self.number = 0
                posts = re.findall(r"""<post>(.+?)</post>""",value,re.DOTALL)
                for p in posts:
                    po = self.CreatePost()
                    po.DeserializeXml(p)
                    self.posts.append(po)
                    self.postnumbers_dict[po.GetNumber()] = len(self.posts)-1
                    self.postnumbers.add(po.GetNumber())
                return True
            except:
                return False
                
        def GetLastPostNumber(self):
            if len(self.postnumbers):
                return max(self.postnumbers)
            else:
                return 0
        def GetNumber(self):
            return self.number or 0
        def Serialize(self):
            return "%s"%("\n\n".join(p.Serialize() for p in self.posts))
    class Post:
        def __init__(self,post=None):
            self.clean_tags_re = r"""<.+?>"""
            self.clean_br = r"""<br.*?>"""
            
            self.post = post
            
        def update(self,post):
            if not (post is None):
                self.post = post
            self.number = None
            self.sage = None
            self.deleted = False
            self.subject = None
            self.postername = None
            self.postertrip = None
            self.attachments = []
            self.date = None
            self.comment = None
            self.update_specifics()
            
        def update_specifics(self):
            return False
        def SetDeleted(self):
            self.deleted = True
        def GetDeleted(self):
            return self.deleted
        def GetNumber(self):
            return self.number or 0
        def GetSage(self):
            return self.sage or False
        def GetSubject(self):
            return self.subject or ''
        def GetPostername(self):
            return self.postername or ''
        def GetPostertrip(self):
            return self.postertrip or ''
        def GetComment(self):
            return self.comment or ''
        def GetAttachments(self):
            return ''
        def Serialize(self,include_attachments=True):
            return "# Post %d %s Subj:'%s' by %s%s\n%s\n%s"%(self.GetNumber(),self.GetSage()*"SAGE"+((self.GetSage() and self.GetDeleted())*" | ")+self.GetDeleted()*"DELETED",self.GetSubject(),self.GetPostername(),self.GetPostertrip(),''+(self.GetAttachments()+"\n")*(bool(len(self.attachments)) and include_attachments),self.GetComment())
        def safexml(self,string):
            return string.replace("<","&lt;").replace(">","&gt;")
        def _unescape_xml(self,string):
            return string.replace("&lt;","<").replace("&gt;",">")
        def SerializeXml(self):
            return """<post><postnumber>%d</postnumber>\n<sage>%d</sage>\n<deleted>%d</deleted>\n<subj>%s</subj>\n<name>%s</name>\n<trip>%s</trip>\n<attachments>%s</attachments>\n<comment>%s</comment></post>"""% \
        (self.GetNumber(),self.GetSage(),self.GetDeleted(),self.safexml(self.GetSubject()),self.safexml(self.GetPostername()),self.safexml(self.GetPostertrip()), \
         "\n".join(["<attachment><filename>%s</filename><filelink>%s</filelink></attachment>"%(l,self.safexml(n)) for ((n,l)) in self.attachments]),(self.safexml(self.GetComment())))
        def DeserializeXml(self,string):
            try:
                self.number = int(self._GetVal(string,"postnumber")[0])
            except:
                self.number = None
            try:
                self.sage = bool(int(self._GetVal(string,"sage")[0]))
            except:
                self.sage = None
            try:
                self.deleted = bool(int(self._GetVal(string,"deleted")[0]))
            except:
                self.deleted = None
            try:
                self.subject = self._unescape_xml(self._GetVal(string,"subj")[0])
            except:
                self.subject = None
            try:
                self.postername = self._unescape_xml(self._GetVal(string,"name")[0])
            except:
                self.postername = None
            try:
                self.postertrip = self._unescape_xml(self._GetVal(string,"trip")[0])
            except:
                self.postertrip = None
            try:
                self.comment = self._unescape_xml(self._GetVal(string,"comment")[0])
            except:
                self.comment = None
            self.attachments = []
            try:
                string = self._GetVal(string,"attachments")[0]
                string = self._GetVal(string,"attachment")
                for att in string:
                    (l,n) = re.findall(r"""<filename>(.+?)</filename><filelink>(.+)</filelink>""",att,re.DOTALL)[0]
                    self.attachments.append((urllib2.quote(n),n))
            except :
                pass
                    
        def _GetVal(self,string,value):
            return re.findall(r"""<%s>(.*?)</%s>"""%(value,value),string,re.DOTALL)
        def _SimplifyComment(self,comment):
            comment = comment.replace("\n","")
            comment = re.sub(self.clean_br,r"\n",comment)
            comment = self._SimplifySpecifics(comment)
            return self.cut_begnewline(self.cut_endnewline(self._unescape_html(re.sub(self.clean_tags_re,"",comment))))
        def _SimplifySpecifics(self,comment):
            return comment
        def cut_begnewline(self,comment):
            for i in range(len(comment)):
                if comment[i]!='\n':
                    return comment[i:]
        def cut_endnewline(self,comment):
            for i in range(len(comment)-1,0,-1):
                if comment[i]!='\n':
                    return comment[0:i+1]
        def _copy(self):
            temp = Parser.Post(None)
            temp.deleted = self.deleted
            temp.number = self.number
            temp.sage = self.sage
            temp.subject = self.subject
            temp.postername = self.postername
            temp.postertrip = self.postertrip
            temp.comment = self.comment
            temp.attachments = self.attachments[:]
            return temp
        
        def _unescape_html(self,text):
            def fixup(m):
                text = m.group(0)
                if text[:2] == "&#":
                    # character reference
                    try:
                        if text[:3] == "&#x":
                            return unichr(int(text[3:-1], 16))
                        else:
                            return unichr(int(text[2:-1]))
                    except ValueError:
                        pass
                else:
                    # named entity
                    try:
                        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                    except KeyError:
                        pass
                return text # leave as is
            return re.sub("&#?\w+;", fixup, text)
 
 