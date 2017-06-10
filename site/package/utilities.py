import os
import sys
import regex
import copy

from sqlalchemy import literal
import requests

import wikipedia
from wikipedia.exceptions import PageError

from shared.models import Annotation, Article
from . import session_scope

def politifact_exists( name ):
	pass

def politifact_rating( name ):
	pass

def collapse( names ):
	names = sorted( set(names), key=len, reverse=True)
	collapsed = {}
	for idx,name in enumerate(names):
		subnames = [ rem for rem in names[idx+1:] if name.endswith( rem ) ]
		collapsed[name] = list(subnames)
	values = [ item for sublist in collapsed.values() for item in sublist ]
	return [ (key,(value,)) for key,value in collapsed.items() if key not in values ]

def get_thumbnail( title ):
	try:
		response = requests.get( 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&pithumbsize=400&titles={}'.format(title) )
		pages = response.json()['query']['pages']
		if len(pages) > 1: raise ValueError('too many results')

		for key,data in pages.items():
			return data['thumbnail']['source']
	except Exception as e:
		return ''

def multi_replace( content, lookups ):
	annotate = regex.compile('|'.join(regex.escape(key) for key in lookups.keys()))
	content = regex.sub(annotate,lambda m: lookups[m.string[m.start():m.end()]], content)
	return content

def annotate( article, session ):
	names = [ anno.name for anno in session.query( Annotation ).filter( literal(article.content).contains(Annotation.name) ).all() if anno.name not in article.get_blacklist() ]

	if names:
		article = copy.deepcopy(article)
		content = article.content

		replacements = { name:'<span class="annotation" name="{0}">{0}</span>'.format(name) for name in names }
		content = multi_replace( content, replacements )
		article.content = content

	article.content = ''.join([ '<p>{}</p>\n'.format(p) for p in article.content.split('\n\n') if p ])
	return article

def summarize( name ):
	summary = wikipedia.summary(name)
	if summary:
		summary = '\n\n'.join([ p for p in summary.split('\n') if p ])
		image_url = get_thumbnail( name )
		annotation = Annotation(name=name,summary=summary,image=image_url)
		with session_scope() as session:
			try:
				session.add( annotation )
				session.commit()
			except:
				session.rollback()
		return annotation
