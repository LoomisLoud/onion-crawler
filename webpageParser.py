# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, NavigableString
html_file = open('posts_list.html', 'r', encoding="utf-8")
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
	#fill thread name
	threads.append(thread)
	print(author.get_text(), ":", elem)

print("number of messages in this thread:", len(message_contents))

