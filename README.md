# Onion Website Parser
@rbsteinm and I were hired in order to develop an open-source tool which purpose is to crawl a specific .onion website. It crawls the forum pages of a forum and retrieves some information to store it in a MongoDB.

In order to use it, you need to be running any Linux distribution, use python3.5, install the required libraries: `pip3.5 install -r requirements.txt`, install the [tor browser](https://www.torproject.org/projects/torbrowser.html.en) and provide to the commandline your tor browser folder. Also, remember to fill out the parameters that you need in the credentials file (login, etc).

Example: ./python/crawler.py path_to/my_tor_browser/folder
