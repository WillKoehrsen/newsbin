import spacy
import regex
import requests
import threading
import os
import queue
import time
import json
import regex

from package import filters
from dateutil.parser import parse
from bs4 import BeautifulSoup

from sqlalchemy import Column, Integer, String, Text, DateTime, exists
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

disambiguation = regex.compile('refer[s]?\s+to|stand\s+for\:')

def launch( function ):
	def wrapped_function( *args, **kwargs ):
		daemon = kwargs.pop('daemon',False)
		thread = threading.Thread(target=function,args=args,kwargs=kwargs)
		thread.daemon = daemon
		thread.start()
		return thread
	return wrapped_function

class Article(Base):
	__tablename__ = 'articles'
	id = Column(Integer, primary_key=True)

	link = Column(String(250), nullable=True)
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
		self.people = ','.join( set(names) )

	def get_people( self ):
		return self.people.split(',')

class Annotation(Base):
	__tablename__ = 'annotations'
	id = Column(Integer, primary_key=True)

	name = Column(String(250), nullable=True, unique=True)
	image = Column(String(250), nullable=True)
	summary = Column(Text, nullable=True)

	def __init__( self, *args, **kwargs ):
		for key, value in kwargs.items():
			setattr(self, key, value)

class Annotator:
	def __init__( self, *args, **kwargs ):
		self.count = kwargs.get('workers',10)
		self.sessionmaker = kwargs['sessionmaker']
		self.workers = []
		self.queue = queue.Queue()

	def add( self, *args ):
		args = sorted( args, key=len, reverse=True )
		for arg in args:
			if arg != None:
				self.queue.put(arg)

	def start( self ):
		for num in range(self.count):
			session = self.sessionmaker()
			self.workers.append( self.__worker( session ) )

	def stop( self ):
		self.queue.join()

		for worker in self.workers:
			self.queue.put( None )

		for worker in self.workers:
			worker.join()

	def __validate( self, name, session ):
		# get all names from the queue and the db
		prev_names = list(self.queue.queue)
		prev_names += [ it.name for it in session.query(Annotation).filter(Annotation.name.contains( name )).all() ]

		# check that name isn't
		for item in prev_names:
			if name in item and name != item:
				return False
		return True

	@launch
	def __worker( self, session ):
		while True:
			item = self.queue.get()

			if item != None:
				if self.__validate( item, session ):
					self.__annotate( item, session )
			else:
				break

			self.queue.task_done()

	def __annotate( self, name, session ):
		try:
			payload = {
				'action':'query',
				'titles':name,
				'format':'json',
				'prop':'extracts',
				'exintro':'',
				'explaintext':'',
				'redirects':'',
			}

			response = requests.get('https://en.wikipedia.org/w/api.php',params=payload)
			pages = json.loads(response.text)['query']['pages']
			test = str(pages)
			if len(pages)==1:
				summary = ''.join([ pages[pageid]['extract'] for pageid in pages if pageid!='-1'])
				if summary and not disambiguation.search(summary[:100]):
					annotation = Annotation(name=name,summary=summary)
					try:
						session.add(annotation)
						session.commit()
					except:
						session.rollback()
		except Exception as e:
			print('[annotator.__annotate failure] type: {}'.format(type(e)))

