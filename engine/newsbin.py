import regex
import requests
import queue
import time
import os
import wikipedia
import feedparser
import logging
import signal
import sys

from requests.exceptions import InvalidSchema
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
engine = None

# ------------------------------------------------------------------------------
# HOUSEKEEPING
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------------------------------------------------------------------

class Fetcher(manager.Manager):
	def __init__( self, *args, **kwargs ):
		self.passback = kwargs.pop('passback',None)
		super(Fetcher, self).__init__( *args, **kwargs, callback=self.__operation )

		log.info('Fetcher initialized')

	def __operation( self, item, session ):
		try:
			response = requests.get( item.link, verify=False )
			content = item.filter.process( response.text )
			item.update( **content )

			if item.title and item.content:
				try:
					session.add(item)
					session.commit()
				except:
					session.rollback()
					raise

		except IntegrityError as e:
			pass
		except ConnectionError as e:
			log.warning('Connection reset (ConnectionError) while fetching article: {}'.format(item.link))
		except InvalidSchema as e:
			log.warning('Article is video/other (InvalidSchema) while fetching article: {}'.format(item.link))
		except Exception as e:
			log.exception('{} exception while fetching article'.format(type(e)))

class Watcher(manager.Manager):
	def __init__( self, *args, **kwargs ):
		self.sources = kwargs.pop('sources')
		self.passback = kwargs.pop('passback',None)

		super(Watcher, self).__init__( *args, **kwargs, callback=self.__operation )
		feeds = [ item for item in self.sources if filters.exists( item[0] ) ]
		self.add(*feeds)

		log.info('Watcher initialized')

	def __operation( self, block, session ):
		source, feed, category = block
		site_filter = filters.lookup(source)

		time.sleep(5)
		try:
			rss = feedparser.parse( feed )
			for item in rss['items']:
				article = models.Article( title=item['title'], link=item['link'], filter=site_filter, source=source, category=category )
				if self.passback: self.passback( article )

		except Exception as e:
			log.exception('{} exception while parsing feed'.format(type(e)))

class Engine:
	def __init__( self, *args, **kwargs ):
		self.sessionmaker = session_generator
		self.sources = defaults.sources

		self.fetcher = None
		self.watcher = None

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			models.Base.metadata.create_all(db_engine)

		# the fetcher tries to parse content from sites
		# and update given article objects (from watcher).
		log.info('Starting Fetcher')
		self.fetcher = Fetcher(
			sessionmaker=self.sessionmaker
			)
		# THREADS: 10 working queue

		# the watcher tracks all of the feeds in sources,
		# assembles preliminary article objects, and gives them
		# to passback (self.fetcher ^)
		log.info('Starting Watcher')
		self.watcher = Watcher(
			passback=self.fetcher.add,
			sessionmaker=self.sessionmaker,
			sources=self.sources,
			loop=True
			)
		# THREADS: 10 working queue

	def start( self ):
		log.info("Newsbin Engine Starting")
		#self.annotator.start()
		self.fetcher.start()
		self.watcher.start()

	def stop( self ):
		log.info("Newsbin Engine Stopping")
		#self.annotator.stop()
		self.fetcher.stop()
		self.watcher.stop()

def shutdown( signal, frame ):
	engine.stop()

if __name__=='__main__':
	if '-v' in sys.argv:
		verbose = True
	else:
		verbose = False


	log = logging.getLogger("newsbin.engine")
	log.setLevel(logging.DEBUG)

	# format messages for log
	_format = logging.Formatter('[%(asctime)s] %(levelname)s:  %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

	# create the file logging handler
	file_h = logging.FileHandler( os.path.join( settings.logdir, 'newsbin_engine.log' ) )
	file_h.setFormatter(_format)

	# create the console logging handler
	console_h = logging.StreamHandler()
	console_h.setFormatter(_format)

	# add handlers to log object
	log.addHandler(file_h)
	if verbose:
		log.addHandler(console_h)

	# register the shutdown signal
	signal.signal(signal.SIGINT, shutdown)

	engine = Engine()
	engine.start()
