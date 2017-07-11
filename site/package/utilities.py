import regex
import copy

from sqlalchemy import literal

from package.models import Annotation

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
