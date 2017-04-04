import requests, json
from package import filters
from dateutil.parser import parse
from datetime import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()
import traceback

class Article(Base):
	__tablename__ = 'articles'
	id = Column(Integer, primary_key=True)
	url = Column(String(250), nullable=False)
	publish_date = Column(DateTime(timezone=True), nullable=False)
	title = Column(String(250), nullable=False)
	source = Column(String(10), nullable=False)
	content = Column(Text, nullable=False)


	def __init__( self, *args, **kwargs ):
		self.title = kwargs.get('title','')
		self.url = kwargs.get('url','')
		self.filter = kwargs.get('filter',None)

		try:
			self.publish_date = parse( kwargs.get('publish_date','') )
		except:
			self.publish_date = None

		try:
			self.source = self.filter.source_name
		except:
			self.source = ''

		self.__read( self.url )

	def __read( self, url ):
		try:
			response = requests.get( url, verify=False )
			article = self.__parse( response.text )

			self.author = article['author']
			self.content = article['content']
			if not self.publish_date:
				self.publish_date = article['publish_date']

		except Exception as e:
			print('Exception: {}'.format(e))
			traceback.print_exc()
			self.author = ''
			self.content = ''

	def __parse( self, content ):
		return self.filter.process( content )


	def is_valid( self ):
		if all(( self.title, self.content )):
			return True
		else:
			return False


if __name__=='__main__':
	# -------------------------------------------------------------------------
	# if called as a standalone script, build the database
	engine = create_engine('sqlite:///articles.db')
	Base.metadata.create_all(engine)

#	a = Article( 'http://www.cnn.com/2017/03/20/politics/james-comey-hearing-white-house-cloud/index.html', filter=filters.cnn, database='sqlite:///sqlalchemy_example.db' )
#	a.save()
