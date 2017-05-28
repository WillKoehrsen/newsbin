from flask import Flask, request, render_template, make_response, abort

import regex
import os
import json

from package import filters, utilities
from package import models, session_scope
from package import log

app = Flask(__name__)

categories = [
	'Top',
	'US',
	'World',
	'Finance',
	'Politics',
	'Technology',
	'Health',
	'Entertainment',
	'Travel',
	'Life',
	'Opinion',
	'Economy',
	'Business',
	'Investing',
	'Education',
	'Sports',
	'Science'
]

@app.route('/', methods=['GET'])
def index():
	options = request.values.to_dict()
	sources = filters.all()

	if not 'count' in options: options['count'] = 100
	if 'all' in options or set(options.keys()).isdisjoint(sources):
		options.update({ key:'on' for key in sources })
		options['all'] = 'on'

	with session_scope() as session:
		category = options.get('category','all')
		if category == 'all':
			articles = session.query( models.Article ).filter( models.Article.source.in_(options)).order_by( models.Article.fetched.desc()).limit(int(options['count'])).all()
		else:
			articles = session.query( models.Article ).filter( models.Article.source.in_(options) ).filter( models.Article.category.contains(category) ).order_by( models.Article.fetched.desc()).limit(int(options['count'])).all()

		search = options.get('search','')
		if 'regex' in options:
			pattern = regex.compile( search )
			articles = [ a for a in articles if pattern.search(a.title) or pattern.search(a.content) ]
		else:
			options['plain'] = 'on'
			articles = [ a for a in articles if search in a.title or search in a.content ]

		return render_template('index.html', **options, articles=articles, categories=categories, selected=category)

	# couldn't get a session for some reason
	return abort(404)

@app.route('/article', methods=['GET','POST'])
def article():
	if request.method == 'GET':
		pk = request.args.get('id',None)
		with session_scope() as session:
			try:
				article = session.query( models.Article ).get( pk )
				article = utilities.annotate( article, session )
				return render_template('article.html', article=article)
			except Exception as e:
				log.exception(e)
				raise
	elif request.method == 'POST':
		pk = request.form.get('id',None)
		name = request.form.get('annotation',None)
		add = 'add' in request.form
		if pk and name:
			with session_scope() as session:
				article = session.query( models.Article ).get( pk )
				if add:
					try:
						utilities.summarize(name)
					except Exception as e:
						log.exception(e)
					article.unblacklist_name( name )
				else:
					article.blacklist_name(name)

				article = utilities.annotate( article, session )
				return render_template('article.html', article=article, blacklist=article.blacklist.replace(';',',') )
		else:
			log.warning('pk or name missing from request: pk:{} name:{} add:{}'.format(pk,name,add))
			return abort(404)
	else:
		return abort(501)

@app.route('/annotations', methods=['GET'])
def annotations():
	name = request.values.get('name',None)
	with session_scope() as session:
		try:
			annotation = session.query( models.Annotation ).filter( models.Annotation.name==name ).first()
			data = annotation.serialize()
			return make_response(data)
		except:
			try:
				annotation = utilities.summarize(name)
				if annotation.name:
					data = annotation.serialize()
					return make_response(data)
			except Exception as e:
				log.exception(e)
	return abort(404)

@app.route('/about', methods=['GET'])
def about():
	return render_template('about.html', categories=categories)


if __name__ == "__main__":
	app.run(host='0.0.0.0')
