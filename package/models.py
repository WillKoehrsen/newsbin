from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

# ------------------------------------------------------------------------------
# LOCALS
try:
	import defaults
	import filters
except:
	from package import defaults
	from package import filters
# ------------------------------------------------------------------------------
# HOUSEKEEPING
Base = declarative_base()

class Article(Base):
	__tablename__ = 'articles'
	id = Column(Integer, primary_key=True)

	link = Column(String(250), nullable=True, unique=True)
	source = Column(String(10), nullable=True)

	content = Column(Text, nullable=True)
	people = Column(Text, nullable=True)
	title = Column(String(250), nullable=True)
	author = Column(String(250), nullable=True)
	publish_date = Column(DateTime(timezone=True), nullable=True)

	def __init__( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def update( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def set_people( self, names ):
		self.people = ';'.join(names)

	def get_people( self ):
		return self.people.split(';')

class Annotation(Base):
	__tablename__ = 'annotations'
	id = Column(Integer, primary_key=True)

	name = Column(String(250), nullable=True, unique=True)
	image = Column(String(250), nullable=True)
	summary = Column(Text, nullable=True)

	def __init__( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)
