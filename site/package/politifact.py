from difflib import SequenceMatcher
import json
import requests
import os
from unidecode import unidecode as dc

# conversion between politifact truth-o-meter rating slugs
# and numeric values to calculate truth rating
rulings_key = {
	'true':1.0,
	'mostly-true':0.75,
	'barely-true':0.6,
	'half-true':0.5,
	'mostly-false':0.25,
	'false':0.0,
	'pants-fire':0.0,
}

def matches( target, name_list ):
	"""generate matches from politifact master list"""
	for name in name_list:
		ratio = SequenceMatcher( None, target, name ).ratio()
		yield ( name, ratio ) if ratio > 0.75 else ()

def get_slug( name ):
	"""preprocess name, get best matching slug"""
	name = "-".join(name.lower().strip().split())
	json_path = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'politifact.json' )
	with open(json_path) as data:
		data = json.load(data)
		slugs = [ item['name_slug'] for item in data ]

	results = sorted([ item for item in matches( name, slugs ) if item ],key=lambda x: x[1], reverse=True)
	return results[0][0] if results else None

def get_rating( name, count=5 ):
	"""get slug, fetch last <count> statements and calculate score"""
	try:
		slug = get_slug( name )
		if slug:
			url = 'http://www.politifact.com/api/statements/truth-o-meter/people/{}/json/?n={}'.format(slug,count)
			data = requests.get(url).json()
			rating = round( ( sum( rulings_key[item['ruling']['ruling_slug']] for item in data )/len(data) )*100,1)
			return (rating,slug)
	except Exception as e:
		pass

	return (None,None)
