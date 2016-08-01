#encoding=utf-8
from app.modules import base

class main(base):
    def render(self, template_name, **kwargs):
        super(main, self).render('main/' + template_name, **kwargs)

class MainHandler(main):
    '''
    yf: 首页
    '''
    def get(self):
        users = self.db.user().data
        self.write({'users':users})

class ParticularHandler(main):
    '''
    yf: Particular
    '''
    def get(self, id=None):
        data = self.db.client(id=id).one()
        self.write({'data': data})

class NotFoundHandler(main):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = ''

urls = [
    ('/m', MainHandler),
    ('/particular/(\d+).json', ParticularHandler)
]