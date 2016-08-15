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
            self.redirect('/login')

class LoginHandler(main):
    '''
    yf: 登录
    '''
    def get(self):
        if self.current_user:
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        dat = self.json_decode(self.request.body)
        u = self.db.user(username=dat['username'], password=dat['password']).one()
        if u:
            self.set_secure_cookie('u', unicode(u.id))
            self.redirect('/')
        else:
            self.render('login.html', error='用户名或密码错误')

class PagesHandler(main):
    def get(self, id=None):
        self.render('s\\'+id+'\\index.html')

class NotFoundHandler(main):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = ''

urls = [
    ('/', MainHandler),
    ('/login', LoginHandler),
    ('/s/(\d+)/', PagesHandler)
]