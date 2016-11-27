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

"""
this method scraps the given html thread file and outputs 4 arrays containing the data
"""
def scrap_thread(html_file):
	html_data = html_file.read()
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

	print("number of messages in this thread:", len(message_contents))
	return message_contents, authors, dates, threads


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



html_file = open('posts_list.html', 'r', encoding="utf-8")
m,a,d,t = scrap_thread(html_file)
client = MongoClient()
db = client.darkweb_db
put_in_db(m, a, d, t, client, db)
