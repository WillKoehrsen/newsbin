from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

import json

from package import defaults
from package import politifact

# ------------------------------------------------------------------------------
# HOUSEKEEPING
Base = declarative_base()

class Article(Base):
	__tablename__ = 'articles'
	id = Column(Integer, primary_key=True)

	link = Column(String(250), nullable=True, unique=True)
	source = Column(String(10), nullable=True)

	content = Column(Text, nullable=True )
	blacklist = Column(Text, nullable=True)
	title = Column(String(250), unique=True)
	author = Column(String(100), nullable=True)
	category = Column(String(250), nullable=True)
	fetched = Column(DateTime(timezone=True), nullable=True)

	# this is a temporary value for templating,
	# it is only set immediately before serving
	category_label = '';

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
		if name and name not in plist:
			plist.append( name )
			self.set_blacklist(plist)

	def unblacklist_name( self, name ):
		plist = [ n for n in self.get_blacklist() if n != name ]
		self.set_blacklist( plist )

	def serialize( self, **kwargs ):
		variables = { key:value for key,value in vars( self ).items() if not key.startswith('_') }
		variables['fetched'] = str(variables['fetched'])
		variables['source_label'] = self.get_source()
		variables['category_label'] = self.get_category()
		return variables

	def deserialize( self, variables ):
		try:
			variables = json.loads(variables)
			for key,value in variables.items():
				self.__setattr__( key, value )
		except ValueError as e:
			raise

	def get_intro( self ):
		return regex.sub('<.*?>','',self.content[:160].replace('cite>','cite> '))

	def get_source( self ):
		return defaults.labels.get(self.source,None)

	def get_category( self ):
		return defaults.labels.get(self.category,None) or self.category.capitalize()

class Annotation(Base):
	__tablename__ = 'annotations'
	id = Column(Integer, primary_key=True)

	name = Column(String(250), nullable=True, unique=True)
	slug = Column(String(250), nullable=True)
	image = Column(Text, nullable=True)
	summary = Column(Text, nullable=True)

	wikiname = Column(String(250), nullable=True)
	wikilink = Column(String(250), nullable=True)

	def __init__( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def update( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def get_ratings( self ):
		table_items = []
		rating, slug = politifact.get_rating(name=self.name,slug=self.slug)
		if rating != None:
			table_items.append({'key':'Truth Score','value':'{}%'.format(rating)})

		return table_items

	def serialize( self, **kwargs ):
		variables = { key:value for key,value in vars( self ).items() if not key.startswith('_') }
		variables['data_table'] = self.get_ratings()
		variables.update(kwargs)
		return variables