class Fetcher:
	def __init__( self, *args, **kwargs ):
		self.count = kwargs.get('workers',10)
		self.sessionmaker = kwargs['sessionmaker']
		self.callback = kwargs['callback']
		self.workers = []
		self.fetched = []
		self.queue = queue.Queue()
		self.nlp = spacy.load('en')

	def add( self, item ):
		if item.title not in self.fetched:
			self.queue.put(item)
			self.fetched.append(item.title)

	def start( self ):
		for num in range(self.count):
			session = self.sessionmaker()
			self.workers.append( self.__worker( session ) )

	def stop( self ):
		self.queue.join()

		for worker in self.workers:
			self.queue.put( None )

		for worker in self.workers:
			worker.join()

	@launch
	def __worker( self, session ):
		while True:
			item = self.queue.get()

			if item != None:
				article_found = session.query(exists().where(Article.title == item.title)).scalar()
				if not article_found:
					try:
						article = self.__fetch( item )
						if article.title and article.content:
							try:
								session.add(article)
								session.commit()
							except:
								session.rollback()
					except Exception as e:
						print('[fetcher.__worker failure] type: {}'.format(type(e)) )
			else:
				break

			self.queue.task_done()

	def __len__( self ):
		return len(self.queue)

	def __clean( self, name ):
		name = regex.sub( '\'s', '', name )
		name = max( regex.split('\"|\'|\(|\)|\,|\;',name), key=len )
		return name.strip(' ,.?\"\'()!-\{\}[]<>\n|\\/')

	def __find_people( self, content ):
		article = self.nlp( content )
		people = [ self.__clean( entity.text ) for entity in article.ents if entity.label_=='PERSON' ]
		return [ p for p in people if p ]

	def __fetch( self, article ):
		response = requests.get( article.link, verify=False )
		content = article.filter.process( response.text )
		people = self.__find_people( content['content'] )

		article.set_people( people )
		self.callback( *people )

		article.update( **content )
		return article

class Watcher:
	def __init__( self, *args, **kwargs ):
		self.sessionmaker = kwargs['sessionmaker']
		self.sources = kwargs['sources']
		self.callback = kwargs['callback']
		self.count = kwargs.get('workers',10)
		self.queue = queue.Queue()
		self.workers = []

	def __fetch( self, link, title, site_filter ):
		article = Article( title=title, link=link, filter=site_filter, source=site_filter.source_name )
		self.callback( article )

	@launch
	def __worker( self, *args, **kwargs ):
		while True:
			item = self.queue.get()

			if item != None:
				try:
					site_filter = item[0]
					feed = item[1]
					time.sleep(10)
					try:
						response = requests.get( feed )
						items = BeautifulSoup( response.text, 'html.parser' ).select('item')

						for it in items:
							self.__fetch( it.link.text, it.title.text, site_filter )

					except Exception as e:
						print('[watcher.__watch_feed failure] type: {}'.format(type(e)))
				except Exception as e:
					print('type: {} item:\n	{}'.format(type(e),item))
			else:
				break

			self.queue.task_done()
			if not self.no_loop.is_set():
				self.queue.put( item )


	def start( self ):
		self.no_loop = threading.Event()
		for _ in range(self.count):
			self.workers.append( self.__worker() )

		for source in self.sources:
			site_filter = filters.lookup( source )
			if site_filter:
				for feed in self.sources[source]:
					print('adding feed: ' + feed)
					self.queue.put( ( site_filter, feed ) )

	def stop( self ):
		self.no_loop.set()
		self.queue.join()

		for worker in self.workers:
			self.queue.put( None )

		for worker in self.workers:
			worker.join()

class Engine:
	def __init__( self, *args, **kwargs ):
		self.sessionmaker = kwargs['sessionmaker']
		self.sources = kwargs['sources']

		# the annotator accepts raw text from the fetcher
		# and parses out entity names to create annotations.
		# If the annotation:
		#		is unique (not in database)
		#		isn't the last portion of another name (like 'Smith' in Joe Smith)
		#		has a valid wikipedia page.
		# it gets pushed to the database.
		self.annotator = Annotator(
			sessionmaker=self.sessionmaker
			)
		# THREADS: 10 working queue

		# the fetcher tries to parse content from sites
		# and update given article objects (from watcher).
		# on success, it pushes articles to the database and
		# passes the article content to callback (self.annotator ^)
		self.fetcher = Fetcher(
			callback=self.annotator.add,
			sessionmaker=self.sessionmaker
			)
		# THREADS: 10 working queue

		# the watcher tracks all of the feeds in sources,
		# assembles preliminary article objects, and gives them
		# to callback (self.fetcher ^)
		self.watcher = Watcher(
			callback=self.fetcher.add,
			sessionmaker=self.sessionmaker,
			sources=self.sources
			)
		# THREADS: 10 working queue

	def start( self ):
		self.annotator.start()
		self.fetcher.start()
		self.watcher.start()

	def stop( self ):
		self.annotator.stop()
		self.fetcher.stop()
		self.watcher.stop()

if __name__=='__main__':
	pass
