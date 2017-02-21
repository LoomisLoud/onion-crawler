# Onion Website Parser
Raphaël and me were hired in order to develop an open-source tool which purpose is to crawl a specific .onion website. It crawls the forum pages of a forum and retrieves some information to store it in a MongoDB.

In order to use it, you need to be running any Linux distribution, python3.5, having all of the required libraries in the requirements.txt file downloaded via pip or easy_install and provide to the commandline your tor browser folder. Also, remember to fill out the parameters that you need in the credentials file (login, etc).

Example: python3.5 python/crawler.py path_to/my_tor_browser/folder
