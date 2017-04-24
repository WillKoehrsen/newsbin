import sys, os
sys.path.insert(1, os.path.dirname(os.path.abspath(sys.argv[0])))

from package.models import Annotation

from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError

import regex

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

from copy import deepcopy

def collapse( names ):
	names = sorted( set(names), key=len, reverse=True)
	collapsed = {}
	for idx,name in enumerate(names):
		subnames = [ rem for rem in names[idx+1:] if name.endswith( rem ) ]
		collapsed[name] = list(subnames)
	values = [ item for sublist in collapsed.values() for item in sublist ]
	return [ (key,(value,)) for key,value in collapsed.items() if key not in values ]

def validate( people, session ):
	validated = []
	for name in people:
		try:
			summary = wikipedia.summary(name)
			if summary:
				annotation = Annotation(name=name,summary=summary)
				validated.append( name )
				try:
					session.add(annotation)
					session.commit()
				except:
					session.rollback()
					raise
		except (DisambiguationError, IntegrityError, PageError) as e:
			pass
	return validated

def annotate( article):
	article = deepcopy(article)

	content = article.content
	names = article.get_people()
	annotations = sorted(set(names), key=lambda x: len(x), reverse=True)

	for name in annotations:
		if name:
			targets = [ t for t in annotations if name.endswith(t) ]
			regstr = '|'.join( '(?<!\<x\-annotate.{{6,{0}}})({2})(?!.{{0,{1}}}\<\/x\-annotate\>)'.format(9+len(name),2+len(t),regex.escape(t).strip('\\')) for t in targets if t)
			try:
				matcher = regex.compile( regstr, flags=regex.IGNORECASE)
				content = regex.sub(matcher,'<x-annotate name=\"{}\">\g<0></x-annotate>'.format(name),content)
			except:
				pass

	article.content = ''.join([ '<p>{}</p>\n'.format(p) for p in content.split('\n\n') if p ])
	return article
