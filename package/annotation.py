# response = requests.get('https://en.wikipedia.org/w/api.php?action=query&titles=Donald%20Trump&format=json&prop=extracts&exintro=')
# link = https://en.wikipedia.org/wiki/<TITLE where space = '_'>

import requests, json
import spacy, regex, re

from pprint import PrettyPrinter
pretty = PrettyPrinter(indent=4,depth=500).pprint

def search( name ):
    response = requests.get( 'https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&indexpageids=&srsearch={}'.format(name.replace(' ','%20')) )
    results = json.loads(response.text)['query']['search']

    return [ result['title'] for result in results ]

def get_summary( name ):
    response = requests.get('https://en.wikipedia.org/w/api.php?action=query&titles={}&format=json&prop=extracts&exintro=&explaintext=&redirects='.format( name ))
    pages = json.loads(response.text)['query']['pages']
    summary = ''.join([ pages[pageid]['extract'] for pageid in pages if pages[pageid]['title'] == name ])
    return summary

def get_links( name ):
    response = requests.get('https://en.wikipedia.org/w/api.php?action=query&titles={}&format=json&prop=links'.format( name ))
    pages = json.loads(response.text)['query']['pages']
    results = {}
    for pageid in pages:
        for link in pages[pageid]['links']:
            title = link['title']
            url = 'https://en.wikipedia.org/wiki/{}'.format( title.replace(' ','_') )
            results[title] = url
    return results

def summarize( name ):
    summary = ''
    try:
        summary = get_summary( name )
    except:
        pass
    if 'may refer to' in summary or not summary:
        try:
            links = get_links( name )
            summary = '{} may refer to:\n{}'.format( name, '\n'.join( [ '<a href="{}">{}</a>'.format( links[item], item ) for item in links ] ) )
        except:
            pass
    return summary

def aliases( name, content ):
    name = clean( name )
    words = regex.split('[^a-zA-Z]', content)
    results = [ word for word in words if word in name and word != name and word ]
    return results

def clean( name ):
    name = regex.sub( '\'s', '', name )
    name = max( regex.split('\"|\'|\(|\)|\,|-',name), key=len )
    name = name.strip(' ,.?\"\'()!-\{\}[]<>\n|\\/')
    return name

def get_mentions( content ):
    nlp = spacy.load('en')
    article = nlp( content )
    results = { entity.text:{'clean':clean(entity.text),'aliases':aliases( entity.text, content )} for entity in article.ents if entity.label_=='PERSON' }
    return {name:results[name] for name in results if not [ i for i in results if name in results[i]['aliases'] ] }














#content = ''
#with open('test.txt|r') as f:
#    content = f.read()
#get_people(content)
