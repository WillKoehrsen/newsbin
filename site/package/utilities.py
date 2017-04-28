import os
import sys
import regex
import copy

import wikipedia
from wikipedia.exceptions import PageError

from shared.models import Annotation

def collapse( names ):
	names = sorted( set(names), key=len, reverse=True)
	collapsed = {}
	for idx,name in enumerate(names):
		subnames = [ rem for rem in names[idx+1:] if name.endswith( rem ) ]
		collapsed[name] = list(subnames)
	values = [ item for sublist in collapsed.values() for item in sublist ]
	return [ (key,(value,)) for key,value in collapsed.items() if key not in values ]

def multi_replace( content, lookups ):
	annotate = regex.compile('|'.join(regex.escape(key) for key in lookups.keys()),flags=regex.IGNORECASE)
	content = regex.sub(annotate,lambda m: lookups[m.string[m.start():m.end()].lower()], content)
	return content

def annotate( article):
	article = copy.deepcopy(article)
	content = article.content
	names = sorted( set( article.get_people() ), key=lambda x: len(x), reverse=True )
	replacements = { name.lower():'<x-annotate onclick="show_summary(this);" name="{0}">{0}</x-annotate>'.format(name) for name in names }
	content = multi_replace( content, replacements )
	article.content = ''.join([ '<p>{}</p>\n'.format(p) for p in content.split('\n\n') if p ])
	return article

def summarize( name, session ):
	summary = wikipedia.summary(name)
	if summary:
		annotation = Annotation(name=name,summary=summary)
		try:
			session.add( annotation )
			session.commit()
		except:
			session.rollback()
		return annotation
	else:
		raise PageError('no summary found')
