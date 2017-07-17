from flask import Flask, request, render_template, make_response, abort, redirect
from flask import session as user_data
from flask import jsonify

import regex
import os
import json
import datetime
import logging
import jinja2

from sqlalchemy import literal, exists

from package import filters, utilities
from package import models, session_scope
from package import politifact
from package import wikimedia
from package import defaults
from package import settings

# global variables
log	 = logging.getLogger('newsbin.site')

# init the app
app = Flask(__name__)

# custom loader so we can inline css
loader = jinja2.ChoiceLoader([
	app.jinja_loader,
	jinja2.FileSystemLoader('static/css/'),
])

app.jinja_loader = loader
app.secret_key = 'DEVELOPMENT'

# index is a stub that funnels people
# to the listing endpoint.
@app.route('/', methods=['GET'])
def index(): return redirect('/articles/?page=0')

# ------------------------------------------------------------------------------
# ARTICLES
#	This endpoint handles requests that need lists of articles in html
#	or json format, and single pages of results in response to async
#	requests (infinite scroll)
@app.route('/articles/', methods=['GET'])
def articles():
	# if this is a request for additional results, and we have
	# a saved search, then change the request context.
	_next, args = ('next' in request.values) and ('last' in user_data), {}
	if _next:
		args = json.loads( user_data['last'] )
	else:
		# convenience assignment
		args = request.values.to_dict()

		# save the last request for additional requests
		user_data['last'] = json.dumps( args )


	# define variables
	sources 	= []								# news sources to pull from
	categories	= []								# categories to include
	search		= args.get('search','')				# search: in title or content
	page		= request.values.get('page')		# page range: 0 to 'page'
	page_size	= int(settings.page_size)			# size of pages to return
	_json		= (args.get('format') == 'json')	# boolean set json response

	# convert page number to int
	try:	page = int(page)
	except: page = 0

	# get the number of rows to fetch
	start = (page*page_size) if _next else 0
	end	  = (page*page_size) + page_size

	# this function parses arguments of the form:
	# 		ARG=value1|value2|value3
	def parse_piped_argument( _dict, _name, _fallback ):
		result = []
		# get requested values or, if no values
		# were given, use fallback.
		if _name in _dict:
			# try to get provided values
			for val in _dict.get(_name,'').split('|'):
				if val and val in _fallback:
					result.append(val)

		# use '_fallback' if result is empty
		return result or _fallback

	# parse sources/categories from request arguments
	sources		= parse_piped_argument( args, 'sources', defaults._sources() )
	categories	= parse_piped_argument( args, 'categories', defaults._categories() )

	# build and execute the database query
	with session_scope() as session:
		articles = session.query( models.Article )\
					.filter( models.Article.source.in_(sources) )\
					.filter( models.Article.category.in_(categories) )\
					.order_by( models.Article.fetched.desc() )

		# check for the search string in the title and content
		articles = articles.filter( models.Article.title.contains(search) | models.Article.content.contains(search))\
					.slice(start,end)\
					.all()

		# if they explicitly request json, or we're responding to
		# a _next request, then return json.
		if _json or _next:
			data = [ a.serialize() for a in articles ]
			return jsonify( data )

		# if we've gotten here, then we should have articles and the request didn't call for a json response
		return render_template( 'articles.html', articles=articles, sources=defaults.default_sources(), categories=defaults.default_categories() )

	abort(404)

# ------------------------------------------------------------------------------
# ARTICLES/<ID>		(GET)
#	This view returns a single article in html or json format
@app.route('/articles/<int:_id>/', methods=['GET','POST'])
def article( _id ):
	args	= request.values.to_dict()			# convenience assignment
	_json	= (args.get('format') == 'json')	# boolean set json response
	add		= ( 'add' in args )					# boolean add switch
	phrase	= args.get('annotation','').strip()	# the annotation to add/remove

	try:
		# try to fetch the article with pk '_id'
		with session_scope() as session:
			article = session.query( models.Article ).get( _id )
			if request.method == 'POST':
				existing = session.query( models.Annotation.id ).filter_by(name=phrase).scalar() is not None

				# if the annotation doesn't exist, try to create it
				if not existing:
					annotation = wikimedia.summarize( phrase )

					if annotation:									# if the annotation was created:
						session.add(annotation)						# 	add it to the session
						existing = True

				if existing:
					if add:	article.unblacklist_name( phrase )		# exists + add = unblacklist
					else: article.blacklist_name( phrase )			# exists + removing = blacklist it

			if _json:
				# if they request json, return article as json
				return jsonify( article.serialize() )

			# try to build a display-ready list of blacklisted terms
			try:	blacklist = ', '.join(article.get_blacklist())
			except:	blacklist = ''

			# try to get a plain-text meta-description (for google)
			try:	intro = article.get_intro()
			except:	intro = article.content[:100]

			# return the article as html
			return render_template( 'article.html', article=article, blacklist=blacklist, date=datetime.datetime.now(), intro=intro )

	except Exception as e:
		# couldn't fetch, so log the error and
		# fall through to a 404 page
		log.exception(e)

	abort(404)

# ------------------------------------------------------------------------------
# ARTICLES/<ID>/ANNOTATIONS
#	Returns annotations in json for a given article
@app.route('/articles/<int:_id>/annotations/', methods=['GET'])
def article_annotations( _id ):
	try:
		with session_scope() as session:
			# get the article, and fetch annotations whose names
			# are in the text of the article
			article		= session.query( models.Article ).get( _id )
			annotations = session.query( models.Annotation )\
							.filter( literal(article.content)\
							.contains(models.Annotation.name))\
							.all()

			# get the article blacklist
			blacklist = article.get_blacklist()

			# filter the results based on the blacklist
			results = [ a.serialize() for a in annotations if a.name not in blacklist ]

			# return json
			return jsonify( results )

	except Exception as e:
		# failed to annotate the article, so log
		# and fall through to the 404 page
		log.exception(e)

	abort(404)

# ------------------------------------------------------------------------------
# ANNOTATIONS
#	Returns annotations (in json) by the page and
#	in alphabetical order.
@app.route('/annotations/', methods=['GET'])
def annotations_all():
	args 		= request.values.to_dict()	# convenience assignment
	page 		= args.get('page')			# page of annotations to fetch
	page_size	= int(settings.page_size)	# size of pages to return

	# convert page to 'int' or '0'
	try:	page = int(page)
	except: page = 0

	# calculate starting and ending indexes
	start = (page*page_size)
	end	  = (page*page_size) + page_size

	try:
		with session_scope() as session:
			# get annotations sorted alphabetically by name,
			# and slice to get requested page.
			annotations = session.query( models.Annotation )\
							.order_by( models.Annotation.name )\
							.slice( start, end )\
							.all()

			# serialize to json and return results
			results = [ a.serialize() for a in annotations ]
			return jsonify( results )
	except Exception as e:
		# failed to fetch annotations, so log
		# and fall through to a 404 response
		log.exception(e)

	abort(404)

# ------------------------------------------------------------------------------
# ANNOTATION
#	Returns json for a single annotation
@app.route('/annotations/<int:_id>/', methods=['GET'])
def annotations_one( _id ):
	try:

		with session_scope() as session:
			annotation = session.query( models.Annotation ).get( _id )	# get annotation by id
			return jsonify( annotation.serialize() )					# serialize to json and return

	except Exception as e:
		# failed to fetch annotation, so log
		# and fall through to a 404 response
		log.exception(e)

	abort(404)


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
