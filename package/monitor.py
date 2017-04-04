from package.article import Base
from package import filters
from package.logger import Logger
from package.watcher import Watcher

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace

from datetime import datetime
import os

DEBUG = True

class Monitor:
	def __init__( self, *args, **kwargs ):
		self.settings = kwargs['settings']
		self.sessionmaker = kwargs['sessionmaker']
		self.sources = kwargs['sources']
		self.log = Logger.load(self.settings.log)
		self.watchers = []

		self.log.debug('------- Monitor -------',echo=DEBUG)
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
				self.log.debug('no filter for: ' + source,echo=DEBUG)
		self.log.debug( str(len(self.watchers)) + ' watchers created',echo=DEBUG)

	def run( self ):
		self.log.debug('running . . .',echo=DEBUG)
		try:
			while True:
				for watcher in self.watchers:
					watcher.update()
		except KeyboardInterrupt:
			self.log.notify('shutting down',echo=DEBUG)


if __name__=='__main__':
	# create a config parser and find newsanno.conf in local dir
	config = ConfigParser(interpolation=ExtendedInterpolation())
	config.read('config/newsbin.conf')

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

	newsanno = Monitor(settings=settings,sources=sources, sessionmaker=sessionmaker(bind=engine))
	newsanno.run()
