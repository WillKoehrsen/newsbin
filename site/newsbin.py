from flask import Flask, request, render_template, make_response, abort

import regex
import os
import json

from package import filters, utilities
from package import models, session

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
	all_sources = sorted(filters.all())
	search = request.values.get( 'search', '' )
	use_regex = request.values.get( 'regex', False )
	sort_descending_date = request.values.get( 'sort_descending_date', True )
	sources = { key:value for key,value in request.values.items() if key in all_sources }
	if not sources:
		sources = { key:'' for key in all_sources }

	results = request.values.get( 'results', 100 )
	if not results:
		number = 100
	else:
		number = int(results)

	if sort_descending_date:
		articles = session.query( models.Article ).filter( models.Article.source.in_(sources)).order_by( models.Article.publish_date.desc()).limit(number).all()
	else:
		articles = session.query( models.Article ).filter( models.Article.source.in_(sources)).order_by( models.Article.publish_date.asc()).limit(number).all()

	if use_regex:
		pattern = regex.compile( search )
		articles = [ a for a in articles if pattern.search(a.title) or pattern.search(a.content) ]
	else:
		articles = [ a for a in articles if search in a.title or search in a.content ]

	requested_all = sorted(list(sources.keys())) == sorted(all_sources)

	return render_template('index.html', all_sources=all_sources, requested_all=requested_all, results=number, search=search, sources=sources, articles=articles, regex=use_regex)

@app.route('/articles', methods=['GET'])
def articles():
	pk = request.values.get('id',None)
	if pk:
		article = session.query( models.Article ).get( pk )
		tmp = utilities.annotate( article )
		data = tmp.serialize()
		return make_response(data)
	else:
		print('ARTICLES: NO PK')

@app.route('/refresh', methods=['POST'])
def refresh():
	try:
		pk = request.values.get('pk')
		people = request.values.get('people')

		article = session.query( models.Article ).get( pk )
		article.set_people( people.split(';') )
		tmp = utilities.annotate( article )
		data = tmp.serialize()
		session.commit()
		return make_response(data)
	except:
		return abort(404)

@app.route('/annotations', methods=['GET','POST'])
def annotations():
	name = request.values.get('name',None)
	if name:
		try:
			annotation = session.query( models.Annotation ).filter( models.Annotation.name==name ).first()
			data = annotation.serialize()
			return make_response(data)
		except:
			try:
				annotation = utilities.summarize(name,session)
				if annotation.name:
					data = annotation.serialize()
					return make_response(data)
			except Exception as e:
				pass
	return abort(404)

@app.route('/about', methods=['GET'])
def about():
	return render_template('about.html')

@app.route('/log', methods=['GET'])
def log():
	return render_template('about.html')



if __name__ == "__main__":
	app.run()
