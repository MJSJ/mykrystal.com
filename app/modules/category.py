# encoding: utf-8
from app.modules import base
import logging as l

class category(base):
    def render(self, template_name, **kwargs):
        super(category, self).render(template_name, **kwargs)

class CatesHandler(category):
    def get(self):
        objs = self.db.category(is_parent=1).data
        self.write({"result": objs})

class CateHandler(category):
    '''
    yf: 分类列表页
    '''
    def get(self):
        cates = self.db.category().data
        self.render('cate.list.html', hl='list-cate', cates=cates)

class CateAddHandler(category):
    '''
    yf: 分类添加页
    '''
    def get(self):
        self.render('cate.edit.html', hl='edit-cate', cate=None)

class CateidHandler(category):
    '''
    yf: 分类编辑页
    '''
    def get(self, id=None):
        cate = self.db.category(id=id).one()
        self.render('cate.edit.html', hl='edit2-cate', cate=cate)

class CateEditHandler(category):
    '''
    yf: 编辑分类
    '''
    def post(self):
        dat = self.json_decode(self.request.body)
        if 'id' in dat: # 编辑
            self.db.category(id=dat['id']).update(**dat)
            self.redirect('/cate')
            return
        else: # 添加
            cid = self.db.category.add(**dat)
            self.redirect('/cate')
            return

url_prefix = '/cate'

urls = [
    ('/?', CateHandler),
    ('.json', CatesHandler),
    ('/edit', CateEditHandler),
    ('/add', CateAddHandler),
    ('/(\d+)', CateidHandler)
]