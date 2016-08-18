# encoding: utf-8
from app.modules import base
import logging as l

class pub(base):
    def render(self, template_name, **kwargs):
        super(pub, self).render(template_name, **kwargs)

class CheckHandler(pub):
    '''
    yf: 认证公众号
    '''
    def get(self):
        sn = self.get_argument('signature', '')
        es = self.get_argument('echostr', '')
        _token = '1q2w3e4r'
        a = ''.join(str(i) for i in sorted([_token, self.get_argument('timestamp', 't'), self.get_argument('nonce', 'n')]))
        import hashlib
        if str(hashlib.sha1(a).hexdigest()) == str(sn):
            self.write(es)
        else:
            self.write("false")

class NotFoundHandler(pub):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = '/pub'

urls = [
    ('/check?', CheckHandler)
]