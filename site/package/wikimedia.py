import requests
import wikipedia
import datetime
import time
import string

from package import politifact
from package import models
from package import database


API_URL = 'http://en.wikipedia.org/w/api.php'
RATE_LIMIT = True
RATE_LIMIT_MIN_WAIT = datetime.timedelta(0,1) # one second
RATE_LIMIT_LAST_CALL = None
USER_AGENT = 'newsbin/1.0 (https://newsbin.us; michaelhouse@gmx.us)'

def get_title( title ):
    try:
        results, suggestion = wikipedia.search(title, results=1, suggestion=True)
        title = suggestion or results[0]
        return wikipedia.WikipediaPage(title)
    except:
        return None

def get_image( title ):
	try:
		response = requests.get( 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&pithumbsize=400&titles={}'.format(title) )
		pages = response.json()['query']['pages']
		for key,data in pages.items():
			return data['thumbnail']['source']
	except:
		return ''

def get_slug( *args ):
    slug = None

    with database.session_scope() as session:
        related = session.query( models.Annotation)\
                    .filter( models.Annotation.name.in_(args) | models.Annotation.wikiname.in_(args) )\
                    .filter( models.Annotation.slug != None ).all()

        # try to get a slug for each given name
        # and update related annos if we have one.
        for title in args:
            slug = politifact.get_slug(title)
            if slug:
                for anno in ( r for r in related if not r.slug):
                    anno.slug = slug
                break

        # didn't get a slug from politifact directly
        # so use a related annotations slug from db
        if not slug and related:
            slug = related[0].slug

    return slug

def _request( params ):

    global RATE_LIMIT_LAST_CALL
    global USER_AGENT

    params['format'] = 'json'
    if not 'action' in params:
        params['action'] = 'query'

    headers = {
        'User-Agent': USER_AGENT
    }

    if RATE_LIMIT and RATE_LIMIT_LAST_CALL and \
        RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT > datetime.datetime.now():

        # it hasn't been long enough since the last API call
        # so wait until we're in the clear to make the request

        wait_time = (RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT) - datetime.datetime.now()
        time.sleep(int(wait_time.total_seconds()))

    r = requests.get(API_URL, params=params, headers=headers)

    if RATE_LIMIT:
        RATE_LIMIT_LAST_CALL = datetime.datetime.now()

    return r.json()

def summarize( title ):
    title = title.strip(string.punctuation)
    page = get_title( title )
    if page:
        try:
            query_params = {
                'prop': 'extracts',
                'explaintext': '',
                'exintro': '',
                'titles': page.title
            }
            request = _request(query_params)
            summary = request['query']['pages'][page.pageid]['extract']

            annotation = models.Annotation(
                name=title,
                wikiname=page.title,
                wikilink='https://en.wikipedia.org/wiki/{}'.format(page.title),
                slug=get_slug( title, page.title ),
                image=get_image( page.title ),
                summary='\n\n'.join([ p for p in summary.split('\n') if p ]),
            )
            return annotation
        except Exception as e:
            print(e)
    return None


if __name__=='__main__':
    test = summarize('Donald J. Trump')
    print(test)
