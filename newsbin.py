from flask import Flask, request, render_template, make_response

import regex
import atexit
import os
import json

from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from package import filters, utilities
from package.models import Article, Annotation, Base
from package.newsbin import Engine

session = None
anno_session = None
settings = None
engine = None

app = Flask(__name__)

@atexit.register
def teardown():
	if engine:
		engine.stop()

@app.before_first_request
def setup( application=None ):
	global session
	global settings
	global engine

	if not settings:
		# create a config parser and find newsbin.conf
		config = ConfigParser(interpolation=ExtendedInterpolation())
		config.read('config/newsbin.conf')
		settings = SimpleNamespace(**config['settings'])

	if not session:
		db_engine = create_engine(settings.database)
		Session = sessionmaker(bind=db_engine)
		session = Session()
		anno_session = Session()

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			Base.metadata.create_all(db_engine)

	if not engine:
		pass
		#engine = Engine( database=settings.database, sessionmaker=Session )
		#engine.start()

@app.route('/', methods=['GET','POST'])
def index():
	all_sources = sorted(filters.all())
	sources = request.values.get( 'sources', filters.string() ).split('|')
	search = request.values.get( 'search', '' )
	sort_descending_date = request.values.get( 'sort_descending_date', True )
	number = int( request.values.get( 'results', 100 ) )

	if sort_descending_date:
		articles = session.query(Article).filter(Article.source.in_(sources)).order_by(Article.publish_date.desc()).limit(number).all()
	else:
		articles = session.query(Article).filter(Article.source.in_(sources)).order_by(Article.publish_date.asc()).limit(number).all()

	pattern = regex.compile( search )
	articles = [ a for a in articles if pattern.search(a.title) or pattern.search(a.content) ]
	all_checked = bool( sources in all_sources )

	return render_template('index.html', all_sources=all_sources, results=number,search=search, checked=sources, all_checked=all_checked, articles=articles)

@app.route('/articles', methods=['GET','POST'])
def articles():
	pk = request.values.get('id',None)
	people = request.values.get('people',None)
	if pk:
		article = session.query(Article).get( pk )
		if people==None:
			tmp = utilities.annotate( article )
			data = tmp.serialize()
			return make_response(data)
		else:
			article.set_people( people.split(';') )
			tmp = utilities.annotate( article )
			data = tmp.serialize()
			session.commit()
			return make_response(data)


@app.route('/annotations', methods=['GET','POST'])
def annotations():
	name = request.values.get('name',None)
	if name:
		try:
			annotation = session.query(Annotation).filter( Annotation.name==name ).first()
			return make_response(annotation.summary)
		except:
			try:
				annotation = utilities.summarize(name,session)
				print('added: ' + name)
				return make_response(annotation.summary)
			except Exception as e:
				return make_response('Annotation Not Found')

@app.route('/about', methods=['GET'])
def about():
	return render_template('about.html')

@app.route('/log', methods=['GET'])
def log():
	return render_template('about.html')



if __name__ == "__main__":
	app.run()
