# encoding: utf-8
from app.modules import base
import logging as l

class main(base):
    def render(self, template_name, **kwargs):
        super(main, self).render(template_name, **kwargs)

class MainHandler(main):
    '''
    yf: 首页
    '''
    def get(self):
        self.current_user = self.get_current_user()
        if self.current_user:
            self.render('sys.html', hl='main')
        else:
            self.redirect('/sys/login')

class LoginHandler(main):
    '''
    yf: 登录
    '''
    def get(self):
        if self.current_user:
            self.redirect('/sys')
        else:
            self.render('login.html')

    def post(self):
        dat = self.json_decode(self.request.body)
        u = self.db.user(username=dat['username'], password=dat['password']).one()
        if u:
            self.set_secure_cookie('u', unicode(u.id))
            self.redirect('/sys')
        else:
            self.render('login.html', error='用户名或密码错误')

class PagesHandler(main):
    '''
    yf: 专题页
    '''
    def get_current_user(self):
        pass

    def get(self, id=None):
        self.render('s/'+id+'/index.html')

class testingHandler(main):
    def get(self):
        self.write("e656fbed187ccbfdc6f972f1b69ab504")

class NotFoundHandler(main):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = ''

urls = [
    ('/sys', MainHandler),
    ('/sys/login', LoginHandler),
    ('/s/(\d+)/', PagesHandler),
    ('/e656fbed187ccbfdc6f972f1b69ab504.txt', testingHandler)
]