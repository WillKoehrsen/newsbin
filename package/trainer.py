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

def get_articles():
	db_engine = create_engine('sqlite:///{}'.format(defaults.database))
	Session = sessionmaker(bind=db_engine)
	session = Session()

	articles = session.query(models.Article).all()
	return articles

def get_dataset():
	articles = get_articles()
	dataset = []

	for article in articles:
		line = article.content
		entities = []

		people = set(article.get_people())
		for person in ( p for p in people if p ):
			for match in regex.finditer(regex.escape(person),line):
				entity = ( match.start(0), match.end(0), 'PERSON')
				entities.append(entity)

		dataset.append([(line,entities)])

	return dataset


def train():
	nlp = spacy.load('en')
	master_set = get_dataset()

	for _ in range(defaults.cycles):
		print('shuffling data-')
		random.shuffle(dataset)
		for raw_text, entity_offsets in dataset:
			doc = nlp.make_doc(raw_text)
			gold = GoldParse(doc, entities=entity_offsets)
			nlp.tagger(doc)
			loss = nlp.entity.update(doc, gold)
	print(' - done')
	nlp.end_training()
	print(os.path.join(defaults.location,'data/'))
	#nlp.save_to_directory(os.path.join(defaults.location,'data/'))

if __name__=='__main__':
	train()
