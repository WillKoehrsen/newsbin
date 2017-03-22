from src.article import Article, Base
from src import filters
from src.logger import Logger

from sqlalchemy import create_engine
from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace

import os

class NewsAnno:
	def __init__( self, *args, **kwargs ):
		self.settings = kwargs['settings']
		self.sources = kwargs['sources']
		self.log = Logger.load(settings.log)

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			engine = create_engine('sqlite:///' + settings.database.replace('\\','\\\\'))
			Base.metadata.create_all(engine)

		self.init_watchers()

	def init_watchers( self ):
		for source in self.sources:
			site_filter = filters.lookup( source )
			if site_filter:
				print( 'site filter for \"' + source + '\"' )
			else:
				print( 'no filter for \"' + source + '\"' )

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
