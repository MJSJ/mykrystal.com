#!/usr/bin/env python
# encoding: utf-8
"""
db.py

a simple orm around torndb
"""
import logging
from tornado.escape import to_unicode as _unicode
# 新版本的tornado 独立了 db库
import torndb as database
from torndb import Row, itertools

class DB(database.Connection):
	def __init__(self, host, database, user=None, password=None,
				max_idle_time=7 * 3600, connect_timeout=3600,
				time_zone="+8:00"):
		super(DB, self).__init__(host=host, database=database, user=user, password=password,
				max_idle_time=max_idle_time, connect_timeout=connect_timeout,
				time_zone=time_zone)
		try:
			self.reconnect()
		except Exception:
			logging.error("Cannot connect to MySQL on %s", self.host, exc_info=True)

	def reconnect(self):
		super(DB, self).reconnect()
		logging.info("Reconnect DB")

	def _execute(self, cursor, query, parameters, kwparameters):
		logging.info(query, *parameters)
		super(DB, self)._execute(cursor, query, parameters, kwparameters)

	def query(self, query, *parameters, **kwparameters):
		"""Returns a row list for the given query and parameters."""
		cursor = self._cursor()
		try:
			self._execute(cursor, query, parameters, kwparameters)
			column_names = [d[0] for d in cursor.description]
			try: # Python 3.x
				return [Row(itertools.zip_longest(column_names, row)) for row in cursor]
			except AttributeError: # Python 2.x
				return [Row(itertools.izip(column_names, row)) for row in cursor]
		finally:
			cursor.close()
	#==============================================================================
	# get this table
	# e.g: users_db = self.db.users
	#==============================================================================
	def __getattr__(self, table):
		return TableQueryer(self, table)
	#==============================================================================
	# get this table
	# e.g: users_db = self.db('users')
	#==============================================================================
	def __call__(self, table):
		return TableQueryer(self, table)
class TableQueryer(object):
	def __init__(self, db, table):
		self._table = table
		self._db = db
	def __call__(self, query=None, **kwargs):
		cond = None
		for k in kwargs.keys():
			if cond is None:
				cond = eval('self.%s=="%s"'%(k,kwargs[k]))
			else:
				cond & eval('self.%s=="%s"'%(k,kwargs[k]))
			if query is None:
				query = cond
		return Operater(self._db, self._table, query, self)

	#==============================================================================
	# insert database
	# user_db see DB.__getattr__
	# users_db.insert(email='xs23933@gmail.com', password='password')
	# or
	# self.db.insert('users', email='xs23933@gmail.com', password='password')
	# gen sql:
	# INSERT INTO `users`(`email`,`password`) VALUES('xs23933@gmail.com','password')
	#==============================================================================
	def insert(self, **fields):
		return Insert(self._db, self._table)(**fields)
	#==============================================================================
	# add
	# insert alias, see insert
	#==============================================================================
	def add(self, **fields):
		''' insert alias'''
		return Insert(self._db, self._table)(**fields)
	def readd(self, **fields):
		''' reinsert alias'''
		return Readd(self._db, self._table)(**fields)
	def __getattr__(self, field):
		return conds(field)

