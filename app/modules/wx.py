# encoding: utf-8
from app.modules import base
import logging as l
import hashlib

class wx(base):
    def render(self, template_name, **kwargs):
        super(wx, self).render(template_name, **kwargs)

class CheckHandler(wx):
    '''
    yf: 认证公众号
    '''
    def get(self):
        pass
    def post(self):
        _token = "sohuweixin"
        sn = self.get_argument('signature', '')
        es = self.get_argument('echostr', '')
        a = ''.join(str(i) for i in sorted([_token, self.get_argument('timestamp', 't'), self.get_argument('nonce', 'n')]))

        if str(hashlib.sha1(a).hexdigest()) == str(sn):
            self.write(es)
        else:
            l.info("fail access")
    def check_xsrf_cookie(self):
        pass

class AjaxHandler(wx):
    '''
    yf: 公众号请求
    '''
    def get(self):
        self.check_tocken()
        self.write(self.getU())

    def post(self):
        l.info(self.request.headers)
        l.info(self.json_decode(self.request.body))

    def check_xsrf_cookie(self):
        pass

class WebHandler(wx):
    def get(self):
        l.info(self.request.headers)
        l.info(self.json_decode(self.request.body))

class NotFoundHandler(wx):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = '/wx'

urls = [
    ('?', CheckHandler),
    ('/ajax?', AjaxHandler),
    ('/web', WebHandler)
]