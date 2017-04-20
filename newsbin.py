from flask import Flask, request, render_template

import regex
import atexit
import os

from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from package import filters
from package.models import Article, Annotation, Base
from package.newsbin import Engine

session = None
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

		# if the database specified by config doesn't exist, create it.
		if not os.path.isfile( settings.database ):
			Base.metadata.create_all(db_engine)

	if not engine:
		engine = Engine( database=settings.database, sessionmaker=Session )
		engine.start

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
	articles = [ a for a in articles if pattern.search(article.title) or pattern.search(article.content) ]
	all_checked = bool( sources in all_sources )

	return render_template('index.html', all_sources=all_sources, results=number,search=search, checked=sources, all_checked=all_checked, articles=articles)

@app.route('/article', methods=['GET'])
def article():
	pass
#	{% for article in articles %}
#		<div class="content" id={{article.id}}>
#			{{article.source|upper}}: {{ article.publish_date }}<br/>
#			<a href="{{article.url}}" target="_blank">original</a><br/>
#			{{ article.content|safe }}
#		</div>
#	{% endfor %}

@app.route('/annotation', methods=['GET'])
def annotation():
	pass


if __name__ == "__main__":
	app.run()