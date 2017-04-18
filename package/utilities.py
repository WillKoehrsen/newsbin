from package.models import Base, Engine, Annotation

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace

import threading, os, spacy, regex, requests, json, regex
from difflib import SequenceMatcher
import unicodedata
import wikipedia

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
		collector = Engine(sources=sources,sessionmaker=Session)
		collector.start()
	else:
		print('	collector exists')

	return Session()

def collapse( names ):
	names = sorted( set(names), key=len, reverse=True)
	collapsed = {}
	for idx,name in enumerate(names):
		subnames = [ rem for rem in names[idx+1:] if name.endswith( rem ) ]
		collapsed[name] = list(subnames)
	values = [ item for sublist in collapsed.values() for item in sublist ]
	return [ (key,(value,)) for key,value in collapsed.items() if key not in values ]

def annotate( article ):
	if not hasattr(annotate,'session'):
		annotate.session = Session()

	content = article.content
	names = article.get_people()
	annotations = sorted(collapse(names), key=lambda x: len(x[0]), reverse=True)

	for item in annotations:
		name = item[0]
		targets = [ *item[1], name ]

		anno_exists = annotate.session.query(exists().where(Annotation.name == name)).scalar()
		if anno_exists:
			regstr = '|'.join( '(?<!\<x\-annotate.{{6,{0}}})({2})(?!.{{0,{1}}}\<\/x\-annotate\>)'.format(9+len(name),2+len(t),regex.escape(t).strip('\\')) for t in targets if t)
			try:
				matcher = regex.compile( regstr, flags=regex.IGNORECASE)
				content = regex.sub(matcher,'<x-annotate name=\"{}\">\g<0></x-annotate>'.format(name),content)
			except:
				print(regstr)

	article.content = content
	return article
