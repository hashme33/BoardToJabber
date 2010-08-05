# -*- coding: utf-8 -*-
'''
Created on 09.07.2010

@author: Foobar
'''
import re
from Parser import Parser

class DobrochanParser(Parser):
    class Thread(Parser.Thread):
        def __init__(self,thread=None,lastpost=None):
            Parser.Thread.__init__(self,thread,lastpost)
            self.oppost_re = re.compile("""<div id="post_(\d+)" class="oppost post">(.+?)<div class="abbrev">\s+</div>\s+</div>""",re.DOTALL)
            self.post_re = re.compile("""<tr>\s+<td class="doubledash">&gt;&gt;</td>\s+<td class="reply" id="reply\d+">(.+?)</td></tr>""",re.DOTALL)
            self.update(thread)
        def update_specifics(self):
            try:
                if self.thread:
                    self.posts = self.post_re.findall(self.thread)
                    oppost = self.oppost_re.findall(self.thread)[0]
                    self.number = int(oppost[0])
                    self.posts.insert(0,oppost[1])
                    self.posts = [DobrochanParser.Post(p) for p in self.posts]
                    return True
                else:
                    return False
            except :
                return False
        def CreatePost(self):
            return DobrochanParser.Post()
            
    class Post(Parser.Post):
        def __init__(self,post=None):
            Parser.Post.__init__(self,post)
            self.header_re = re.compile("""()?\s+()?\s+(<span class="postername">(.+?)</span>)?\s+(<span class="postertrip">(.+?)</span>)?\s+(.+?:\d+)""",re.DOTALL)
            self.pnum_re = re.compile(r"""<a name="i(\d+)"></a>""")
            self.sg_re = re.compile(r"""<img src="/images/sage-carbon.png" alt="Сажа" title="Сажа"/>""")
            self.sj_re = re.compile(r"""<span class="replytitle">(.+?)</span>""")
            self.pn_re = re.compile(r"""<span class="postername">(.+?)</span>""")
            self.pt_re = re.compile(r"""<span class="postertrip">(.+?)</span>""")
            self.at_re = re.compile(r"""<div class="fileinfo.*?">\s+Файл: <a href="(.+?)" target="_blank">(.+?)</a>""")
            self.dt_re = re.compile(r"""(\d+ \w+ \d+ \(\w+\) \d+:\d+)\s+</label>""")
            self.comment_re = re.compile("""<div class="postbody">\s+<div class="message">(.*?)</div>\s+</div>""",re.DOTALL)
            self.clean_blockquote = r"""<blockquote.*?>(.+?)</blockquote>"""
            self.clean_blockquote1 = r"""(.)<blockquote.*?>(.+?)</blockquote>"""
            self.clean_pre = r"""<pre>(.+?)</pre>"""
            self.clean_pre1 = r"""(.)<pre>(.+?)</pre>"""
            self.update(post)
        def _SimplifySpecifics(self,comment):
            comment = re.sub(self.clean_pre1,r"\1\n\2\n\n",comment)
            comment = re.sub(self.clean_pre,r"\1\n\n",comment)
            comment = re.sub(self.clean_blockquote1,r"\1\n\2\n\n",comment)
            return re.sub(self.clean_blockquote,r"\1\n\n",comment)
        def GetAttachments(self):
            return "\n".join(["File: %s Link: http://dobrochan.ru%s"%(l,n) for ((n,l)) in self.attachments])
        def _copy(self):
            temp = DobrochanParser.Post(None)
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
                self.comment = self._SimplifyComment(self.comment_re.findall(self.post)[0])
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
                    self.postername = self.pn_re.findall(self.post)[0]
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
            except :
                return False