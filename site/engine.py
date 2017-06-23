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
pp = PrettyPrinter(indent=4)
log = logging.getLogger('newsbin.engine')
engine = None

# '/etc/update-motd.d/engine_report.txt'
# '/home/mhouse/Projects/python/newsbin/engine/engine_status'

# ------------------------------------------------------------------------------
# HOUSEKEEPING
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ------------------------------------------------------------------------------

class NewsbinReport:
	def __init__( self, *args, **kwargs ):
		self.files = kwargs.get('files',[])
		self.data = {
			'start time':datetime.now(),
			'end time':None,
			'articles visited':0,
		}

	def visited( self, count=1 ):
		self.data['articles visited'] += count

	def write_out( self, count=1 ):
		pass

class NewsbinEngine:

	def __init__( self, *args, **kwargs ):
		self.sources = kwargs['sources']
		self.settings = kwargs['settings']
		self.dbengine = kwargs['engine']

		# Bloom filter
		#	at some point, I would like to replace the visited list
		#	with something more scalable, probably a bloom filter.

		self.analytics = {
			'started':time.time(),						# start time
			'passes':0,									# times we've crawled all feeds
			'feeds':{ f[1]:0 for f in self.sources},	# times we've crawled each feed
			'initial':0,								# titles in db already
			'visited':[],								# titles we've already fetched
		}

		self.thread=None
		self.stop_event=threading.Event()

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( self.settings.database ):
			models.Base.metadata.create_all(self.dbengine)

	def status( self ):
		started = self.analytics.pop('started')
		elapsed = time.time()-started
		log.info("{:<10} {:<10}".format("Started:",datetime.fromtimestamp(started).strftime('%Y-%m-%d %H:%M:%S')))
		log.info("{:<10} {:<10}".format("Elapsed:",str(timedelta(seconds=elapsed))))
		log.info("{:<10} {:<10}".format("Visited:",str(len(self.analytics['visited'])-self.analytics['initial']) + ' article(s)'))
		log.info("{:<10} {:<10}".format("Loops:",str(self.analytics['passes']) + ' time(s)'))

	def start( self ):
		log.info("Newsbin Engine Starting")

		with session_scope() as session:
			titles = [ a.title for a in session.query( models.Article ).all() ]
			log.info("Loading {} stored article titles".format(len(titles)))
			self.analytics['visited'] = titles
			self.analytics['initial'] = len(titles)

		self.thread = threading.Thread(target=self.__run)
		self.thread.start()

	def stop( self ):
		log.info("Newsbin Engine Stopping")
		self.stop_event.set()
		self.thread.join()

		# log closing information
		self.status()
		#pp.pprint(self.analytics)

	def __crawl_article( self, item, meta ):
		sfilter, source, category = meta
		status = 0
		if item['title'] not in self.analytics['visited']:
			try:

				with session_scope() as session:
					article = models.Article( title=item['title'], link=item['link'], filter=sfilter, source=source, category=category )

					response = requests.get( article.link, verify=False )
					content = article.filter.process( response.text )
					article.update( **content )

					if article.content.strip() and article.title.strip():
						session.add( article )

			except IntegrityError as e:
				pass

			except Exception as e:
				log.exception('{} exception in __crawl_article'.format(type(e)))
				status = 0

			else:
				status = 1

			finally:
				self.analytics['visited'].append(item['title'])

		return status

	def __crawl_feed( self, item ):
		source, feed, categories = item

		try:
			sfilter = filters.lookup( source )
			rss = feedparser.parse(feed)
			count = 0
			for item in rss['items']:

				# if stop_event isn't set crawl the article,
				# otherwise, return.
				if not self.stop_event.is_set():
					count += self.__crawl_article( item, (sfilter,source,categories) )
				else:
					return

		except Exception as e:
			log.exception('{} exception in __crawl_feed'.format(type(e)))

		finally:
			log.info("{}: {}".format(feed[-40:],count))
			self.analytics['feeds'][feed] += count

	def __run( self ):
		while True:
			self.analytics['passes'] += 1;
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
