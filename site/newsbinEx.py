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
def index(): return redirect('/articles/?count=40')

@app.route('/articles/', methods=['GET'])
def articles():
	# if this is a request for additional results, and we have
	# a saved search, then change the request context.
	_next, args = ('next' in request.values) and ('last' in user_data), {}
	if _next:
		args = json.loads( user_data['last'] )
	else:
		# conveniance assignment
		args = request.values.to_dict()

		# save the last request for additional requests
		user_data['last'] = json.dumps( args )


	# define variables
	sources 	= []							# news sources to pull from
	categories	= []							# categories to include
	search		= args.get('search','')			# search: in title or content
	page		= request.values.get('page')	# page range: 0 to 'page'
	page_size	= int(settings.page_size)		# size of pages to return
	_json		= args.get('format')			# boolean set json response

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

		return render_template( 'articles.html', articles=articles, sources=defaults.default_sources(), categories=defaults.default_categories() )

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
