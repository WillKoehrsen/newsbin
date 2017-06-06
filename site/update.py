import regex
import os
import json
import datetime

from package import filters, utilities
from package import models, session_scope
from package import log
from package import politifact

import wikipedia
from wikipedia.exceptions import PageError

def update_annotations():
	with session_scope() as session:
		annotations = session.query( models.Annotation ).all()
		for annotation in annotations:
			try:
				name = annotation.name
				annotation.summary = wikipedia.summary(name)
				annotation.image = utilities.get_thumbnail( name )
			except Exception as e:
				pass

if __name__=='__main__':
	update_annotations()
