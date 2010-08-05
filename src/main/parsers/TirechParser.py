# -*- coding: utf-8 -*-
'''
Created on 09.07.2010

@author: Foobar
'''
import re
from Parser import Parser

class TirechParser(Parser):
    class Thread(Parser.Thread):
        def __init__(self,thread=None,lastpost=None):
            Parser.Thread.__init__(self,thread,lastpost)
            self.oppost_re = re.compile("""<form id="delform" action="/[a-zA-Z0-9]+/wakaba\.pl" method="post">(.+?</blockquote>\s+(<br clear="left"|<table>))""",re.DOTALL)
            self.post_re = re.compile("""<td class="reply" id="reply\d+">(.+?</blockquote>\s+</td>)""",re.DOTALL)
            self.update(thread)
        def update_specifics(self):
            try:
                if self.thread:
                    self.posts = self.post_re.findall(self.thread)
                    oppost = self.oppost_re.findall(self.thread)
                    self.posts.insert(0,oppost[0][0])
                    self.posts = [TirechParser.Post(p) for p in self.posts]
                    self.number = int(self.posts[0].GetNumber())
                    return True
                else:
                    return False
            except:
                return False
        def CreatePost(self):
            return TirechParser.Post()
            
    class Post(Parser.Post):
        def __init__(self,post=None):
            Parser.Post.__init__(self,post)
            self.pnum_re = re.compile(r"""<a name="(\d+)"></a>""")
            self.sg_re = re.compile(r"""<span class="(comment)?postername"><a href="mailto:sage">""")
            self.sj_re = re.compile(r"""<span class="replytitle">(.*?)</span>""")
            self.pn_re = re.compile(r"""<span class="(comment)?postername">(<a href="mailto:sage">)?(.+?)<""")
            self.pt_re = re.compile(r"""<span class="postertrip">(.+?)</span>""")
            self.at_re = re.compile(r"""<span class="filesize">Файл: <a target="_blank" href="(.+?)">(.+?)</a>""")
            self.dt_re = re.compile(r"""\w+ \d+ \w+ \d+ \d+:\d+:\d+</label>""")
            self.comment_re = re.compile("""<blockquote>(.+?)</blockquote>\s+(<br clear="left"|<table>|</td>)""",re.DOTALL)
            self.clean_blockquote = r"""<blockquote.*?>(.+?)</blockquote>"""
            self.clean_blockquote1 = r"""(.)<blockquote.*?>(.+?)</blockquote>"""
            self.clean_pre = r"""<pre>(.+?)</pre>"""
            self.clean_pre1 = r"""(.)<pre>(.+?)</pre>"""
            self.clean_p = r"""<p>(.+?)</p>"""
            self.clean_p1 = r"""(.)<p>(.+?)</p>"""
            self.update(post)
        def _SimplifySpecifics(self,comment):
            comment = re.sub(self.clean_p1,r"\1\n\2\n\n",comment)
            comment = re.sub(self.clean_p,r"\1\n\n",comment)
            comment = re.sub(self.clean_pre1,r"\1\n\2\n\n",comment)
            comment = re.sub(self.clean_pre,r"\1\n\n",comment)
            comment = re.sub(self.clean_blockquote1,r"\1\n\2\n\n",comment)
            return re.sub(self.clean_blockquote,r"\1\n\n",comment)
        def GetAttachments(self):
            return "\n".join(["File: %s Link: http://2-ch.ru%s"%(l,n) for ((n,l)) in self.attachments])
        def _copy(self):
            temp = TirechParser.Post(None)
            temp.deleted = self.deleted
            temp.number = self.number
            temp.sage = self.sage
            temp.subject = self.subject
            temp.postername = self.postername
            temp.postertrip = self.postertrip
            temp.comment = self.comment
            temp.attachments = self.attachments[:]
            return temp
        def update_specifics(self):
            if not self.post:
                return False
            try:
                self.comment = self._SimplifyComment(self.comment_re.findall(self.post)[0][0])
                self.attachments = self.at_re.findall(self.post)
                try:
                    self.number = int(self.pnum_re.findall(self.post)[0])
                except:
                    pass
                self.sage = bool(len(self.sg_re.findall(self.post)))
                try:
                    self.subject = self.sj_re.findall(self.post)[0]
                except:
                    pass
                try:
                    self.postername = self.pn_re.findall(self.post)[0][2]
                except:
                    pass
                try:
                    self.postertrip = self.pt_re.findall(self.post)[0]
                except:
                    pass
                try:
                    self.data = self.dt_re.findall(self.post)[0]
                except:
                    pass
                return True
            except:
                return False