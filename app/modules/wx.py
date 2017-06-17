# encoding: utf-8
from app.modules import base
import logging as l
import hashlib, json

class wx(base):
    def render(self, template_name, **kwargs):
        super(wx, self).render(template_name, **kwargs)

class CheckHandler(wx):
    '''
    yf: 网页授权获取用户基本信息
    '''
    def get(self):
        c = self.get_secure_cookie("c", None)
        path = self.get_argument('state', '')
        if c is None: # 2天内未在此设备上认证 或 重新登录了微信客户端
            code = self.get_argument('code', '')
            access_token = self.get_access_token(code)
            user = self.get_web_user(access_token)
            if 'unionid' in user:
                ud = self.db.client(openid=user['openid'], unionid=user['unionid']).one()
            else:
                ud = self.db.client(openid=user['openid']).one()
            if ud:
                self.set_secure_cookie("c", str(ud.id), expires_days=2)
                pass
            else:
                data = {
                    "openid": user['openid'],
                    "unionid": user['unionid'],
                    "nickname": user['nickname'],
                    "sex": user['sex'],
                    "province": user['province'],
                    "city": user['city'],
                    "country": user['country'],
                    "headimgurl": user['headimgurl']
                }
                if 'unionid' in user:
                    data['unionid'] = user['unionid']
                newu = self.db.client.add(**data)
                if newu:
                    self.set_secure_cookie("c", str(newu), expires_days=2)
                else:
                    self.write("Error!")
        self.render('act/index.html')
        return

    '''
    yf: 认证公众号
    '''
    def post(self):
        _token = "sohuweixin"
        sn = self.get_argument('signature', '')
        es = self.get_argument('echostr', '')
        a = ''.join(str(i) for i in sorted([_token, self.get_argument('timestamp', 't'), self.get_argument('nonce', 'n')]))

        if str(hashlib.sha1(a).hexdigest()) == str(sn):
            self.write(es)
        else:
            l.info("fail access")
    def check_xsrf_cookie(self):
        pass

class AjaxHandler(wx):
    '''
    yf: 公众号请求
    '''
    def get(self):
        self.check_tocken()
        self.write(self.getU())

    def post(self):
        l.info(self.request.headers)
        l.info(self.json_decode(self.request.body))

    def check_xsrf_cookie(self):
        pass

class WebHandler(wx):
    def get(self):
        l.info(self.request.headers)
        l.info(self.json_decode(self.request.body))

class AuthHandler(wx):
    def get(self):
        self.render('MP_verify_oai1jPbiuXyaD710.txt')

class NotFoundHandler(wx):
    def get(self):
        self.write("Sorry, Page not Found.. Go <a href=\"/\">back</a>")

url_prefix = '/wx'

urls = [
    ('/ajax?', AjaxHandler),
    ('/web', WebHandler),
    ('/auth/MP_verify_oai1jPbiuXyaD710.txt', AuthHandler),
    ('/auth/activity', CheckHandler)
]