from flask import Flask, request, render_template
import os
import re
import crawling
import reporting
import logging
import asyncio

crawlski = Flask(__name__, static_url_path='')

def check_url(raw_url):

   #validate protocol
    protocol = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_url)
    if protocol is None:
      print("no protocol")
      return False

    #validate ending part
#end_thing = raw_url.endswith('.com', '.org', '.edu') #'.gov', '.xxx', '.co', '.tax, '.news')
#    if not end_thing:
#      print("no ending thing")
#      return False

    #lets ping it - but first remove the protocol heder http://
    no_protocol = re.sub('http://', '', raw_url)
    response = os.system("ping -c 1 " + no_protocol)

    if response != 0:
      print("no response")
      return False

    return True

def create_spider(raw_url):

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    loop = asyncio.get_event_loop()

    crawler = crawling.Crawler(raw_url,
        exclude=None,
        strict=True,
        max_redirect=10,
        max_tries=4,
        max_tasks=10,
    )

    try:
        loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl.

    except KeyboardInterrupt:
        return False
        sys.stderr.flush()
        print('\nInterrupted\n')

    finally:
        reporting.report(crawler)
        crawler.close()
        return True

@crawlski.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

@crawlski.route('/')
def hello(name=None):
    return render_template('index.html', name=name)

@crawlski.route('/', methods=['POST'])
def crawl_url_form_post():

    raw_url = request.form['text']

    if check_url(raw_url) is True:
        if create_spider(raw_url) is True:
	       #spider is doneski
           return render_template('index.html', name=raw_url)
        else:
	        #might not just be spider - check how the url looks.
            return 'could not create the spydah'

    #check_url returned False so this is not a valid url to crawl
    else:
        return 'not a valid url'
	#TODO return static page that the url is not working becasue:
	  #no http://
	  #no .com or somethin
	  #could not connect - no ping

if __name__ == '__main__':
    crawlski.run()
