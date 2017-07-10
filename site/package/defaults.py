
# sources to fetch articles from
sources = [
	('cnn','http://rss.cnn.com/rss/edition.rss','top'),
	('cnn','http://rss.cnn.com/rss/cnn_world.rss','world'),
	('cnn','http://rss.cnn.com/rss/cnn_us.rss','us'),
	('cnn','http://rss.cnn.com/rss/money_latest.rss','finance'),
	('cnn','http://rss.cnn.com/rss/cnn_allpolitics.rss','politics'),
	('cnn','http://rss.cnn.com/rss/cnn_tech.rss','technology'),
	('cnn','http://rss.cnn.com/rss/cnn_health.rss','health'),
	('cnn','http://rss.cnn.com/rss/cnn_showbiz.rss','social'),
	('cnn','http://rss.cnn.com/rss/cnn_travel.rss','travel'),
	('cnn','http://rss.cnn.com/rss/cnn_living.rss','social'),
	('cnn','http://rss.cnn.com/rss/cnn_latest.rss','top'),
	('cnbc','http://www.cnbc.com/id/100003114/device/rss/rss.html','top'),
	('cnbc','http://www.cnbc.com/id/100727362/device/rss/rss.html','world'),
	('cnbc','http://www.cnbc.com/id/15837362/device/rss/rss.html','us'),
	('cnbc','http://www.cnbc.com/id/19832390/device/rss/rss.html','world'),
	('cnbc','http://www.cnbc.com/id/19794221/device/rss/rss.html','world'),
	('cnbc','http://www.cnbc.com/id/10001147/device/rss/rss.html','finance'),
	('cnbc','http://www.cnbc.com/id/15839135/device/rss/rss.html','finance'),
	('cnbc','http://www.cnbc.com/id/100370673/device/rss/rss.html','opinion'),
	('cnbc','http://www.cnbc.com/id/20910258/device/rss/rss.html','finance'),
	('cnbc','http://www.cnbc.com/id/10000664/device/rss/rss.html','technology'),
	('cnbc','http://www.cnbc.com/id/19854910/device/rss/rss.html','technology'),
	('cnbc','http://www.cnbc.com/id/10000113/device/rss/rss.html','politics'),
	('cnbc','http://www.cnbc.com/id/10000108/device/rss/rss.html','health'),
	('cnbc','http://www.cnbc.com/id/10000115/device/rss/rss.html','social'),
	('cnbc','http://www.cnbc.com/id/10001054/device/rss/rss.html','finance'),
	('cnbc','http://www.cnbc.com/id/10000101/device/rss/rss.html','social'),
	('cnbc','http://www.cnbc.com/id/19836768/device/rss/rss.html','technology'),
	('cnbc','http://www.cnbc.com/id/10000110/device/rss/rss.html','social'),
	('cnbc','http://www.cnbc.com/id/10000116/device/rss/rss.html','social'),
	('cnbc','http://www.cnbc.com/id/10000739/device/rss/rss.html','social'),
	('cnbc','http://www.cnbc.com/id/44877279/device/rss/rss.html','business'),
	('cnbc','http://www.cnbc.com/id/15839069/device/rss/rss.html','business'),
	('cnbc','http://www.cnbc.com/id/100646281/device/rss/rss.html','finance'),
	('cnbc','http://www.cnbc.com/id/21324812/device/rss/rss.html','social'),
	('cnbc','http://www.cnbc.com/id/23103686/device/rss/rss.html','opinion'),
	('cnbc','http://www.cnbc.com/id/20409666/device/rss/rss.html','business'),
	('cnbc','http://www.cnbc.com/id/38818154/device/rss/rss.html','opinion'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/World.xml','world'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Africa.xml','world'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Americas.xml','us'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml','world'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Europe.xml','world'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml','world'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/US.xml','us'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Education.xml','education'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml','politics'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Business.xml','business'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/EnergyEnvironment.xml','technology'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/SmallBusiness.xml','business'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Economy.xml','finance'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml','technology'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml','technology'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Sports.xml','sports'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Science.xml','science'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Environment.xml','science'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Space.xml','technology'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Health.xml','health'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Travel.xml','social'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml','social'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Arts.xml','social'),
	('nytimes','http://rss.nytimes.com/services/xml/rss/nyt/Movies.xml','social'),
	('nytimes','http://topics.nytimes.com/top/opinion/editorialsandoped/oped/contributors/index.html?rss=1','opinion'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_election-2012','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_powerpost','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_fact-checker','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_the-fix','opinion'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_monkey-cage','opinion'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_act-four','social'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_achenblog','science'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_checkpoint','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_innovations','technology'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_morning-mix','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_post-nation','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_speaking-of-science','science'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_to-your-health','health'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_blogpost','opinion'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_digger','politics'),
	('washpo','http://feeds.washingtonpost.com/rss/national/energy-environment','science'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_on-leadership','business'),
	('washpo','http://feeds.washingtonpost.com/rss/blogs/rss_the-switch','technology'),
	('washpo','http://feeds.washingtonpost.com/rss/rss_wonkblog','politics'),
	('reuters','http://feeds.reuters.com/news/artsculture','social'),
	('reuters','http://feeds.reuters.com/reuters/businessNews','business'),
	('reuters','http://feeds.reuters.com/reuters/companyNews','business'),
	('reuters','http://feeds.reuters.com/reuters/entertainment','social'),
	('reuters','http://feeds.reuters.com/reuters/environment','science'),
	('reuters','http://feeds.reuters.com/reuters/healthNews','health'),
	('reuters','http://feeds.reuters.com/reuters/lifestyle','social'),
	('reuters','http://feeds.reuters.com/news/wealth','finance'),
	('reuters','http://feeds.reuters.com/reuters/MostRead','top'),
	('reuters','http://feeds.reuters.com/reuters/peopleNews','social'),
	('reuters','http://feeds.reuters.com/Reuters/PoliticsNews','politics'),
	('reuters','http://feeds.reuters.com/reuters/scienceNews','science'),
	('reuters','http://feeds.reuters.com/reuters/sportsNews','sports'),
	('reuters','http://feeds.reuters.com/reuters/technologyNews','technology'),
	('reuters','http://feeds.reuters.com/reuters/topNews','top'),
	('reuters','http://feeds.reuters.com/Reuters/domesticNews','us'),
	('reuters','http://feeds.reuters.com/Reuters/worldNews','world'),
	('foxnews','http://feeds.foxnews.com/foxnews/latest','top'),
	('foxnews','http://feeds.foxnews.com/foxnews/most-popular','top'),
	('foxnews','http://feeds.foxnews.com/foxnews/entertainment','social'),
	('foxnews','http://feeds.foxnews.com/foxnews/health','health'),
	('foxnews','http://feeds.foxnews.com/foxnews/section/lifestyle','social'),
	('foxnews','http://feeds.foxnews.com/foxnews/opinion','opinion'),
	('foxnews','http://feeds.foxnews.com/foxnews/politics','politics'),
	('foxnews','http://feeds.foxnews.com/foxnews/science','science'),
	('foxnews','http://feeds.foxnews.com/foxnews/sports','sports'),
	('foxnews','http://feeds.foxnews.com/foxnews/tech','technology'),
	('foxnews','http://feeds.foxnews.com/foxnews/national','us'),
	('foxnews','http://feeds.foxnews.com/foxnews/world','world'),
	('wired','https://www.wired.com/feed/rss','top'),
	('wired','https://www.wired.com/feed/category/business/latest/rss','business'),
	('wired','https://www.wired.com/feed/category/culture/latest/rss','social'),
	('wired','https://www.wired.com/feed/category/gear/latest/rss','technology'),
	('wired','https://www.wired.com/feed/category/security/latest/rss','technology'),
	('wired','https://www.wired.com/feed/category/science/latest/rss','science'),

	('techcrunch','http://feeds.feedburner.com/TechCrunch/startups','startups'),
	('techcrunch','http://feeds.feedburner.com/TechCrunch/fundings-exits','startups'),
	('techcrunch','http://feeds.feedburner.com/TechCrunch/social','social'),
	('techcrunch','http://feeds.feedburner.com/Mobilecrunch','startups'),
	('techcrunch','http://feeds.feedburner.com/Techcrunch/europe','startups'),
	('techcrunch','http://feeds.feedburner.com/TechCrunch/greentech','technology'),
]

labels = {
	'cnn':'CNN',
	'cnbc':'CNBC',
	'nytimes':'The New York Times',
	'washpo':'The Washington Post',
	'reuters':'Reuters',
	'foxnews':'Fox News',
	'wired':'Wired',
	'techcrunch':'TechCrunch',
	'us':'U.S.',
}

def default_categories():
	results = []
	for source, feed, categories in sources:
		for category in categories.split(','):
			result = ( category, labels.get(category,category.capitalize()) )
			if result not in results:
				results.append(result)
	results = sorted(results,key=lambda x: x[1])
	return results

def default_feeds():
	for source, feed, categories in sources:
		yield feed

def default_sources():
	results = []
	for source, feed, categories in sources:
		result = ( source, labels.get(source,source.capitalize()) )
		if result not in results:
			results.append(result)
	results = sorted(results,key=lambda x: x[1])
	return results

def category_label( category ):
	if category in labels:
		return labels[category]
	else:
		return category.capitalize()