class Operater(object):
	def __init__(self, db, table, query, queryer):
		self._q = query
		self.add = Insert(db, table)
		self.insert = Insert(db, table)
		self.readd = Readd(db, table)
		self.find = Select(db, table, query)
		self.select = Select(db, table, query)
		self.update = Update(db, table, query, queryer)
		self.delete = Delete(db, table, query)
	#==============================================================================
	# one
	# self.db.users(id=1).one()
	# SELECT * FROM `users`  WHERE `id`=1
	#==============================================================================
	def one(self):
		dat = self.select()
		if len(dat)>0:
			return dat[0]
		return None
	#==============================================================================
	# sort
	# order by sort
	# e.g:
	# user_db().sort(id='DESC')).data
	# gen sql:
	# SELECT * FROM `users` ORDER BY `id` DESC
	# e.g:
	# q = user_db().sort(id='DESC', email='ASC')
	# q.data
	# or:
	# user_db().sort(id='DESC', email='ASC').data
	# gen sql:
	# SELECT * FROM `users` ORDER BY `id` DESC,`email` ASC
	#==============================================================================
	def sort(self, **kwargs):
		return self.select.sort(**kwargs)
	#==============================================================================
	# group_by
	# e.g: user_db().group_by(user_db.id,user_db.email).data
	# gen sql:
	# SELECT * FROM `users` GROUP BY id,email
	#==============================================================================
	def group_by(self, *kwargs):
		return self.select.group_by(*kwargs)
	#==============================================================================
	# get pre_page data
	# Must need page number
	#          current page
	#                ↓
	# e.g: user_db()[2:10]
	#                  ↑
	#               page size
	# Complete e.g:
	#  dat = user_db()[2:10]
	#  for item in dat.object_list:
	#   print item.id
	#  next page num: dat.nextpage
	#  prev page num: dat.prevpage
	#==============================================================================
	@property
	def object_list(self):
		return self.select.object_list()
	#==============================================================================
	# return select data
	# e.g: user_db().data
	#==============================================================================
	@property
	def data(self):
		return self.select.data
	#==============================================================================
	# Pre page
	#          current page
	#                ↓
	# e.g: user_db()[2:10].data
	#                  ↑
	#               page size
	# gen sql: SELECT * FROM `users`  LIMIT 2,10
	#==============================================================================
	def __getslice__(self, pid, psize):
		return self.select.__getslice__(pid, psize)

class Options(object):
	def __init__(self, db, table, where):
		self._db = db
		self._table = table
		self._where = where

class Select(Options):
	def __init__(self, db, table, where):
		super(Select, self).__init__(db, table, where)
		self._fields = []
		self._limit=None
		self._groups = []
		self._sort_fields = []
		self._having = None
		self._paginator = False
		self._psize = None
		self._pid = None
		self._curpage = 1
		self._nextpage = None
		self._prevpage = None
	def collect(self,*fields):
		if len(fields):
			self._fields+=fields
		return self
	def fields(self, fields):
		self._fields+=fields
		return self
	@property
	def object_list(self):
		if self._pid is None or self._psize is None:
			raise database.OperationalError("Must set Page pre num")
			# raise database.OperationalError, 'Must Set Page pre num'
		self._paginator = True
		self._limit = ''.join(['LIMIT ', str(self._pid), ',', str(self._psize+1)])
		data = self.__call__()
		self._limit = ''.join(['LIMIT ', str(self._pid), ',', str(self._psize)])
		self._paginator = False
		if len(data) > self._psize:
			data = data[:-1]
			self._nextpage = self._curpage+1
		else:
			self._nextpage = None
		if self._curpage > 1:
			self._prevpage = self._curpage-1
		else:
			self._prevpage = None
		return data
	@property
	def nextpage(self):
		if self._nextpage <= self._curpage:
			return False
		return self._nextpage
	@property
	def prevpage(self):
		return self._prevpage

	#==============================================================================
	# data
	# get select data
	# see Operater.data
	#==============================================================================
	@property
	def data(self):
		return self.__call__()
	def one(self):
		dat = self.__call__()
		if len(dat)>0:
			return dat[0]
		return None
	#==============================================================================
	# get select data
	# see Operater.data
	# e.g: user_db().sort(id='DESC')()
	# gen sql:
	# SELECT * FROM `users` ORDER BY `id` DESC
	#==============================================================================
	def __call__(self):
		_sql = self.get_sql()
		_plist = []
		if self._table.__class__.__name__ == 'Select':
			for p in self._table.get_sql():
				_plist.append(p)
		if self._where:
			for p in self._where.get_params():
				_plist.append(p)
		if self._having:
			for p in self._having.get_params():
				_plist.append(p)
		if _plist:
			return self._db.query(_sql, *_plist)
		else:
			return self._db.query(_sql)
	def sort(self, **fields):
		del self._sort_fields[:]
		for key in fields.keys():
			self._sort_fields.append(''.join(['`', key, '` ', fields[key]]))
		return self
	def group_by(self, *fields):
		if len(fields)<1:
			raise database.OperationalError("must nave a field")
			# raise database.OperationalError, 'Must have a field'
		for f in fields:
			self._groups.append(f)
		return self
	def having(self, cond):
		self._having = cond
	def __getslice__(self, pid, psize):
		if pid<1:
			pid = 1
		if psize<1:
			pid = 1
		self._pid = (int(pid)-1)*int(psize)
		self._curpage = pid
		self._psize = psize
		self._limit = ''.join(['LIMIT ', str(self._pid), ',', str(psize)])
		return self
	def get_sql(self):
		_sql_slice = ['SELECT ']
		if self._fields:
			_sql_slice.append(','.join([str(f) for f in self._fields]))
		else:
			_sql_slice.append('*')
		_sql_slice.append(' FROM `')
		if self._table.__class__.__name__ == 'Select':
			_sql_slice.append('(')
			_sql_slice.append(self._table.get_sql())
			_sql_slice.append(')t ')
		else:
			_sql_slice.append(self._table)
		_sql_slice.append('` ')
		if self._where:
			_sql_slice.append(' WHERE ')
			if self._table.__class__.__name__ == 'Select':
				_sql_slice.append(self._where.get_sql(tn='t'))
			else:
				_sql_slice.append(self._where.get_sql())
			_sql_slice.append(' ')
		if len(self._groups)>0: #have group by
			_sql_slice.append('GROUP BY ')
			if self._table.__class__.__name__ == 'Select':
				_sql_slice.append(','.join([f.get_sql(tn='t') for f in self._groups]))
			else:
				x = []
				for f in self._groups:
					if f.__class__.__name__ == 'str':
						x.append(f)
					else:
						x.append(f.get_sql())

				_sql_slice.append(','.join(x))
			if self._having:
				_sql_slice.append(' HAVING ')
				_sql_slice.append(self._having.get_sql())
			_sql_slice.append(' ')
		if self._sort_fields:
			_sql_slice.append('ORDER BY ')
			if self._table.__class__.__name__ == 'Select':
				_sql_slice.append(','.join([self._add_tb('t',s) for s in self._sort_fields]))
			else:
				_sql_slice.append(','.join([s for s in self._sort_fields]))
		if self._limit:
			_sql_slice.append(' ')
			_sql_slice.append(self._limit)
		return ''.join(_sql_slice)

	def _add_tb(self, tn, src):
		p = compile(r'`(\w*?)`')
		return p.sub(r'`%s.\1`'%tn,src)
