from package.article import Base
from package.monitor import Monitor

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace



import threading, os
from package import annotation

collector = None
Session = None
config = None
settings = None

def setup():
	global collector
	global Session
	global config
	global settings
	print('setup:')

	if not config:
		print('	config created')
		# create a config parser and find newsanno.conf in local dir
		config = ConfigParser(interpolation=ExtendedInterpolation())
		config.read('config/newsbin.conf')

		# unwrap settings into a namespace for ease of use
		settings = SimpleNamespace(**config['settings'])

		# build sources dict to scrape for articles
		sources = {}
		for source in ( item for item in config['sources'] if item not in config.defaults() ):
			sources[source] = [ item.strip() for item in config['sources'][source].split(',') if item ]
	else:
		print('	config exists')

	if not Session:
		print('	session created')
		# get the engine
		db_engine = create_engine(settings.database)

		# get the sessionmaker
		Session = sessionmaker(bind=db_engine)

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			Base.metadata.create_all(db_engine)
	else:
		print('	session exists')

	if not collector:
		print('	collector created')
		# launch news anno
		newsanno = Monitor(settings=settings,sources=sources,sessionmaker=Session)

		collector = threading.Thread(target=newsanno.run)
		collector.daemon = True
		collector.start()
	else:
		print('	collector exists')

	return Session()
