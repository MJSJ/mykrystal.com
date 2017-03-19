# encoding: utf-8
from app.modules import base
import logging as l

class user(base):
    def render(self, template_name, **kwargs):
        if self.current_user:
            kwargs['u'] = self.get_current_user()
            super(user, self).render(template_name, **kwargs)
        else:
            self.redirect('/sys/login')

class UsersHandler(user):
    def get(self):
        users = self.db.user().data
        self.render('user.list.html', hl='list-user', users=users)

class UserHandler(user):
    def get(self, id=None):
        user = self.db.user(id=id).one()
        self.render('user.edit.html', hl='user', user=user)

class UserNewHandler(user):
    def get(self):
        self.render('user.edit.html', hl='new-user', user=None)

class UserEditHandler(user):
    def post(self):
        dat = self.json_decode(self.request.body)
        if 'id' not in dat: # 添加用户
            uid = self.db.user.add(**dat)
            self.redirect('/sys/user')
        else:
            self.db.user(id=dat['id']).update(**dat)
            self.redirect('/sys/user')

class UserDelHandler(user):
    def post(self):
        dat = self.json_decode(self.request.body)
        self.db.user(id=dat['id']).update(**dat)
        self.redirect('/sys/user')

url_prefix = '/sys/user'

urls = [
    ('/?', UsersHandler),
    ('/(\d+)', UserHandler),
    ('/new', UserNewHandler),
    ('/edit', UserEditHandler),
    ('/del', UserDelHandler)
]