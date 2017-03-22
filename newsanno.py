from src.article import Article, Base
from src import filters
from src.logger import Logger
from src.watcher import Watcher

from sqlalchemy import create_engine
from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace

from datetime import datetime
import os, time

class NewsAnno:
	def __init__( self, *args, **kwargs ):
		self.settings = kwargs['settings']
		self.sources = kwargs['sources']
		self.log = Logger.load(settings.log)
		self.watchers = []

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			engine = create_engine(settings.database)
			Base.metadata.create_all(engine)

		self.log.notify('------- NewsAnno -------',echo=True)
		self.log.notify('date: ' + datetime.now().strftime('%d/%m/%Y %I:%M:%S') + '\n',echo=True)
		self.init_watchers()

	def init_watchers( self ):
		for source in self.sources:
			site_filter = filters.lookup( source )
			if site_filter:
				self.log.notify('creating watchers for: ' + source, echo=True)
				for feed in self.sources[source]:
					watcher = Watcher(feed=feed, filter=site_filter, database=self.settings.database, log=self.log)
					self.watchers.append( watcher )
			else:
				self.log.notify('no filter for: ' + source)
		self.log.notify( str(len(self.watchers)) + ' watchers created')

	def run( self ):
		self.log.notify('running . . .',echo=True)
		try:
			while True:
				for watcher in self.watchers:
					watcher.update()
					time.sleep(5)
		except KeyboardInterrupt:
			self.log.notify('shutting down',echo=True)

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

	newsanno = NewsAnno(settings=settings,sources=sources)
	newsanno.run()
