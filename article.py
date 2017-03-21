import filters, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Article(Base):
	__tablename__ = 'article'
	id = Column(Integer, primary_key=True)
	url = Column(String(250), nullable=False)
	title = Column(String(250), nullable=False)
	category = Column(String(100), nullable=False)
	content = Column(Text, nullable=False)


	def __init__( self, *args, **kwargs ):
		try:
			self.filter = kwargs['filter']
			self.database = kwargs['database']
			self.__read( args[0] )
		except:
			raise ValueError('need a filter, url and database in order to parse content')

	def __read( self, url ):
		response = requests.get( url, verify=False )

		self.url = url
		article = self.__parse( response.text )

		self.title = article['title']
		self.author = article['author']
		self.category = article['category']
		self.content = article['content']

	def __parse( self, content ):
		if self.filter:
			return self.filter( content )

	def save( self ):
		if self.title and self.content:
			session = sessionmaker( bind=create_engine(self.database) )()
			session.add(self)
			session.commit()
			return True
		else:
			return False

	def load( self ):
		session = sessionmaker( bind=create_engine(self.database) )()




if __name__=='__main__':
	# -------------------------------------------------------------------------
	# if called as a standalone script, build the database
	engine = create_engine('sqlite:///articles.db')
	Base.metadata.create_all(engine)

#	a = Article( 'http://www.cnn.com/2017/03/20/politics/james-comey-hearing-white-house-cloud/index.html', filter=filters.cnn, database='sqlite:///sqlalchemy_example.db' )
#	a.save()
