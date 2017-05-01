import os

LOCATION = os.path.dirname( os.path.abspath(__file__) )
def expand( local ):
	return os.path.join( LOCATION, local )

targets = {
	'static/js/newsbin.min.js':(
			'static/js/base/extend.js',
			'static/js/base/interface.js',
			'static/js/base/newsbin.js'
	),
	'static/css/newsbin.min.css':(
			'static/css/base/about.css',
			'static/css/base/newsbin.css',
	)
}

def dump( bases ):
	for base in bases:
		with open(base) as f:
			for line in f:
				yield line

def build( target, bases ):
	with open(target,'w') as target:
		for line in dump( bases ):
			target.write(line)

for target,bases in targets.items():
	build( target, bases )
