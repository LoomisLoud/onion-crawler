# -*- coding: utf-8 -*-

"""
This file takes an html posts page as input (you could also change the code to give it the url) and
for each message gets the author, the content of the message, the date and the thread in which it is
(for a given page each post is in the same thread obviously). The data is stored in arrays and then we
put it in a database using mongodb.
"""

from bs4 import BeautifulSoup, NavigableString
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
	if thread is None:
		thread = ""
		print("a thread name could not be found!")
	else:
		thread = thread.find("h1").get_text()
	for mi in message_info:
		# scrap content
		message_content = mi.find("blockquote", {"class":"messageText"})
		#discard message text end marker
		for elem in message_content:
			if isinstance(elem, NavigableString):
				break
		if elem is None:
			elem = ""
			print("a message could not be found!")
		message_contents.append(elem)
		#scrap author
		author = mi.find("a",{"class":"username author"})
		if author is None:
			authors.append("")
			print("an author name could not be found!")
		else:
			authors.append(author.get_text())
		#scrap message date
		#note: sometimes the date is contained in a 'abbr' balise instead of 'span'
		date = mi.find("span", {"class":"DateTime"})
		if date is None:
			date = mi.find("abbr", {"class":"DateTime"})
			if date is None:
				print("a date could not be found!")
				dates.append("")
			else:
				dates.append(date.get_text())
		else:
			dates.append(date.get_text())
		#fill thread name array
		threads.append(thread)
	assert(len(message_contents) == len(authors) == len(dates) == len(threads))

	current_page_data = [ (m, a, d, t) for m, a, d, t in zip(message_contents, authors, dates, threads) ]
	return current_page_data

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
