from __future__ import print_function
import requests
import pyrebase
import json
import nltk, re
import feedparser
from pprint import pprint
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from gensim import corpora, models, similarities
from time import time
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation


#exec(open("config.py").read())
fire_config = {
	        "apiKey": "GET YOUR OWN KEY",
            "authDomain": "AUTHENTICATION KEY",
            "databaseURL": "LOCATION OF YOUR DB",
            "storageBucket": "STORAGE LOCATION",
            "messagingSenderId": "MESSENGER ID"
        }


firebase = pyrebase.initialize_app(fire_config)

def news_search(search_term, *args):
	db = firebase.database()

	
	base = "http://www.faroo.com/api?q="
	connector = "&start=1&length=10&l=en&src=news&f=json"
	api_key = "&key=NWPsWfgdnoKG8KLL56rzN8Zosbk_"

	search = base+search_term+connector+api_key
		
	r = requests.get(search)
	text = str(r.content, 'utf-8', errors='ignore')
	newR = json.loads(text)
		
	for i, entry in enumerate(newR['results']):
		row = {"data_type": "article", "tag": search_term}
		row['author'] = entry['author']
		row['text'] = entry['title']
		row['link'] = entry['url']
		row['date'] = entry['date']

		#apply sentiment analysis
		text = TextBlob(row['text'])
		sent = {"polarity": text.polarity, "subjective": text.subjectivity}
		row['sentiment'] = sent
	
		data = json.dumps(row)
		print(data)

		db.child(search_term).push(json.loads(data))

def web_search(search_list = [], *args):
	db = firebase.database()
	for term in search_list:
		base = "http://www.faroo.com/api?q="
		connector = "&start=1&length=10&l=en&src=web&f=json"
		api_key = "&key=KEY GOES HERE" #Get your own API Key at http://www.faroo.com

		search = base+term+connector+api_key

		r = requests.get(search)
		print(r.content)

		text = str(r.content, 'cp437', errors='ignore')
		newR = json.loads(text)

		for i, entry in enumerate(newR['results']):
			row = {"data_type": "web", "tag": term}
			row['author'] = entry['author']
			row['text'] = entry['title']
			row['link'] = entry['url']
			row['date'] = entry['date']

			#apply NB Classifier - sentiment analysis
			text = TextBlob(row['text'])
			sent = {"polarity": text.polarity, "subjective": text.subjectivity}
			row['sentiment'] = sent

			data = json.dumps(row)
			print(data)
		
			db.child(term).push(json.loads(data))



def parseRSS( rss_url ):
    return feedparser.parse( rss_url ) 
    
    
    
# Function grabs the rss feed headlines (titles) and returns them as a list
def getHeadlines( rss_url ):
    db = firebase.database() 
    
    headlines = []
    
    feed = parseRSS( rss_url )
    for newsitem in feed['items']:
        headlines.append(newsitem['title'])
        headlines.append(newsitem['link'])
    
    print('Printing subset of headlines...', set(headlines))
    
    for item in headlines:
        url = item[1]
        print(url)
        
        
    return(headlines)



# A list to hold all headlines
def getRssFeed():
   
    allheadlines = []
    
    # List of RSS feeds that we will fetch and combine
    
    newsurls = {
    'apnews':           'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a76b4ad082fe88aa0db04909',
    'googlenews':       'http://news.google.com/?output=rss',
    'reutersBiz':       'http://feeds.reuters.com/reuters/businessNews',
    'yahoonews':        'http://news.yahoo.com/rss/',
    'disasters':        'http://www.gdacs.org/xml/rss.xml',
    'reutersMoney':     'http://feeds.reuters.com/news/wealth',
    'reutersEnv':       'http://feeds.reuters.com/reuters/environment',
    'reutersTech':      'http://feeds.reuters.com/reuters/technologyNews',
    'reutersSci':       'http://feeds.reuters.com/reuters/scienceNews'
    
    }
    
    # Iterate over the feed urls
    
    for key,url in newsurls.items():
    # Call getHeadlines() and combine the returned headlines with allheadlines
        
        allheadlines.extend( getHeadlines( url ) )
        
        # Iterate over the allheadlines list and print each headline
        for hl in allheadlines:
            print(hl)
         
         
    return set(allheadlines)



def getDocsFromSearch(url):      
    
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    r = s.get(url)
    texts = r.text
    visible_texts = clean_html(texts)
            
    print(visible_texts)
    return(visible_texts)
    

def getDocsFromLink(term):
    db = firebase.database()
    twit = db.child(term).get()
    
    url = []
    for item in twit.each():
        obj = item.val()
        link = obj['link']
        url.append(link)
        print(url)
        
    
    uni_list = set(url)
    
    print("Retrieving web documents...")
    
    docs = []
    for i in uni_list:
        if i == 'none':
            print(i)
        else:
            s = requests.Session()
            s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
            r = s.get(i)
            texts = r.text
            visible_texts = clean_html(texts)
            docs.append(visible_texts)
            
            print(visible_texts)

    return(docs)




def clean_html(html):
    """
    Copied from NLTK package.
    Remove HTML markup from the given string.

    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """
    str_html = str(html)

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", str_html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"[\s]", "  ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", "\n", cleaned)
    
    tmp = cleaned.split()
    print(tmp)
    
    for i in tmp:
        if len(i) <= 1:
            tmp.remove(i)
        else:
            pass
    
    tmp = ' '.join(tmp)
    print(tmp)
    
    return(tmp)


def getMedia(term):
	db = firebase.database()

	twit = db.child(term).get()
	#data = str(twit, 'cp437', errors='ignore')
	for item in twit.each():
		obj = json.dumps(item.val())
		print(obj)
  
      

		
def genMedia(term):
    documents = getDocsFromLink(term)
    
    print("Loading dataset...")
    stoplist = set('for a of the and to in but'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
    
    print(texts)
    
    from collections import defaultdict
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    
    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    dictionary = corpora.Dictionary(texts)
    
    print(dictionary)
    dictionary.save('web_lda.dic')    
    
    dictionary.token2id
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=100)
    
    corp_lda = lda[corpus]
    
    #tfidf = models.TfidfModel(corpus)
    #corpus_tfidf = tfidf[corpus]
    
    for doc in corp_lda:
        pprint(doc)

    corpora.MmCorpus.serialize('web_lda.mm', corp_lda)





