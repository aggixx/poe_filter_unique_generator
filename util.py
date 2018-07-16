import urllib2
import json

def get_url_data(raw_url):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

	req = urllib2.Request(raw_url, headers=headers)
	
	url = urllib2.urlopen(req)
	
	data = url.read()
	return data
	
def get_url_as_json(url):
	return json.loads(get_url_data(url))