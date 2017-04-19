import spacy
import random
import regex
import unidecode
from spacy.gold import GoldParse
from spacy.language import EntityRecognizer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

import defaults
import models
import sys, os

import importlib.util

def random_article( num ):
	db_engine = create_engine('sqlite:///{}'.format(defaults.database))
	Session = sessionmaker(bind=db_engine)
	session = Session()

	for _ in range(num):
		query = session.query(models.Article)
		rowCount = int(query.count())
		article = query.offset(int(rowCount*random.random())).first()
		yield article

def dump( count ):
	with open('dump.py','w') as out:
		for _type in defaults.entity_ex:
			out.write('# {}:{}\n'.format(_type,defaults.entity_ex[_type]))

	lines = []
	for article in random_article(int(count)):
		lines += [ '(\'{}\',\n [])'.format( l.replace('\"','\\\"').replace('\'','\\\'').strip().rstrip('\\') ) for l in article.content.split('\n') if l ]

	data_set = 'DATA_SET=[\n {}\n]'.format(',\n '.join(line for line in lines))
	with open('dump.py','a') as out:
		out.write(data_set)

def train( target ):
	directory = os.path.dirname(os.path.abspath(target))
	sys.path.insert(1, directory)
	import dump

	nlp = spacy.load('en')

	for _ in range(defaults.cycles):
		print('shuffling data-')
		random.shuffle(dump.DATA_SET)
		for raw_text, entity_offsets in dump.DATA_SET:
			doc = nlp.make_doc(raw_text)
			gold = GoldParse(doc, entities=entity_offsets)
			nlp.tagger(doc)
			loss = nlp.entity.update(doc, gold)
	print(' - done')
	nlp.end_training()
	nlp.save_to_directory(os.path.join(defaults.location,'/data'))

def parse( content ):
	nlp = spacy.load('en')
	chunked = nlp( content )
	people = [ entity for entity in chunked.ents if entity.label_ in defaults.entities ]
	print('LINE: {}'.format(content))
	for p in people:
		print('	{}'.format(p))

OPS = {
	'--dump':dump,
	'--train':train,
	'--parse':parse,
}

if __name__=='__main__':
	if len(sys.argv)==3:
		command, target = sys.argv[1:]
		OPS[command]( target )
