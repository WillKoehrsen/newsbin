import os
import pprint

targets = (
	'static/js/newsbin.min.js',
	'static/css/newsbin.min.css'
)

here = os.path.dirname( os.path.abspath(__file__) )

def build( target ):
	target = os.path.join( here, target )
	location = os.path.dirname(target)
	config = '.'.join(target.split('.')[:-1]) + '.conf'

	bases = []
	with open(config) as conf:
		bases = [ os.path.normpath( os.path.join( location, b.strip() ) ) for b in conf.readlines() if b ]

	content = []
	for base in bases:
		with open(base,'r') as f:
			content.extend( [ l.strip() for l in f if l.strip() ] )

	with open(target,'w') as f:
		for line in content:
			f.write(line+'\n')

if __name__=='__main__':
	for target in targets:
		build( target )
