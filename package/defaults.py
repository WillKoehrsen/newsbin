import os
import sys

# ------------------------------------------------------------------------------
# GLOBALS
location = os.path.dirname(os.path.abspath(sys.argv[0]))
database = os.path.join( location, 'newsbin.db' )
cycles = 20

# ------------------------------------------------------------------------------
# DATA

# entity whitelist
entities = ('PERSON','NORP','FACILITY','ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LANGUAGE')
entity_ex = {
	'PERSON':'a person',
	'NORP':'nationality or religion/pol group',
	'FACILITY':'buildings and airports etc.',
	'ORG':'companies and agencies',
	'GPE':'countries, cities, states',
	'LOC':'mountain ranges, bodies of water',
	'PRODUCT':'objects, vehicles, foods',
	'EVENT':'battles, wars, sports events',
	'WORK_OF_ART':'titles of books/songs',
	'LANGUAGE':'named languages'
	}

# sources
sources = {
	'cnn':	[
				'http://rss.cnn.com/rss/edition.rss',
		  		'http://rss.cnn.com/rss/cnn_world.rss',
		  		'http://rss.cnn.com/rss/cnn_us.rss',
		  		'http://rss.cnn.com/rss/money_latest.rss',
		  		'http://rss.cnn.com/rss/cnn_allpolitics.rss',
		  		'http://rss.cnn.com/rss/cnn_tech.rss',
		  		'http://rss.cnn.com/rss/cnn_health.rss',
		  		'http://rss.cnn.com/rss/cnn_showbiz.rss',
		  		'http://rss.cnn.com/rss/cnn_travel.rss',
		  		'http://rss.cnn.com/rss/cnn_living.rss',
		  		'http://rss.cnn.com/rss/cnn_latest.rss'
			],
	'cnbc': [
				'http://www.cnbc.com/id/100003114/device/rss/rss.html',
				'http://www.cnbc.com/id/100727362/device/rss/rss.html',
				'http://www.cnbc.com/id/15837362/device/rss/rss.html',
				'http://www.cnbc.com/id/19832390/device/rss/rss.html',
				'http://www.cnbc.com/id/19794221/device/rss/rss.html',
				'http://www.cnbc.com/id/10001147/device/rss/rss.html',
				'http://www.cnbc.com/id/15839135/device/rss/rss.html',
				'http://www.cnbc.com/id/100370673/device/rss/rss.html',
				'http://www.cnbc.com/id/20910258/device/rss/rss.html',
				'http://www.cnbc.com/id/10000664/device/rss/rss.html',
				'http://www.cnbc.com/id/19854910/device/rss/rss.html',
				'http://www.cnbc.com/id/10000113/device/rss/rss.html',
				'http://www.cnbc.com/id/10000108/device/rss/rss.html',
				'http://www.cnbc.com/id/10000115/device/rss/rss.html',
				'http://www.cnbc.com/id/10001054/device/rss/rss.html',
				'http://www.cnbc.com/id/10000101/device/rss/rss.html',
				'http://www.cnbc.com/id/19836768/device/rss/rss.html',
				'http://www.cnbc.com/id/10000110/device/rss/rss.html',
				'http://www.cnbc.com/id/10000116/device/rss/rss.html',
				'http://www.cnbc.com/id/10000739/device/rss/rss.html',
				'http://www.cnbc.com/id/44877279/device/rss/rss.html',
				'http://www.cnbc.com/id/15839069/device/rss/rss.html',
				'http://www.cnbc.com/id/100646281/device/rss/rss.html',
				'http://www.cnbc.com/id/21324812/device/rss/rss.html'
		   ],
	'nytimes': [
				'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Africa.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Americas.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Europe.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/US.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Education.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/EnergyEnvironment.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/SmallBusiness.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Economy.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Sports.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Science.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Environment.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Space.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Health.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Travel.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml',
				'http://rss.nytimes.com/services/xml/rss/nyt/Movies.xml',
				'http://topics.nytimes.com/top/opinion/editorialsandoped/oped/contributors/index.html?rss=1'
		  		],
	'washingtonpost': [
						'http://feeds.washingtonpost.com/rss/rss_election-2012',
						'http://feeds.washingtonpost.com/rss/rss_powerpost',
						'http://feeds.washingtonpost.com/rss/rss_fact-checker',
						'http://feeds.washingtonpost.com/rss/rss_the-fix',
						'http://feeds.washingtonpost.com/rss/rss_monkey-cage',
						'http://feeds.washingtonpost.com/rss/rss_act-four',
						'http://feeds.washingtonpost.com/rss/rss_achenblog',
						'http://feeds.washingtonpost.com/rss/rss_checkpoint',
						'http://feeds.washingtonpost.com/rss/rss_innovations',
						'http://feeds.washingtonpost.com/rss/rss_morning-mix',
						'http://feeds.washingtonpost.com/rss/rss_post-nation',
						'http://feeds.washingtonpost.com/rss/rss_speaking-of-science',
						'http://feeds.washingtonpost.com/rss/rss_to-your-health',
						'http://feeds.washingtonpost.com/rss/rss_blogpost',
						'http://feeds.washingtonpost.com/rss/rss_digger',
						'http://feeds.washingtonpost.com/rss/national/energy-environment',
						'http://feeds.washingtonpost.com/rss/rss_on-leadership',
						'http://feeds.washingtonpost.com/rss/blogs/rss_the-switch',
						'http://feeds.washingtonpost.com/rss/rss_wonkblog'
					 ],
	'reuters': [
				'http://feeds.reuters.com/news/artsculture',
				'http://feeds.reuters.com/reuters/businessNews',
				'http://feeds.reuters.com/reuters/companyNews',
				'http://feeds.reuters.com/reuters/entertainment',
				'http://feeds.reuters.com/reuters/environment',
				'http://feeds.reuters.com/reuters/healthNews',
				'http://feeds.reuters.com/reuters/lifestyle',
				'http://feeds.reuters.com/news/wealth',
				'http://feeds.reuters.com/reuters/MostRead',
				'http://feeds.reuters.com/reuters/peopleNews',
				'http://feeds.reuters.com/Reuters/PoliticsNews',
				'http://feeds.reuters.com/reuters/scienceNews',
				'http://feeds.reuters.com/reuters/sportsNews',
				'http://feeds.reuters.com/reuters/technologyNews',
				'http://feeds.reuters.com/reuters/topNews',
				'http://feeds.reuters.com/Reuters/domesticNews',
				'http://feeds.reuters.com/Reuters/worldNews'
			  ],
	'foxnews': [
				'http://feeds.foxnews.com/foxnews/latest',
				'http://feeds.foxnews.com/foxnews/most-popular',
				'http://feeds.foxnews.com/foxnews/entertainment',
				'http://feeds.foxnews.com/foxnews/health',
				'http://feeds.foxnews.com/foxnews/section/lifestyle',
				'http://feeds.foxnews.com/foxnews/opinion',
				'http://feeds.foxnews.com/foxnews/politics',
				'http://feeds.foxnews.com/foxnews/science',
				'http://feeds.foxnews.com/foxnews/sports',
				'http://feeds.foxnews.com/foxnews/tech',
				'http://feeds.foxnews.com/foxnews/national',
				'http://feeds.foxnews.com/foxnews/video',
				'http://feeds.foxnews.com/foxnews/world'
			  ],
}

if __name__=='__main__':
	print(location)
	print(database)
