# tornado
py web service.

环境搭建
-------------
1. 安装 python 2.7
2. 安装 tornado 3.2 [链接](https://github.com/tornadoweb/tornado/archive/v3.2.2.zip "链接")
3. 安装 Mysql 5.6
4. 安装 Mysql workbench [链接](http://dev.mysql.com/downloads/workbench/ "链接")
5. 安装 Python-Mysql [链接](https://pypi.python.org/packages/27/06/596ae3afeefc0cda5840036c42920222cb8136c101ec0f453f2e36df12a0/MySQL-python-1.2.5.win32-py2.7.exe#md5=6f43f42516ea26e79cfb100af69a925e "链接")

本地调试
-------------
1. 修改/app/config.conf文件，debug = True 以及 mysql 配置
2. 根目录在运行: python app.py
