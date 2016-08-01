#encoding=utf-8
from app.modules import base

class sys(base):
    def render(self, template_name, **kwargs):
        super(sys, self).render('sys/' + template_name, **kwargs)

class sysHandler(sys):
    '''
    yf: Particular
    '''
    def get(self, id=None):
        data = self.db.client(id=id).one()
        self.write({'data': data})

url_prefix = '/sys'

urls = [
    ('/(\d+).json', sysHandler)
]