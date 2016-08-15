# encoding: utf-8
from app.modules import base
import logging as l

class object(base):
    def render(self, template_name, **kwargs):
        super(object, self).render(template_name, **kwargs)

class ObjectHandler(object):
    '''
    yf: 编辑专题页
    '''
    def get(self, id=None):
        import os
        obj = self.db.object(id=id).one()
        ph = os.path.dirname(__file__).split("app")[0] + 'templates\\s\\'+str(id)
        f = ""
        try:
            with open(ph + "\\index.html") as d:
                f = d.read()
        except IOError as err:
            l.info("File Error:"+str(err))
        self.render('object.edit.html', hl='edit-object', obj=obj, htmltxt=f)

class ObjectsNewHandler(object):
    '''
    yf: 新建专题页
    '''
    def get(self):
        self.render('object.edit.html', hl='new-object', obj=None)

class ObjectEditHandler(object):
    def post(self):
        import os
        dat = self.json_decode(self.request.body)
        dat['user_id'] = self.current_user
        if 'id' not in dat: # 添加
            oid = self.db.object.add(**dat)
            if oid: # 添加模板
                ph = os.path.dirname(__file__).split("app")[0] + 'templates\\s\\'+str(oid)
                os.makedirs(ph)
                # open("./templates/s/"+str(oid)+"/index.html", "w")
                try:
                    with open(ph+"\\index.html", "w") as f:
                        f.close()
                except IOError as err:
                    l.error("File Error:"+str(err))
            self.redirect('/obj')
            return
        else:
            import sys, os
            reload(sys)
            sys.setdefaultencoding('utf8')

            ph = os.path.dirname(__file__).split("app")[0] + 'templates\\s\\'+dat['id']
            try:
                f = open(ph + "\\index.html", "w+")
                f.truncate()
                f.write(dat['html'])
            except IOError as err:
                l.error('File Error:'+str(err))
            finally:
                if 'f' in locals():
                    f.close()
            del dat['html']
            self.db.object(id=dat['id']).update(**dat)
            self.redirect('/obj')
            return

class ObjectsHandler(object):
    '''
    yf: 专题
    '''
    def get(self):
        objs = self.db.object().data
        self.render('object.list.html', hl='list-object', objs=objs)

url_prefix = '/obj'

urls = [
    ('/?', ObjectsHandler),
    ('/(\d+)', ObjectHandler),
    ('/new', ObjectsNewHandler),
    ('/edit', ObjectEditHandler)
]