#===============================================================================
# Insert
# See TableQueryer.Insert
#===============================================================================
class Insert(Options):
	'''
	e.g:
	self.db.add(table, abc=1,bc=2)
	self.db.users.add(abc=1,bc=2)
	'''
	def __init__(self, db, table):
		super(Insert, self).__init__(db, table, None)
	def __call__(self, **fields):
		columns = fields.keys()
		_prefix = ''.join(['INSERT INTO `', self._table, '`'])
		_fields = ','.join([''.join(['`', column, '`']) for column in columns])
		_values = ','.join(['%s' for i in range(len(columns))])
		_sql = ''.join([_prefix, '(', _fields, ') VALUES(', _values, ')'])
		_params=[fields[key] for key in columns]
		return self._db.execute(_sql,*tuple(_params))
class Readd(Options):
	'''
	e.g:
	self.db.readd(table, abc=1,bc=2)
	self.db.users.readd(abc=1,bc=2)
	'''
	def __init__(self, db, table):
		super(Readd, self).__init__(db, table, None)
	def __call__(self, **fields):
		columns = fields.keys()
		_prefix = ''.join(['REPLACE INTO `', self._table, '`'])
		_fields = ','.join([''.join(['`', column, '`']) for column in columns])
		_values = ','.join(['%s' for i in range(len(columns))])
		_sql = ''.join([_prefix, '(', _fields, ') VALUES(', _values, ')'])
		_params=[fields[key] for key in columns]
		return self._db.execute(_sql,*tuple(_params))


