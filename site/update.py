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
				summary = wikipedia.summary(name)
				image_url = utilities.get_thumbnail( name )

				if summary:
					annotation.summary = summary
					annotation.image = image_url
				else:
					session.delete(annotation)

			except Exception as e:
				print(e)

if __name__=='__main__':
	update_annotations()
