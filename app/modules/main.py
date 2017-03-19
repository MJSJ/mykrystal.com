# encoding: utf-8
from app.modules import base
import logging as l

class main(base):
    def render(self, template_name, **kwargs):
        if self.current_user:
            kwargs['u'] = self.get_current_user()
            super(main, self).render(template_name, **kwargs)
        else:
            self.redirect('/sys/login')

class MainHandler(main):
    '''
    yf: 首页
    '''
    def get(self):
        self.render('sys.html', hl='main')

class LoginHandler(main):
    '''
    yf: 登录
    '''
    def render(self, template_name, **kwargs):
        super(main, self).render(template_name, **kwargs)

    def get(self):
        self.render('login.html')

    def post(self):
        dat = self.json_decode(self.request.body)
        u = self.db.user(username=dat['username'], password=dat['password'], is_del=0).one()
        if u:
            self.set_secure_cookie('u', unicode(u.id))
            self.redirect('/sys')
        else:
            self.render('login.html', error='用户名或密码错误')

class SignoutHandler(main):
    '''
    yf: 退出登录
    '''
    def render(self, template_name, **kwargs):
        super(main, self).render(template_name, **kwargs)

    def get(self):
        self.set_secure_cookie('u', '')
        self.redirect('/sys/login')

class PagesHandler(main):
    '''
    yf: old专题
    '''
    def render(self, template_name, **kwargs):
        super(main, self).render(template_name, **kwargs)

    def get(self, id=None):
        self.render('s/'+id+'/index.html')

class NotFoundHandler(main):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href='/sys'>back</a>")

url_prefix = ''

urls = [
    ('/sys', MainHandler),
    ('/s/(\d+)/', PagesHandler),
    ('/sys/login', LoginHandler),
    ('/sys/signout', SignoutHandler)
]