#===============================================================================
# Update
# self.db.users(id=1000).update(email='xs23933@gmail.com')
# e.g:
# user_db(id=1000).update(id=100, email='xs23933@gmail.com')
# UPDATE users SET `email`='xs23933@gmail.com',`id`='100' WHERE `id`='1000'
# or
# user_db(id=1000).update(user_db.id==user_db.id+1, user_db.email=='xs23933@gmail.com')
# UPDATE `users` SET `id`=`id`+1,`email`=xs23933@gmail.com WHERE `id`=1000
#===============================================================================
class Update(Options):
	def __init__(self, db, table, query, queryer):
		super(Update, self).__init__(db, table, query)
		self._queryer = queryer
	'''
		e.g:
		user = self.db.users
		q = user(user.id.In(['100','200','300','400'])) & (user.id.Not_In([500,600,700]))
		q.update(user.id==user.id+100000, user.email=='xs@gmail.com')
	'''
	def __call__(self, *fields, **kwargs):
		_params = []
		_cols = []
		if len(fields)<1 and not kwargs:
			raise database.OperationalError("Update need some date")
			# raise database.OperationalError, 'Update Need some data'
		elif kwargs:
			for k in kwargs.keys():
				if type(kwargs[k]).__name__ == 'unicode':
					cond = eval(''.join(['self._queryer.', k, "==u'''", kwargs[k].replace("'''", "\\'\\'\\'"), "'''"]))
				elif type(kwargs[k]).__name__ == 'int' or type(kwargs[k]).__name__ == 'long':
					cond = eval(''.join(['self._queryer.', k, "==u'''", str(kwargs[k]), "'''"]))
				elif type(kwargs[k]).__name__ == 'datetime':
					cond = eval(''.join(['self._queryer.', k, "==u'", unicode(kwargs[k]), "'"]))
				else:
					cond = eval(''.join(['self._queryer.', k, "==u'", _unicode(kwargs[k]), "'"]))
				_cols.append(cond.get_sql())
				_params.append(cond.get_params()[0])
		else:
			for f in fields:
				_cols.append(f.get_sql())
				_params.append(f.get_params()[0])
		_sql_slice = ['UPDATE `', self._table, '` SET ', ','.join(_cols)]
		if self._where:
			_sql_slice.append(' WHERE ')
			_sql_slice.append(self._where.get_sql())
			for p in self._where.get_params():
				_params.append(p)
			_sql = ''.join(_sql_slice)
			return self._db.execute(_sql,*_params)
		raise database.OperationalError("Update need where")
		# raise database.OperationalError, 'Update Need Where'
#===============================================================================
# Delete
# user_db(id=1000).delete()
# user_db(user_db.id==1000).delete()
# DELETE FROM `users` WHERE `id`=1000
#===============================================================================
class Delete(Options):
	''' see Update '''
	def __call__(self):
		_sql_slice = ['DELETE FROM `', self._table, '`']
		if self._where:
			_sql_slice.append(' WHERE ')
			_sql_slice.append(self._where.get_sql())
			_sql = ''.join(_sql_slice)
			return self._db.execute(_sql, *self._where.get_params())
		raise database.OperationalError("Delete data must need some where")
		# raise database.OperationalError, 'Delete Data Must Need some Where'
class conds(object):
	def __init__(self, field):
		self._field = field
		self._has_value = False
		self._params = []
		self._sub_conds = []
