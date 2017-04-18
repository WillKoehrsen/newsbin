from flask import Flask, request, render_template

from package import filters
from package.models import Article, Annotation
from package import utilities

import re
import atexit

session = None
settings = None

app = Flask(__name__)

@atexit.register
def teardown():
	pass
	#utilities.collector.stop()

@app.before_first_request
def setup( application=None ):
	global session
	global settings
	session = utilities.setup()
	settings = utilities.settings

@app.route('/', methods=['GET','POST'])
def index():
	all_sources = filters.all()
	sources = [ s for s in request.values if s in all_sources ]
	count = request.values.get('results','')
	search = request.values.get('search','')

	if not count:
		count = 100

	articles = []
	if sources:
		try:
			articles = session.query(Article).filter(Article.source.in_(sources)).order_by(Article.publish_date.desc()).limit(int(count)).all()
		except:
			articles = session.query(Article).filter(Article.source.in_(sources)).order_by(Article.publish_date.desc()).all()

	else:
		try:
			articles = session.query(Article).order_by(Article.publish_date.desc()).limit(int(count)).all()
		except:
			articles = session.query(Article).order_by(Article.publish_date.desc()).all()

	if search:
		pattern = re.compile(search)
		search_results = []
		for article in articles:
			if pattern.search(article.title) or pattern.search(article.content):
				search_results.append(article)
		articles = search_results

	tmp_articles = []
	for article in articles:
		annotated = utilities.annotate( article )
		annotated.content = '\n'.join([ '<p>{}</p>'.format(para) for para in annotated.content.split('\n\n') if para ])
		tmp_articles.append( annotated )
	articles = tmp_articles

	all_checked = False
	if not [ item for item in all_sources if item not in sources ]:
		all_checked = True

	all_sources = sorted(all_sources)
	return render_template('index.html', all_sources=all_sources, results=count,search=search, checked=sources, all_checked=all_checked, articles=articles)

@app.route('/summarize', methods=['GET','POST'])
def summarize():
	try:
		name = request.values['name']
		anno = session.query(Annotation).filter(Annotation.name==name).one()
		return anno.summary
	except:
		return '<span class=\"summary_error\">Couldn\'t find summary</span>'



	#try:
	#	return wikipedia.summary(name)
	#except wikipedia.exceptions.DisambiguationError as e:
	#		print(e.options)
	#		return ''

if __name__ == "__main__":
	app.run()
