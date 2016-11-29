from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os, hashlib
from parser import *

"""
This test program has for purpose to login, download and store pages
and information from a website through tor.
A few credentials and settings are to be set with your own
"""
# A few credentials:
PASSWORD = "6d53f2e71f0ce3e796c756ffb46e424d"
USERNAME_CARDING_SERVICES = "cf0b5e141fd6a7ff19f"
EMAIL = "cf0b5e141fd6a7ff19f@yopmail.com"

# Variables
THREADS_PAGES_NUMBER = 2

# URLS
URL = "http://pwoah7foa6au2pul.onion/"
URL_FORUM_SERVICE = URL + "forum/index.php?forums/carding-services.83/page-"
URL_LOGIN_FORUM = URL + "forum/index.php?login/"
URL_CAPTCHA = URL + "challenge.php"

# Current folder
FOLDER = os.path.dirname(os.path.realpath(__file__))

"""
Logs into the website, some captchas are needed to be solved individually
along the way.
"""
def visit_and_login(driver):
    # Solve the captcha
    print("Loading the captcha page, solve it to proceed")
    driver.get(URL_CAPTCHA)
    WebDriverWait(driver, 120).until(EC.title_contains("Login"))

    print("Loading the forum login page can take a long time, wait for it to be finished totally.")
    print("Solve the captcha if there is one, and log in.")
    driver.get(URL_LOGIN_FORUM)
    # Log in and solve the captcha
    WebDriverWait(driver, 120).until(EC.title_contains("Log in"))
    user_field = driver.find_element_by_id("ctrl_pageLogin_login").send_keys(USERNAME_CARDING_SERVICES)
    pass_field = driver.find_element_by_id("ctrl_pageLogin_password").send_keys(PASSWORD)
    WebDriverWait(driver, 120).until(EC.title_is("AlphaBay Market Forum"))
    return driver

"""
Goes through the thread pages one by one and calling the function that stores the information
for each thread
"""
def get_pages(driver):
    print("Starting the crawling and parsing")
    # xvfb_display = start_xvfb()
    for i in range(1, THREADS_PAGES_NUMBER + 1):
        threads_page = URL_FORUM_SERVICE + str(i)
        go_and_walk_through_thread(driver, threads_page)

    sleep(1000)
    # stop_xvfb(xvfb_display)

"""
Walks through a thread, downloading the html and storing it in the database
"""
def go_and_walk_through_thread(driver, threads_page):
    print("Loading:", threads_page)
    driver.get(threads_page)
    thread_urls = get_thread_urls(driver.page_source)
    for thread_page in thread_urls:
        print("Parsing:", thread_page)
        driver.get(URL + "forum/" + thread_page + "page-1")
        pages_total = get_n_pages(driver.page_source)

        for i in range(1, pages_total + 1):
            print("Parsing:", thread_page + "page-" + str(i))
            driver.get(URL + "forum/" + thread_page + "page-" + str(i))
            html = driver.page_source
            hashed_html = hasher(html)
            # Parse and store page and html

""" Calculates the hash of the data using sha256. It is returned in HEX formatting."""
def hasher(data):
    h = hashlib.sha256()
    data = data.encode('utf-8')
    h.update(data)
    return h.hexdigest()

"""
The main function needs to be fed the location of your Tor Browser folder.
Simply starts the program.
"""
def main():
    desc = "Visit check.torproject.org website"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()

    with TorBrowserDriver(args.tbb_path) as dr:
        dr = visit_and_login(dr)
        get_pages(dr)

if __name__ == '__main__':
  main()