#		print field
	def __getattr__(self, attr):
		if not self._has_value:
			if attr.__class__.__name__ == 'str':
				return self
			if attr.__class__.__name__ == 'Select':
				self._field = ''.join([attr, '(t.', self._field, ') as ', attr, '_', self._field])
			else:
				self._field = ''.join([attr, '(', self._field, ') as ', attr, '_', self._field])
			return self
		raise database.OperationalError("Multiple Operate conditions")
		# raise database.OperationalError, 'Multiple Operate conditions'

	def __str__(self):
		if self._has_value:
			return self._sql
		else:
			return self._field

	def _prepare(self, sql, value):
		if not self._has_value:
			self._sql = sql
			self._params.append(value)
			self._has_value = True
			return self
		raise database.OperationalError("Multiple operate onditions")
		# raise database.OperationalError, 'Multiple Operate onditions'

	def __eq__(self,value):
		if not self._has_value:
			if value.__class__.__name__ == 'conds':
				self._sql = ''.join(['`', self._field, '`=', value.get_sql()])
				self._params.append(value.get_params()[0])
			else:
				self._sql = ''.join(['`', self._field, '`=%s'])
				self._params.append(value)
			self._has_value = True
			return self
		raise database.OperationalError("Multiple operate conditions")
		# raise database.OperationalError,"Multiple Operate conditions"
	def like(self, value):
		return self._prepare(''.join(['`', self._field, '` like %s']), value)
	def DL(self, value, format='%%Y-%%m-%%d'):
		return self._prepare(''.join(['DATE_FORMAT(`', self._field,"`, '",format, "') <= %s"]),value)
	def DG(self, value, format='%%Y-%%m-%%d'):
		return self._prepare(''.join(['DATE_FORMAT(`', self._field,"`, '",format, "') >= %s"]),value)
	def DE(self, value, format='%%Y-%%m-%%d'):
		return self._prepare(''.join(['DATE_FORMAT(`', self._field,"`, '",format, "') = %s"]),value)
	def null(self):
		self._sql = ''.join(['`', self._field, '` is null'])
		return self
	def notnull(self):
		self._sql = ''.join(['`', self._field, '` is not null'])
		return self

	def __le__(self,value):
		return self._prepare("".join(["`", self._field, '`<=%s']), value)
	def __lt__(self,value):
		return self._prepare("".join(["`", self._field, '`<%s']), value)
	def __gt__(self,value):
		return self._prepare("".join(["`", self._field, '`>%s']), value)
	def __ge__(self,value):
		return self._prepare("".join(["`", self._field, '`>=%s']), value)
	def __sub__(self, value):
		return self._prepare(''.join(['`', self._field, '`-%s']), value)
	def __add__(self, value):
		return self._prepare(''.join(['`', self._field, '`+%s']), value)
	def __ne__(self, value):
		return self._prepare(''.join(['`', self._field, '`<>%s']), value)
	# 附加合并查询
	def __or__(self, cond):
		if self._has_value:
			self._sub_conds.append((cond," OR "))
			return self
		raise database.OperationalError("Operation with no value")
		# raise database.OperationalError,"Operation with no value"
	def __and__(self, cond):
		if self._has_value:
			self._sub_conds.append((cond," AND "))
			return self
		raise database.OperationalError("Operation with no value")
		# raise database.OperationalError,"Operation with no value"
	def __ror__(self, cond):
		if self._has_value:
			cond._q._sub_conds.append((self, ' OR '))
			return cond
		raise database.OperationalError("Operation with no value")
		# raise database.OperationalError, 'Operation with no value'
	def __rand__(self, cond):
		if self._has_value:
			cond._q._sub_conds.append((self, ' AND '))
			return cond
		raise database.OperationalError("Operation with no value")
		# raise database.OperationalError, 'Operation with no value'
	def get_sql(self, tn=None):
		_sql_slice = []
		_sql_slice.append(str(self._sql))
		if len(self._sub_conds):
			for cond in self._sub_conds:
				_sql_slice.append(cond[1])
				_sql_slice.append(cond[0].get_sql())
		_where = ''.join(_sql_slice)
		if tn:
			p=compile(r'`(\w*?)`')
			_where = p.sub(r'`%s.\1`'%tn,_where)
		return _where

	def get_params(self):
		_my_params = []+self._params
		if len(self._sub_conds):
			for cond in self._sub_conds:
				_my_params+=cond[0].get_params()
		return _my_params
	def In(self,array):
		'''
		@param array: list or Select
		e.g: q = user(user.id.In([1,2,3,4,5])) '''
		if not self._has_value:
			if array.__class__.__name__ == "Select":
				self._sql="".join(["`",self._field,'`',' in (',array.get_sql(),")"])
				for p in array.get_params():
					self._params.append(p)
			else:
				_values=",".join(["".join(["'",str(i),"'"]) for i in array])
				self._sql="".join(["`",self._field,'`',' in (',_values,")"])
				self._has_value=True
			return self
		raise database.OperationalError("Multiple operate conditions")
		# raise database.OperationalError,"Multiple Operate conditions"

	def Not_In(self,array):
		''' see In '''
		if not self._has_value:
			if array.__class__.__name__ == "Select":
				self._sql="".join(["`",self._field,'`',' not in (',array.get_sql(),")"])
				for p in array.get_params():
					self._params.append(p)
			else:
				_values=",".join(["".join(['\'',str(i),'\'']) for i in array])
				self._sql="".join(["`",self._field,'`',' not in (',_values,")"])
				self._has_value=True
			return self
		raise database.OperationalError("Multiple operate conditions")
		# raise database.OperationalError,"Multiple Operate conditions"

