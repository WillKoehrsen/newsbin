from flask import Flask, request, render_template

from package import filters
from package.article import Article
from package import utilities

import re

session = None
settings = None

app = Flask(__name__)

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

	all_checked = False
	if not [ item for item in all_sources if item not in sources ]:
		all_checked = True

	all_sources = sorted(all_sources)
	return render_template('index.html', all_sources=all_sources, results=count,search=search, checked=sources, all_checked=all_checked, articles=articles)

if __name__ == "__main__":
	app.run()
