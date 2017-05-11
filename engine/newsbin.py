import regex
import requests
import queue
import time
import os
import wikipedia
import feedparser
import logging

from wikipedia.exceptions import DisambiguationError, PageError
from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError

# ------------------------------------------------------------------------------
# LOCALS
from package import defaults
from package import filters
from package import models
from package import manager

from package import session_generator
from package import db_engine
from package import settings

# ------------------------------------------------------------------------------
# GLOBALS
log = None

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
			log.exception('{} exception while processing annotation'.format(type(e)))

class Fetcher(manager.Manager):
	def __init__( self, *args, **kwargs ):
		self.passback = kwargs.pop('passback',None)
		super(Fetcher, self).__init__( *args, **kwargs, callback=self.__operation )

	def __operation( self, item, session ):
		try:
			response = requests.get( item.link, verify=False )
			content = item.filter.process( response.text )
			item.update( **content )

			print(item.title)

			# --------------removed spaCy and entity recognition--------------
			#people = self.__find_people( content['content'] )
			#item.set_people( people )
			#if self.passback: self.passback( *people )

			if item.title and item.content:
				try:
					session.add(item)
					session.commit()
				except:
					session.rollback()
					raise

		except IntegrityError as e:
			pass
			#print(e)
		except Exception as e:
			print('{} exception while fetching article'.format(type(e)))
			log.exception('{} exception while fetching article'.format(type(e)))

	def __clean( self, name ):
		name = regex.sub( '\'s', '', name )
		name = max( regex.split('\"|\(|\)|\,|\;',name), key=len )
		return name.strip(' ,.?\"\'()!-\{\}[]<>\n|\\/')

	def __find_people( self, content ):
		# --------------removed spaCy and entity recognition--------------
		#article = self.nlp( content )
		#people = [ self.__clean( entity.text ) for entity in article.ents if entity.label_=='PERSON' ]
		#return [ p for p in people if p ]
		return None

class Watcher(manager.Manager):
	def __init__( self, *args, **kwargs ):
		self.sources = kwargs.pop('sources')
		self.passback = kwargs.pop('passback',None)

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
				if self.passback: self.passback( article )

		except Exception as e:
			print('{} exception while parsing feed'.format(type(e)))
			log.exception('{} exception while parsing feed'.format(type(e)))

class Engine:
	def __init__( self, *args, **kwargs ):
		print('init engine:')

		self.sessionmaker = session_generator
		self.sources = defaults.sources

		self.annotator = None
		self.fetcher = None
		self.watcher = None

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			models.Base.metadata.create_all(db_engine)


		# the annotator accepts raw text from the fetcher
		# and parses out entity names to create annotations.
		# If the annotation:
		#		is unique (not in database)
		#		has a valid wikipedia page.
		# it gets pushed to the database.
		#print('	starting Annotator')
		#self.annotator = Annotator(
		#	sessionmaker=self.sessionmaker
		#	)
		# THREADS: 10 working queue

		# the fetcher tries to parse content from sites
		# and update given article objects (from watcher).
		# on success, it pushes articles to the database and
		# passes the article content to passback (self.annotator ^)
		print('	starting Fetcher')
		self.fetcher = Fetcher(
			#passback=self.annotator.add,
			sessionmaker=self.sessionmaker
			)
		# THREADS: 10 working queue

		# the watcher tracks all of the feeds in sources,
		# assembles preliminary article objects, and gives them
		# to passback (self.fetcher ^)
		print('	starting Watcher')
		self.watcher = Watcher(
			passback=self.fetcher.add,
			sessionmaker=self.sessionmaker,
			sources=self.sources,
			loop=True
			)
		# THREADS: 10 working queue

	def start( self ):
		print("Newsbin Engine Starting")
		log.info("Newsbin Engine Starting")
		#self.annotator.start()
		self.fetcher.start()
		self.watcher.start()

	def stop( self ):
		log.info("Newsbin Engine Stopping")
		#self.annotator.stop()
		self.fetcher.stop()
		self.watcher.stop()

if __name__=='__main__':
	log = logging.getLogger("newsbin.engine")
	log.setLevel(logging.ERROR)

	# create the logging file handler
	fh = logging.FileHandler( os.path.join( settings.logdir, 'newsbin_engine.log' ) )
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s:  %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
	fh.setFormatter(formatter)

	# add handler to log object
	log.addHandler(fh)

	engine = Engine()
	engine.start()
