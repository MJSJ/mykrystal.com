# encoding: utf-8
from app.modules import base
import logging as l

class object(base):
    def render(self, template_name, **kwargs):
        if self.current_user:
            kwargs['u'] = self.get_current_user()
            super(object, self).render(template_name, **kwargs)
        else:
            self.redirect('/sys/login')

class ObjectHandler(object):
    '''
    yf: 编辑专题页
    '''
    def get(self, id=None):
        import os
        obj = self.db.object(id=id).one()
        obj_back = self.db.object_back(object_id=obj.id).sort(last_modify_time='DESC').data
        ph = os.path.dirname(__file__).split("app")[0] + 'assets/s/'+str(id)
        f = ""
        try:
            with open(ph + "/index.html") as d:
                f = d.read()
        except IOError as err:
            l.info("File Error:"+str(err))
        self.render('object.edit.html', hl='edit-object', obj=obj, objb=obj_back, htmltxt=f)

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
        dat['user_id'] = self.current_user['id']
        if 'id' not in dat: # 添加
            oid = self.db.object.add(**dat)
            if oid: # 添加模板
                # add html file
                ph = os.path.dirname(__file__).split("app")[0] + 'assets/s/'+str(oid)
                os.makedirs(ph)
                # open("./templates/s/"+str(oid)+"/index.html", "w")
                try:
                    with open(ph+"/index.html", "w") as f:
                        f.close()
                except IOError as err:
                    l.error("File Error:"+str(err))
            self.redirect('/sys/obj')
            return
        else:
            import sys, os
            reload(sys)
            sys.setdefaultencoding('utf8')
            # edit html file
            ph = os.path.dirname(__file__).split("app")[0] + 'assets/s/'+dat['id']
            try:
                # 添加回溯记录
                obid = self.db.object_back.add(**{'object_id': dat['id']})
                # 添加回溯备份
                if obid:
                    os.rename(ph + "/index.html", ph + "/index_" + str(obid) + ".html")
                    obj_back = self.db.object_back(object_id=dat['id']).sort(last_modify_time='DESC').data
                    if len(obj_back) > 10:
                        os.remove(ph + '/index_' + str(obj_back[len(obj_back) - 1]['id']) + '.html')
                        self.db.object_back(id=obj_back[len(obj_back) - 1]['id']).delete()
                # 更新最新版
                f = open(ph + "/index.html", "w+")
                f.truncate()
                f.write(dat['html'])
            except IOError as err:
                l.error('File Error:'+str(err))
            finally:
                if 'f' in locals():
                    f.close()
            del dat['html']
            self.db.object(id=dat['id']).update(**{
                'name': dat['name'],
                'des': dat['des']
            })
            self.redirect('/sys/obj')
            return

class ObjectsHandler(object):
    '''
    yf: 专题
    '''
    def get(self):
        objs = self.db.object().data
        self.render('object.list.html', hl='list-object', objs=objs)

class ObjectBackHandler(object):
    '''
    yf: 专题回溯
    '''
    def post(self):
        import sys, os
        reload(sys)
        sys.setdefaultencoding('utf8')
        dat = self.json_decode(self.request.body)
        ph = os.path.dirname(__file__).split("app")[0] + 'assets/s/' + str(dat['object_id'])
        try:
            os.remove(ph + '/index.html')
            os.rename(ph + "/index_" + str(dat['id']) + ".html", ph + "/index.html")
            # 删除该回溯记录之后的记录
            objb = self.db.object_back(object_id=dat['object_id']).sort(last_modify_time='DESC').data
            del_ind = 0
            for index, item in enumerate(objb):
                if int(item['id']) == int(dat['id']):
                    del_ind = index
            for index, item in enumerate(objb):
                if index < del_ind:
                    self.db.object_back(id=item['id']).delete()
                    os.remove(ph + '/index_' + str(item['id']) + '.html')
            # 删除当前回溯
            self.db.object_back(id=dat['id']).delete()
        except IOError as err:
            l.error('File Error:'+str(err))
        self.redirect('/sys/obj/' + str(dat['object_id']))

class NotFoundHandler(object):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href='/sys'>back</a>")

url_prefix = '/sys/obj'

urls = [
    ('/?', ObjectsHandler),
    ('/(\d+)', ObjectHandler),
    ('/new', ObjectsNewHandler),
    ('/edit', ObjectEditHandler),
    ('/back', ObjectBackHandler)
]