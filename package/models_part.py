import traceback
import spacy
import json
import regex
import requests
import difflib
import threading
import time
import os

#from package import filters
from dateutil.parser import parse
from datetime import datetime
from bs4 import BeautifulSoup

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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

			self.people = self.__get_people()
			for name in self.people:
				self.annotate( name )

			self.content = ''.join([ '<p>{}</p>\n'.format(p) for p in self.content.split('\n\n') if p ])

		except Exception as e:
			print('Exception: {}'.format(e))
			traceback.print_exc()
			self.author = ''
			self.content = ''
			self.people = []

	def __parse( self, content ):
		return self.filter.process( content )

	def __clean( self, name ):
		name = max( regex.split( '\"|\'s$|\'|\(|\)|\,', name.strip() ), key=len )
		return name.strip(' ,.?\"\'()!-\{\}[]<>\n|\\/')

	def __get_people( self ):
		nlp = spacy.load('en')
		chunked = nlp( self.content )
		names = [ self.__clean(e.text) for e in chunked.ents if e.label_=='PERSON' ]
		return [ name for name in names if name ]

	def __expand( self, name ):
		for person in sorted(self.people,key=len,reverse=True):
			if person.endswith(name):
				return person

	def annotate( self, name ):
		replacement = '<span class=\"summarize\" value=\"{}\">{}</span>'.format( self.__expand(name), name )
		self.content = regex.sub('(?<!value=\".*?|>){}(?!<|.*?\">)'.format( regex.escape(name) ), replacement, self.content )

	def is_valid( self ):
		if all(( self.title, self.content )):
			return True
		else:
			return False

class Annotator:
	def __init__( self, *args, **kwargs ):
		self.count = kwargs.get('workers',8)
		self.workers = []
		self.queue = Queue()
		for value in kwargs.get('values',[]):
			self.queue.put( value )
		self.__start()

	def __start( self ):
		for num in range(self.count):
			thread = threading.Thread(target=self.__run)
			thread.start()
			self.workers.append( thread )

	def __run( self ):
		while True:
			item = self.queue.get()

			if item == None:
				break
			else:
				self.__annotate( item )

			self.queue.task_done()

	def __annotate( self, name ):
		print( name )

	def add( self, value ):
		self.queue.put(value)

	def stop( self ):
		self.queue.join()

		for worker in self.workers:
			self.queue.put( None )

		for worker in self.workers:
			worker.join()

class FeedWatcher:
	def __init__( self, *args, **kwargs ):
		self.filter = kwargs['filter']
		self.database = kwargs['database']
		self.feed = kwargs['feed']
		self.last_etag = ''

		self.__setup()

	def __setup( self ):
		self.__stop = threading.Event()

	def __parse( self, item ):
		if item.title and item.link:
			link = item.link.text.strip()
			title = item.title.text.strip()
			pubdate = item.pubDate.text.strip() if item.pubDate else None

			#article_exists = self.database.query(exists().where(Article.title == title)).scalar()

			#if not article_exists:
			#	article = Article(title=title,url=link,publish_date=pubdate, filter=self.filter)
			#	if article.is_valid():
			#		self.database.add(article)
			#		self.database.commit()

	def __run( self ):
		while not self.__stop.is_set():
			headers = requests.head( self.feed ).headers
			new_etag = headers['etag'] if 'etag' in headers else ''
			if not new_etag or new_etag!=self.last_etag:
				response = requests.get( self.feed )
				items = BeautifulSoup( response.text, 'html.parser' ).select('item')
				for item in items:
					self.__parse( item )
				self.last_etag = new_etag

	def start( self ):
		self.thread = threading.Thread(target=self.__run)
		self.thread.start()

	def stop( self ):
		self.__stop.set()
		self.thread.join()

class SourceWatcher:
	def __init__( self, *args, **kwargs ):
		self.sessionmaker = kwargs['sessionmaker']
		self.sources = kwargs['sources']
		self.watchers = []

		self.__setup()

	def __setup( self ):
		for source in self.sources:
			pass
			#site_filter = filters.lookup( source )
			#if site_filter:
			#	for feed in self.sources[source]:
			#		session = self.sessionmaker()
			#		watcher = FeedWatcher(feed=feed, filter=site_filter, database=session )
			#		self.watchers.append( watcher )

	def start( self ):
		for watcher in self.watchers:
			watcher.start()

	def stop( self ):
		for watcher in self.watchers:
			watcher.stop()

if __name__=='__main__':
	#site_filter = filters.lookup('cnn')
	site_filter = 'cnn'
	db_engine = create_engine('sqlite:////home/mhouse/Projects/python/newsannotation/articles.db')

	# get the sessionmaker
	Session = sessionmaker(bind=db_engine)

	# if the database specified by config doesn't exist, create it.
	if not os.path.isfile('sqlite:////home/mhouse/Projects/python/newsannotation/articles.db'):
		Base.metadata.create_all(db_engine)

	session=Session()
	feedwatcher = FeedWatcher(feed='http://rss.cnn.com/rss/cnn_world.rss', filter=site_filter, database=session)
	feedwatcher.start()
