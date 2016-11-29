# -*- coding: utf-8 -*-

"""
This file takes an html posts page as input (you could also change the code to give it the url) and
for each message gets the author, the content of the message, the date and the thread in which it is
(for a given page each post is in the same thread obviously). The data is stored in arrays and then we
put it in a database using mongodb.
"""

from bs4 import BeautifulSoup, NavigableString
import pymongo
from pymongo import MongoClient
import re

"""
Goes through all the posts on the page and some data out of each post
input: html data of a thread page as a string
output: 4 arrays (message_contents, authors, dates, thread)
"""
def scrap_thread(html_data):
	soup = BeautifulSoup(html_data, 'lxml')

	message_info = soup.findAll("div", {"class":"messageInfo"})

	message_contents = []
	authors = []
	dates = []
	threads = []

	# get thread name
	thread = soup.find("div", {"class":"titleBar"})
	thread = thread.find("h1").get_text()
	print("thread:", thread)


	for mi in message_info:
		#soup = mi.descendants
		# scrap content
		message_content = mi.find("blockquote", {"class":"messageText"})
		#discard message text end marker
		for elem in message_content:
			if isinstance(elem, NavigableString):
				break
		message_contents.append(elem)
		#scrap author
		author = mi.find("a",{"class":"username author"})
		authors.append(author.get_text())
		#scrap message date
		date = mi.find("span", {"class":"DateTime"})
		dates.append(date.get_text())
		#fill thread name array
		threads.append(thread)
	assert(len(message_contents) == len(authors) == len(dates) == len(threads))

	print("number of messages in this thread:", len(message_contents))
	return message_contents, authors, dates, threads




"""
input: html page of the list of threads (html code in a string)
output: a list of strings contaning the url to each thread on the input page
"""
def get_thread_urls(html_data):
    soup = BeautifulSoup(html_data, 'lxml')
    balises_a = soup.findAll("a",{"class":"PreviewTooltip"})
    links = []
    for balise in balises_a:
        link = balise['href']
        if(link.endswith('unread')):
            link = link[:-6]
        links.append(link)
    return links

"""
This method gets the number of pages of a thread
input: html code of the thread
output: the number of pages in the thread
"""
def get_n_pages(html_data):
	soup = BeautifulSoup(html_data, 'lxml')
	found = soup.find("span",{"class":"pageNavHeader"})
	if not found:
		return 1
	text = found.get_text()
	number = re.match(r'.*?of\s(\d+)$', text).group(1)
	return int(number)

"""
This method takes as inputs the data outputed by scrap_thread
and for each message create a new document and stores it in the db.
TODO: test this method
"""
def put_in_db(message_contents, authors, dates, threads, client, db):
	docs = db.posts
	for i in range(len(message_contents)):
		doc = { "author":authors[i],
				"content":message_contents[i],
				"date":dates[i],
				"thread":threads[i]}
		doc_id = docs.insert_one(doc)
	print("inserting done.")
	print("test:", posts.find_one({"author":"higashi2014"}))


"""
some mongoDB shit-testing
"""
#client = MongoClient()
#db = client.darkweb_db
#put_in_db(m, a, d, t, client, db)
