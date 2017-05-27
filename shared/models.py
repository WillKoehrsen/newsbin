from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

import json

# ------------------------------------------------------------------------------
# HOUSEKEEPING
Base = declarative_base()

class Article(Base):
	__tablename__ = 'articles'
	id = Column(Integer, primary_key=True)

	link = Column(String(250), nullable=True, unique=True)
	source = Column(String(10), nullable=True)

	content = Column(Text, nullable=True, unique=True)
	blacklist = Column(Text, nullable=True)
	title = Column(String(250), unique=True)
	author = Column(String(100), nullable=True)
	category = Column(String(250), nullable=True)
	fetched = Column(DateTime(timezone=True), nullable=True)

	def __init__( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def update( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def set_blacklist( self, names ):
		self.blacklist = ';'.join(set(names))

	def get_blacklist( self ):
		return self.blacklist.split(';') if self.blacklist else []

	def blacklist_name( self, name ):
		plist = self.get_blacklist()
		if name not in plist:
			plist.append( name )
			self.set_blacklist(plist)

	def unblacklist_name( self, name ):
		plist = [ n for n in self.get_blacklist() if n != name ]
		self.set_blacklist( plist )

	def serialize( self ):
		variables = { str(key):str(value) for key,value in vars( self ).items() if not key.startswith('_') }
		return json.dumps( variables )

	def deserialize( self, variables ):
		try:
			variables = json.loads(variables)
			for key,value in variables.items():
				self.__setattr__( key, value )
		except ValueError as e:
			raise

class Annotation(Base):
	__tablename__ = 'annotations'
	id = Column(Integer, primary_key=True)

	name = Column(String(250), nullable=True, unique=True)
	image = Column(String(250), nullable=True)
	summary = Column(Text, nullable=True)

	def __init__( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def serialize( self ):
		variables = { str(key):str(value) for key,value in vars( self ).items() if not key.startswith('_') }
		return json.dumps( variables )
