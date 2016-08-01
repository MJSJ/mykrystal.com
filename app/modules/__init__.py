#!/usr/bin/env python
# encoding: utf-8
"""
    __init__.py
    @author yf
    @version
    Copyright (c) 2013 yufeng All rights reserved.
"""
import tornado.web
import tornado.web, hmac, hashlib, datetime, json #, functools, urllib, os
from tornado.escape import json_decode
from tornado import escape
import decimal
import logging as l

def _default(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    else:
        return obj

class base(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("u")

    # def write(self, data):


    def write(self, chunk):
        if isinstance(chunk, dict):
            cb = self.get_argument("callback", None)
            if cb is not None:
                super(base, self).write(cb + '(' + json.dumps(chunk) + ')')
                self.set_header('Content-Type', 'application/javascript')
            else:
                chunk = json.dumps(chunk, default=_default).replace('</', "<\\/")
                self.set_header("Content-Type", "application/json; charset=UTF-8")
                chunk = escape.utf8(chunk)
                self._write_buffer.append(chunk)
        else:
            super(base, self).write(chunk)

    def hour(self, h=1):
        cur = datetime.datetime.now() - datetime.timedelta(minutes=int(h)*60)
        return "%d-%02d-%02d %02d:%02d:%02d" % (cur.year, cur.month, cur.day, cur.hour, cur.minute, cur.second)

    def set_default_headers(self):
        self.set_header('Server', 's')

    @property
    def now(self):
        return datetime.datetime.now()