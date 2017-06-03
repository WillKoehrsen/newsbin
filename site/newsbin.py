from flask import Flask, request, render_template, make_response, abort

import regex
import os
import json
import datetime

from package import filters, utilities
from package import models, session_scope
from package import log
from package import politifact

app = Flask(__name__)

# these are the categories that appear in the search
# menu on the index/about pages. They need to be automatically
# generated from the engine/package/defaults.py feed tags, but
# I haven't done it yet.
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

	if not options.get('count',False): options['count'] = 100
	if 'all' in options or set(options.keys()).isdisjoint(sources):
		options.update({ key:'on' for key in sources })
		options['all'] = 'on'

	with session_scope() as session:
		category = options.get('category','all')
		if category == 'all':
			articles = session.query( models.Article ).filter( models.Article.source.in_(options) ).order_by( models.Article.fetched.desc() ).all()
		else:
			articles = session.query( models.Article ).filter( models.Article.source.in_(options) ).filter( models.Article.category.contains(category) ).order_by( models.Article.fetched.desc() ).all()

		search = options.get('search','')
		if search.startswith('re:'):
			search = search.split(':',1)[1]
			pattern = regex.compile( search )
			articles = [ a for a in articles if pattern.search(a.title) or pattern.search(a.content) ]
		else:
			articles = [ a for a in articles if search in a.title or search in a.content ]

		return render_template('index.html', articles=articles[:int(options['count'])], categories=categories, date=datetime.datetime.now())


	# couldn't get a session for some reason
	return abort(404)

@app.route('/article/<int:pk>', methods=['GET','POST'])
def article( pk ):
	if request.method == 'GET':
		with session_scope() as session:
			try:
				article = session.query( models.Article ).get( pk )
				article = utilities.annotate( article, session )
				if article.blacklist:
					blacklist = article.blacklist.replace(';',',')
				else:
					blacklist = ''
				return render_template('article.html', article=article, blacklist=blacklist, date=datetime.datetime.now())
			except Exception as e:
				log.exception(e)
				raise
	elif request.method == 'POST':
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
				return render_template('article.html', article=article, blacklist=article.blacklist.replace(';',','), date=datetime.datetime.now())
		else:
			log.warning('pk or name missing from request: pk:{} name:{} add:{}'.format(pk,name,add))
			return abort(404)
	else:
		return abort(404)

@app.route('/annotations', methods=['GET'])
def annotations():
	name = request.values.get('name',None)
	with session_scope() as session:
		try:
			annotation = session.query( models.Annotation ).filter( models.Annotation.name==name ).first()
			rating, slug = politifact.get_rating(annotation.name)
			data = annotation.serialize(truth_score=rating,slug=slug)
			return make_response(data)
		except Exception as e:
			try:
				annotation = utilities.summarize(name)
				if annotation.name:
					rating, slug = politifact.get_rating(annotation.name)
					data = annotation.serialize(truth_score=rating,slug=slug)
					print(data)
					return make_response(data)
			except Exception as e:
				log.exception(e)
	return abort(404)

@app.route('/about', methods=['GET'])
def about():
	return render_template('about.html', categories=categories, date=datetime.datetime.now())

# ------------------------------------------------------------------------------
# Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', e=e), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html', e=e), 500

if __name__ == "__main__":
	app.run(host='0.0.0.0')
