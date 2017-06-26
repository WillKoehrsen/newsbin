import threading
import requests
import time
import os
import feedparser
import logging
import signal
import sys

from datetime import timedelta, datetime
from pprint import PrettyPrinter
from sqlalchemy.exc import IntegrityError

# ------------------------------------------------------------------------------
# LOCALS
from package import defaults
from package import filters
from package import models

from package import session_scope
from package import db_engine
from package import settings

# ------------------------------------------------------------------------------
# GLOBALS
log = logging.getLogger('newsbin.engine')
engine = None

# '/etc/update-motd.d/engine_report.txt'
# '/home/mhouse/Projects/python/newsbin/engine/engine_status'

# ------------------------------------------------------------------------------
# HOUSEKEEPING
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------------------------------------------------------------------

class NewsbinEngine:

	def __init__( self, *args, **kwargs ):
		self.sources = kwargs['sources']
		self.settings = kwargs['settings']
		self.dbengine = kwargs['engine']

		# Bloom filter
		#	at some point, I would like to replace the visited list
		#	with something more scalable, probably a bloom filter.
		self.visited = []

		self.thread=None
		self.stop_event=threading.Event()

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( self.settings.database ):
			models.Base.metadata.create_all(self.dbengine)

	def start( self ):
		log.info("Newsbin Engine Starting")

		with session_scope() as session:
			titles = [ a.title for a in session.query( models.Article ).all() ]
			log.info("Loading {} stored article titles".format(len(titles)))
			self.visited = titles

		self.thread = threading.Thread(target=self.__run)
		self.thread.start()

	def stop( self ):
		log.info("Newsbin Engine Stopping")
		self.stop_event.set()
		self.thread.join()

	def __crawl_article( self, item, meta ):
		sfilter, source, category = meta
		if item['title'] not in self.visited:
			try:
				# the title hasn't been fetched before, so try to add
				# it to the database
				with session_scope() as session:
					# set initial values based off the rss item
					article = models.Article( title=item['title'], link=item['link'], filter=sfilter, source=source, category=category )

					# fetch and filter the article, and then update
					# with additional information (content, for one)
					response = requests.get( article.link, verify=False )
					content = article.filter.process( response.text )
					article.update( **content )

					# if there is a title and some sort of content,
					# try to add it to the database
					if article.content.strip() and article.title.strip():
						session.add( article )

			except IntegrityError as e:
				pass

			except Exception as e:
				log.exception('{} exception in __crawl_article'.format(type(e)))

			finally:
				self.visited.append(item['title'])

	def __crawl_feed( self, item ):
		source, feed, categories = item

		try:
			sfilter = filters.lookup( source )
			rss = feedparser.parse(feed)
			for item in rss['items']:

				# if stop_event isn't set crawl the article,
				# otherwise, return.
				if not self.stop_event.is_set():
					self.__crawl_article( item, (sfilter,source,categories) )
				else:
					return

		except Exception as e:
			log.exception('{} exception in __crawl_feed'.format(type(e)))

		finally:
			pass

	def __run( self ):
		while True:
			for item in self.sources:

				# if stop_event isn't set crawl the feed,
				# otherwise, exit.
				if not self.stop_event.is_set():
					self.__crawl_feed( item )
				else:
					return

def shutdown( signal, frame ):
	engine.stop()

if __name__=='__main__':
	# register the shutdown signal
	signal.signal(signal.SIGINT, shutdown)

	engine = NewsbinEngine(sources=defaults.sources, settings=settings, engine=db_engine )
	engine.start()
