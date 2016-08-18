# encoding: utf-8
from app.modules import base
import logging as l

class pub(base):
    def render(self, template_name, **kwargs):
        super(pub, self).render(template_name, **kwargs)

class CheckHandler(pub):
    '''
    yf: 首页
    '''
    def get(self):
        self.write("true")

class NotFoundHandler(pub):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = '/pub'

urls = [
    ('/check?', CheckHandler)
]