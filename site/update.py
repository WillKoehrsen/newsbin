import regex
import os
import json
import datetime

from package import filters, utilities
from package import models, session_scope
from package import log
from package import politifact

def update_annotations():
	with session_scope() as session:
		annotations = session.query( models.Annotation ).all()
		for annotation in annotations:
			name = annotation.name
			annotation.delete()
			utilities.summarize(name)

if __name__=='__main__':
	update_annotations()
