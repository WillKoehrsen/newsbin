import spacy
import regex
import requests
import threading
import queue
import time
import json
import os
import sys
import wikipedia
import feedparser

from wikipedia.exceptions import DisambiguationError, PageError
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# ------------------------------------------------------------------------------
# LOCALS
try:
	import defaults
	import filters
	import models
	import manager
except:
	from package import defaults
	from package import filters
	from package import models
	from package import manager


# ------------------------------------------------------------------------------
# HOUSEKEEPING
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------------------------------------------------------------------
disambiguation = regex.compile('refer[s]?\s+to|stand\s+for\:')

class Annotator(manager.Manager):
	def __init__( self, *args, **kwargs ):
		super(Annotator, self).__init__( *args, **kwargs, callback=self.__operation )

	def __operation( self, name, session ):
		try:
			summary = wikipedia.summary(name)
			if summary:
				annotation = models.Annotation(name=name,summary=summary)
				try:
					session.add(annotation)
					session.commit()
				except:
					session.rollback()
					raise
		except (DisambiguationError, IntegrityError, PageError) as e:
			pass
		except Exception as e:
			print('[annotator.__operation failure] type: {}'.format(type(e)))

class Fetcher(manager.Manager):
	def __init__( self, *args, **kwargs ):
		self.passback = kwargs.pop('passback')
		self.nlp = spacy.load('en')
		super(Fetcher, self).__init__( *args, **kwargs, callback=self.__operation )

	def __operation( self, item, session ):
		try:
			response = requests.get( item.link, verify=False )
			content = item.filter.process( response.text )
			item.update( **content )
			people = self.__find_people( content['content'] )
			item.set_people( people )
			self.passback( *people )
			if item.title and item.content:
				try:
					session.add(item)
					session.commit()
				except:
					session.rollback()
					raise

		except IntegrityError as e:
			pass
		except Exception as e:
			print('[fetcher.__operation failure] type: {} - {}'.format(type(e),str(e)))

	def __clean( self, name ):
		name = regex.sub( '\'s', '', name )
		name = max( regex.split('\"|\(|\)|\,|\;',name), key=len )
		return name.strip(' ,.?\"\'()!-\{\}[]<>\n|\\/')

	def __find_people( self, content ):
		article = self.nlp( content )
		people = [ self.__clean( entity.text ) for entity in article.ents if entity.label_=='PERSON' ]
		return [ p for p in people if p ]

class Watcher(manager.Manager):
	def __init__( self, *args, **kwargs ):
		self.sources = kwargs.pop('sources')
		self.passback = kwargs.pop('passback')

		super(Watcher, self).__init__( *args, **kwargs, callback=self.__operation )
		feeds = [ ( filters.lookup( source ), feed ) for source in self.sources for feed in self.sources[source] if filters.exists( source )  ]
		self.add(*feeds)

	def __operation( self, block, session ):
		site_filter = block[0]
		feed = block[1]
		time.sleep(5)
		try:
			rss = feedparser.parse( feed )
			for item in rss['items']:
				article = models.Article( title=item['title'], link=item['link'], filter=site_filter, source=site_filter.source_name )
				self.passback( article )

		except Exception as e:
			print('[watcher.__watch_feed failure] type: {}'.format(type(e)))

class Engine:
	def __init__( self, *args, **kwargs ):
		self.sessionmaker = kwargs.get('sessionmaker',None)
		self.database = kwargs.get('database',None)
		self.sources = kwargs.get('sources',None)

		# use the current directory + 'newsbin.db'
		if not self.database:
			self.database = defaults.database

		# if no sessionmaker is given, create one and
		# init the database location
		bkup_engine = create_engine(self.database)

		if not self.sessionmaker:
			# get the sessionmaker
			self.sessionmaker = sessionmaker(bind=bkup_engine)

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( self.database ):
			models.Base.metadata.create_all(bkup_engine)

		if not self.sources:
			self.sources = defaults.sources

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
		# passes the article content to passback (self.annotator ^)
		self.fetcher = Fetcher(
			passback=self.annotator.add,
			sessionmaker=self.sessionmaker
			)
		# THREADS: 10 working queue

		# the watcher tracks all of the feeds in sources,
		# assembles preliminary article objects, and gives them
		# to passback (self.fetcher ^)
		self.watcher = Watcher(
			passback=self.fetcher.add,
			sessionmaker=self.sessionmaker,
			sources=self.sources,
			loop=True
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
	engine = Engine()
	engine.start()
