from flask import Flask, request, render_template, make_response, abort, redirect
from flask import session as user_data

import regex
import os
import json
import datetime
import logging

from sqlalchemy import literal

from package import filters, utilities
from package import models, session_scope
from package import politifact
from package import defaults

log = logging.getLogger('newsbin.site')
app = Flask(__name__)
app.secret_key = 'DEVELOPMENT'

@app.route('/', methods=['GET'])
@app.route('/<int:page>', methods=['GET'])
def index( page=0 ):
	options = request.values.to_dict()
	all_sources = defaults.default_sources()
	all_categories = defaults.default_categories()

	page_size = 40
	end = page*page_size + page_size

	with session_scope() as session:
		categories = [ c for c in options.get('categories','').split(',') if c ] or [ c[0] for c in all_categories ]
		sources = [ s for s in options.get('sources','').split(',') if s ] or [ s[0] for s in all_sources ]
		search = options.get('search','')


		# the base query is just a filter to make sure the sources are
		# what was requested and orders them by date. Note that we don't
		# care about the 'all' option- it's just a javascript hook to set
		# the other values in the search form.
		articles = session.query( models.Article )\
			.filter( models.Article.source.in_(sources) )\
			.filter( models.Article.category.in_(categories) )\
			.order_by( models.Article.fetched.desc() )

		# check for the search string in the title and content and then execute the query
		articles = articles.filter( models.Article.title.contains(search) | models.Article.content.contains(search))\
			.slice(0,end)\
			.all()

		data = {
			'page':0,
			'categories':categories,
			'sources':sources,
			'search':search,
		}
		user_data.clear()
		user_data['last_search'] = data

		for a in articles:
			a.category_label = defaults.category_label( a.category )

		short_page = True if len(articles) < page_size else False
		
		return render_template('index.html', articles=articles, sources=defaults.default_sources(), categories=defaults.default_categories(), short_page=short_page)


	# couldn't get a session for some reason
	return abort(404)

@app.route('/titles/<int:page>', methods=['GET'])
def titles( page ):
	page_size = 40
	start = page*page_size
	end = start + page_size
	all_sources = [ s[0] for s in defaults.default_sources() ]
	all_categories = [ c[0] for c in defaults.default_categories() ]
	options = user_data['last_search']

	with session_scope() as session:
		categories = options.get('categories') or all_categories
		sources = options.get('sources') or all_sources
		search = options.get('search','')

		articles = session.query( models.Article )\
			.filter( models.Article.source.in_(sources) )\
			.filter( models.Article.category.in_(categories) )\
			.order_by( models.Article.fetched.desc() )

		articles = articles.filter( models.Article.title.contains(search) | models.Article.content.contains(search))\
			.slice(start,end)\
			.all()

		for a in articles:
			a.category_label = defaults.category_label( a.category )

		data = [ a.serialize(exclude=('content')) for a in articles ]
		if data:
			return make_response( json.dumps(data) )

	return abort(404)

# ------------------------------------------------------------------------------
# ANNOTATIONS
# 	This view returns articles complete with the article
#	blacklist. If called as POST, this view is used to
#	submit new annotations for consideration.
@app.route('/article/<int:pk>', methods=['GET','POST'])
def article( pk ):
	if request.method == 'GET':
		with session_scope() as session:
			try:
				article = session.query( models.Article ).get( pk )
				if article.blacklist:
					blacklist = article.blacklist.replace(';',', ')
				else:
					blacklist = ''
				try:
					summary = regex.sub('<.*?>','',article.content[:160].replace('</cite>','</cite> '))
				except Exception as e:
					log.exception(e)
					summary = article.content[:100]
				return render_template('article.html', article=article, blacklist=blacklist, date=datetime.datetime.now(), summary=summary.strip())
			except Exception as e:
				log.exception(e)
				raise

	elif request.method == 'POST':
		name = request.form.get('annotation','').strip()
		add = 'add' in request.form
		if pk:
			try:
				with session_scope() as session:
					article = session.query( models.Article ).get( pk )

					if add and name:
						utilities.summarize(name)
						article.unblacklist_name( name )
					elif name:
						article.blacklist_name(name)

					return render_template('article.html', article=article, blacklist=article.blacklist.replace(';',', '), date=datetime.datetime.now())
			except Exception as e:
				log.exception(e)
		else:
			log.warning('pk missing from request: pk:{} name:{} add:{}'.format(pk,name,add))
			return abort(404)
	else:
		return abort(404)

# ------------------------------------------------------------------------------
# ANNOTATIONS
# 	These routes handle fetching info about annotations
#		1. annotate:		fetch annotations for article
#		2. annotations: 	get annotation data for modal
@app.route('/article/<int:pk>/annotate', methods=['GET'])
def annotate( pk ):
	try:
		with session_scope() as session:
			article = session.query( models.Article ).get( pk )
			annotations = session.query( models.Annotation ).filter( literal(article.content).contains(models.Annotation.name)).all()
			data = {
				'annotations':[ a.name for a in annotations if a.name not in article.get_blacklist() ],
				'blacklist':article.get_blacklist(),
			}
			return make_response( json.dumps(data) )
	except Exception as e:
		log.exception('at /article/<int:pk>/annotate: '.format(e))
		return abort(404)



@app.route('/annotations', methods=['GET'])
def annotations():
	name = request.values.get('name',None)
	with session_scope() as session:
		try:
			annotation = session.query( models.Annotation ).filter( models.Annotation.name==name ).first()
			slug = annotation.slug
			if not slug:
				rating, slug = politifact.get_rating(name=annotation.name)
				if slug: annotation.update(slug=slug)
			else:
				rating, slug = politifact.get_rating(name=annotation.name,slug=slug)
		except Exception as e:
			try:
				annotation = utilities.summarize(name)
				if annotation.name:
					rating, slug = politifact.get_rating(name=annotation.name)
					if slug: annotation.update(slug=slug)
			except Exception as e:
				log.exception(e)
				return abort(404)

		table_items = []
		if rating: table_items.append({'key':'Truth Score','value':str(rating)+'%','tooltip':'from last five statements rated by politifact.com'})

		data = annotation.serialize(data_table=table_items,slug=slug)
		return make_response(data)

@app.route('/about', methods=['GET'])
def about():
	return render_template('about.html', categories=defaults.default_categories(), date=datetime.datetime.now())

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
