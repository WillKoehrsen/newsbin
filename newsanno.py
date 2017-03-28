from engine.article import Article, Base
from engine import filters
from engine.logger import Logger
from engine.watcher import Watcher

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace
import threading

from datetime import datetime
import os, time

DEBUG = False

class NewsAnno:
	def __init__( self, *args, **kwargs ):
		self.settings = kwargs['settings']
		self.sessionmaker = kwargs['sessionmaker']
		self.sources = kwargs['sources']
		self.log = Logger.load(self.settings.log)
		self.watchers = []

		self.log.debug('------- NewsAnno -------',echo=DEBUG)
		self.log.debug('date: ' + datetime.now().strftime('%d/%m/%Y %I:%M:%S') + '\n',echo=DEBUG)
		self.init_watchers()

	def init_watchers( self ):
		for source in self.sources:
			site_filter = filters.lookup( source )
			if site_filter:
				self.log.debug('creating watchers for: ' + source,echo=DEBUG)
				for feed in self.sources[source]:
					session = self.sessionmaker()
					watcher = Watcher(feed=feed, filter=site_filter, database=session, log=self.log)
					watcher.debug = DEBUG
					self.watchers.append( watcher )
			else:
				self.log.debug('no filter for: ' + source)
		self.log.debug( str(len(self.watchers)) + ' watchers created')

	def run( self ):
		self.log.debug('running . . .',echo=DEBUG)
		try:
			while True:
				for watcher in self.watchers:
					watcher.update()
					time.sleep(5)
		except KeyboardInterrupt:
			self.log.notify('shutting down',echo=DEBUG)

if __name__=='__main__':
	# create a config parser and find newsanno.conf in local dir
	config = ConfigParser(interpolation=ExtendedInterpolation())
	config.read('newsanno.conf')

	# unwrap settings into a namespace for ease of use
	settings = SimpleNamespace(**config['settings'])

	# build sources dict to scrape for articles
	sources = {}
	for source in ( item for item in config['sources'] if item not in config.defaults() ):
		sources[source] = [ item.strip() for item in config['sources'][source].split(',') if item ]

	# get a database engine
	engine = create_engine(settings.database)

	# if the database specified by config doesn't exist, create it.
	if not os.path.isfile( settings.database ):
		Base.metadata.create_all(engine)

	DEBUG = True

	newsanno = NewsAnno(settings=settings,sources=sources, sessionmaker=sessionmaker(bind=engine))
	newsanno.run()
