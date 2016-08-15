#!/usr/bin/env python
# encoding: utf-8
import logging as l

import os
import tornado.httpserver
import tornado.ioloop
import tornado.locale
import tornado.netutil
import tornado.process
import tornado.web
from tornado.options import options, define
from app.utils import db

define('mysql_database', default="test")
define('mysql_host', default="localhost")
define('mysql_user', default="0")
define('mysql_password', default="0")

define('debug', default=True)
define('template_path', default="templates")
define('static_path', default="assets")
define('static_url_prefix', default="/assets/")
define('cookie_secret', default="s")
define('cookie_domain', default="localhost")
define('login_url', default="/login")
define('xsrf_cookies', default=True)
define('port', default=8080)

class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            'template_path': os.path.join(os.path.dirname(__file__), options.template_path),
            'static_path': os.path.join(os.path.dirname(__file__), options.static_path),
            'static_url_prefix': options.static_url_prefix,
            'cookie_secret': options.cookie_secret,
            'cookie_domain': options.cookie_domain,
            'login_url': options.login_url,
            'debug': options.debug,
            'xsrf_cookies': options.xsrf_cookies,
        }
        super(Application, self).__init__(self.build_urls, **settings)

        self.db = db.DB(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

    @property
    def build_urls(self):
        '''
        自动装载各module 的网址
        '''
        handler_list = []
        files = os.listdir('./app/modules')
        files.sort()
        for f in files:
            if f.startswith("_"): # Filter __init__.py
                continue
            if f[-3:] != '.py': # Filter .pyc .DS_Store .svn ...
                continue
            module_name = f.split(".")[0]
            url_module = __import__('app.modules.%s' % module_name, globals(), locals(), ['urls', 'url_prefix'], 0)
            try:
                url_list = url_module.__dict__['urls']
                try:
                    prefix = url_module.__dict__['url_prefix']
                except KeyError:
                    prefix = '/' + module_name
                for handler in url_list:
                    new_handler = (prefix + handler[0], handler[1])
                    handler_list.append(new_handler)
                del(url_module)
            except KeyError:
                l.error('[%s] need "urls" list' % module_name)
        from app.modules import main
        handler_list.append((r'.*', main.NotFoundHandler))
        del(main)
        return handler_list

if __name__ == "__main__":
    # tornado.locale.load_translations(os.path.join(options.run_path, "locale"))
    tornado.options.parse_config_file('app/config.conf')
    tornado.options.parse_command_line()
    app = Application()
    if options.debug:
        print('debug --------------------')
        server = tornado.httpserver.HTTPServer(app, xheaders=True)
        server.listen(options.port)
    else:
        print('run --------------------')
        sockets = tornado.netutil.bind_sockets(options.port)
        tornado.process.fork_processes(0)
        server = tornado.httpserver.HTTPServer(app, xheaders=True)
        server.add_sockets(sockets)
    tornado.ioloop.IOLoop.current().start()