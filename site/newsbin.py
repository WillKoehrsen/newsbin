from flask import Flask, request, render_template, make_response, abort

import regex
import os
import json

from package import filters, utilities
from package import models, session_scope
from package import log

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
	all_sources = filters.all()
	number = request.values.get( 'results', 100 ) or 100
	search = request.values.get( 'search', '' )
	use_regex = request.values.get( 'regex', False )
	sources = [ item for item in request.values if item in all_sources ]
	if not sources: sources = all_sources

	with session_scope() as session:
		articles = session.query( models.Article ).filter( models.Article.source.in_(sources)).order_by( models.Article.publish_date.desc()).limit(number).all()

		if use_regex:
			pattern = regex.compile( search )
			articles = [ a for a in articles if pattern.search(a.title) or pattern.search(a.content) ]
		else:
			articles = [ a for a in articles if search in a.title or search in a.content ]

		requested_all = sorted(sources)==sorted(all_sources)
		return render_template('index.html', all_sources=all_sources, requested_all=requested_all, results=number, search=search, sources=sources, articles=articles, regex=use_regex)

@app.route('/article', methods=['GET','POST'])
def article():
	if request.method == 'GET':
		pk = request.args.get('id',None)
		with session_scope() as session:
			article = session.query( models.Article ).get( pk )
			article = utilities.annotate( article, session )
			return render_template('article.html', article=article)
	elif request.method == 'POST':
		pk = request.form.get('id',None)
		name = request.form.get('annotation',None)
		action = request.form.get('action',None)
		if pk and name and action:
			with session_scope() as session:
				article = session.query( models.Article ).get( pk )
				if action=='add':
					try:
						utilities.summarize(name)
					except Exception as e:
						log.exception(e)
					article.unblacklist_name( name )
				elif action=='remove':
					article.blacklist_name(name)

				article = utilities.annotate( article, session )
				return render_template('article.html', article=article, blacklist=article.get_blacklist() )
		else:
			log.warning('pk, name or action missing from request: pk:{} name:{} action:{}'.format(pk,name,action))
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
	return render_template('about.html')


if __name__ == "__main__":
	app.run(host='0.0.0.0')
