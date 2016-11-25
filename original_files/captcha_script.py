#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Version 1.0
Version Date: 05. 10. 2016
Authors: Mathieu di Floriani, Hannes Spichiger, Vincent Benou, Rossana Caccia

Pyhon Version 2.7

Used libraries:
---------------
urllib2
requests
bs4.BeautifulSoup
selenium.webdriver
hashlib
datetime
time
os
shutil

To run this program, the above libraries need to be installed in your python environment.
To install the libraries, use "pip install <library-name>" in your console.

Usage:
------
Make sure you have a working internet connection. Otherwise Freeze-site won't be able to
access the pages you want to take an image from.

Run the script by executing it from your file explorer (explorer on windows, finder on
MacOS) or using the console with the command "python Freeze-site-1-00.py"

Parameters:
-----------
The script will ask you the following questions:

"Choose language: F (French) or E (English)"
Choose the language: This will only affect the parameter input exchange. All output will
still be in english. The following dialogue is represented under the assumtion that 'E' 
was given as an input.

"Input the url (please use the following form http://www.site.aaa)"
Write the url of the website you would like to take an image from. The indicated format
must be respected, otherwise, the script will end in an error.

"Input the screen height for the screenshot (standard = 1024)"
Insert the height of the browser window to be used. This parameter is of lesser
importance, since the script scrolls down to take a screenshot of the entire page in any
case.

"Input the screen width for the screenshot (standard = 800)"
Insert the width of the browser window to be used. Make sure to use a parameter of
sufficient size to be representative.

"use urllib or requests to get the source code? (everything in minuscule) Please use
requests for HTTPS sites"
Insert which library to use. Urllib does not support https. Using it with https sites
will result in a crash. Use the request library if you need to access a https-site.
Another input than urllib or requests will result in the question beeing repeated.


Execution:
----------
The script will request the server side code by a direct request. Afterwards, the script
will simulate an access to the site using phantomjs. The script will attempt to close
eventual pop-ups. Then it will proceed to capture the client side code and taking a
screen shot of the entire page. During the entire execution, all aperations and used 
parameters are recorded in a logfile. Hashes of all created files are calculated using
the sha256 hash-algorithm. All hashes (at the exception of the log-file) are registered
in the logfile as well. The hash of the logfile is returned via the console.

All created files are moved to a seperate folder in the folder of the executable. The
name of the folder is created based on the inputed url.
"""

import urllib2
import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4
from selenium import webdriver #pip install selenium
import hashlib
import datetime
import time
import os
import shutil

def renderedHTML(driver):
	"""Récupération du rendered HTML"""
	elem = driver.find_element_by_xpath("//*") 
	"""prend l'entier du code html"""
	html = elem.get_attribute("outerHTML")
	return html
    
def requestsSC(url):
	"""Récupération du code source d'une URL via requests"""
	headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0"}
	r = requests.get(url, headers=headers)
	contents = r.content
	return contents
				
def hasher(data):
	# Calculates the hash of the data using sha256. It is returned in HEX formatting.
	"""fonction de hashage: sha256"""
	h = hashlib.sha256()
	h.update(data)
	return h.hexdigest()
				
def hashimage(filename):
	# Calculates the hash of a picture by dividing it in chuncks of 4096 bits to avoid overload
	hash_sha256 = hashlib.sha256()
	with open(filename, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_sha256.update(chunk)
	return hash_sha256.hexdigest()

def urllibSC(url):
	"""Récupération du code source d'une URL via urllib2"""
	headers = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0"}
	request = urllib2.Request(url, headers=headers)
	contents = urllib2.urlopen(request).read()
	return contents

def saveContent(data, filename):
	"""Enregistrement de data dans un fichier filename"""
	with open(filename, 'wb+') as f:
		f.write(data.encode('utf-8'))

def get_server_source_code(RequestsOrUrllib,url,logfile):
	# Gets server source code. The method is separated in two segments depending on the used library
	urlsplit = url.split('.') # Get name for filenames
	if RequestsOrUrllib == "requests":
		s=requestsSC(str(url))
		soup = BeautifulSoup(s, 'html.parser') 
		s2= soup.prettify() # Organises the data in html format
		h = hasher(s)
		ti = datetime.datetime.utcnow() # Get time for filenames
		ti_date = str(ti.year) + "_" + str(ti.month) + "_" + str(ti.day) # Put time into usable format
		ti_time = str(ti.hour) + "_" + str(ti.minute) + "_" + str(ti.second) # Put time into usable format
		filename = 'server_source_code_request'+ ti_date + "_" + ti_time + urlsplit[1] +'.html' # Create filename
		print 'sha256 hash serverside source code with requests: ' + h
		saveContent(s2, filename)
          
          	# Write Logfile
		with open(logfile, 'a+') as f:
			f.write("\nServer Source Code:\n*******************\n")
			f.write("Use Library:\t\trequest\n")
			f.write("Saved in file:\t\t" + filename + "\n")
			f.write("Calculated Hash (sha256):\t\t" + h + "\n")
	else:
		s=urllibSC(str(url))
		soup = BeautifulSoup(s, 'html.parser')
		s2= soup.prettify() # Organises the data in html format
		h = hasher(s)
		ti = datetime.datetime.utcnow() # Get time for filenames
		ti_date = str(ti.year) + "_" + str(ti.month) + "_" + str(ti.day) # Put time into usable format
		ti_time = str(ti.hour) + "_" + str(ti.minute) + "_" + str(ti.second) # Put time into usable format
		filename = 'server_source_code_urllib'+ ti_date + "_" + ti_time +urlsplit[1] +'.html'  # Create filename
		print 'sha256 hash serverside source code with urllib: ' + h
		saveContent(s2, filename)
		
		# Write logfile
		with open(logfile, 'a+') as f:
			f.write("\nServer Source Code:\n*******************\n")
			f.write("Use Library:\t\turllib\n")
			f.write("Saved in file:\t\t" + filename + "\n")
			f.write("Hash (sha256):\t\t" + h + "\n")
	return filename
              
def bypasssimplecaptcha(driver):
	# Test method trying to bypass captchas. It does not work..	
	driver.add_cookie({'name':'ct_cookies_test','value': '56ebc769f7684a639aeb0ae987e949af','domain':'i-fit4life.cc'})
	driver.add_cookie({'name':'cf_clearance','value': '486aba476f3054a8f7dfe08e775ebd307fcd4c39-1475585354-1800','domain':'i-fit4life.cc'})
	driver.add_cookie({'name':'ct_checkjs','value': '56ebc769f7684a639aeb0ae987e949af','domain':'i-fit4life.cc'})
	driver.add_cookie({'name':'ct_sfw_pass_key','value':'2222b09f64dbd3ac68d1907f8b1e88e2','domain':'i-fit4life.cc'})
#	mainWin = driver.current_window_handle  
#	a= []
#	a= driver.find_elements_by_tag_name("iframe")
#	driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[0])
#	
#	# *************  locate CheckBox  **************
#	#wait = WebDriverWait(driver, 10)
#	#CheckBox = wait.until(EC.find_element_by_name("undefined")) 
#	#CheckBox = driver.find_element((By.name ,"undefined")[0])
#
#	CheckBox = WebDriverWait(driver, 200).until(EC.presence_of_element_located((By.ID ,"recaptcha-anchor"))) 
#	
#	# *************  click CheckBox  ***************
#	# making click on captcha CheckBox 
#	time.sleep(0.7)
#	CheckBox.click() 
#	time.sleep(1.5)
#	#***************** back to main window *********************************
#	driver.switch_to.window(mainWin)  

def PopUp_Handler(driver, logfile):
	# Method closing a eventual pop-up
	try:
		print "Please wait a bit"
		time.sleep(5) # give the page time to load the pop-up
		#print "blabla"
	
		el=driver.find_elements_by_id("fancybox-close")[0] # If the pop-up is a "fancy-box"-element, this is the part that permitts closing it.
		action = webdriver.common.action_chains.ActionChains(driver)
		action.move_to_element(el).click().perform() # click the close button

		#driver.switch_to_alert.dismiss()
		#driver.sendEvent('click',1,1,'left')
		#driver.move_with_offset(1,1)
		#driver.click()

		# Write log-entry
		ti = datetime.datetime.utcnow() # get time for log-entry
		with open(logfile, 'a') as f:
			f.write("\nALERT WAS DISMISSED BY MOUSCLICK AT CLOSE BUTTON AT TIME " + str(ti)) + "\n"
			#print "titi"
		time.sleep(5) # give the page time to close the pop-up
	except:
		pass
              
def get_client_source_code_and_Screenshot(url,ScreenHeight, ScreenWidth,logfile):
	# Get the client source code and the screenshot of the page.
	urlsplit = url.split('.') # Format url for file naming
	ep = 'C:\webdriver\phantomjs.exe'
	driver = webdriver.PhantomJS(executable_path=ep,service_args=['--web-security=no'])
	driver.set_window_size(ScreenHeight, ScreenWidth)
	driver.get(str(url))
	
	PopUp_Handler(driver, logfile) # Close eventual pop-ups
	#bypasssimplecaptcha(driver)

	# Get client side source code  
	content = renderedHTML(driver)
	content1 = content.encode('utf-8')

	# Stuff used for naming the file and writing the log
	ti = datetime.datetime.utcnow()
	ti_date = str(ti.year) + "_" + str(ti.month) + "_" + str(ti.day)
	ti_time = str(ti.hour) + "_" + str(ti.minute) + "_" + str(ti.second)
	csc_file = 'client_source_code'+ ti_date + "_" + ti_time +urlsplit[1] +'.html'
	csc_hash = hasher(content1)
	# Format the client side source code in html	
	soup = BeautifulSoup(content1, 'html.parser')
	s2= soup.prettify()
	print 'sha256 hash clientside source code: ' + csc_hash
	saveContent(s2, csc_file)
	
	# Name of screenshot
	im_file = 'Screenshot'+ ti_date + "_" + ti_time +urlsplit[1] +'.png'
	# Get screenshot
	driver.save_screenshot(im_file)
	im_hash = hashimage(im_file)	
	print 'sha256 hash screenshot: ' + im_hash
 
     # Write Logfile
	with open(logfile, 'a+') as f:
		f.write("\nClient Source Code:\n*******************\n")
		f.write("Browser:\t\tphantomjs\n")
		f.write("Executable path:\t" + ep + "\n")
		f.write("Saved in file:\t\t" + csc_file + "\n")
		f.write("Hash (sha256):\t\t" + csc_hash + "\n")
		f.write("\nScreenshot:\n***********\n")
		f.write("Browser:\t\tphantomjs\n")
		f.write("Executable path:\t" + ep + "\n")
		f.write("Saved in file:\t\t" + im_file + "\n")
		f.write("Hash (sha256):\t\t" + im_hash + "\n")
              
	##############################################################################################################
	#je ne comprends pas pourquoi ces deux lignes suivantes ne ferment pas le webdriver, en totu cas chez moi il y a une 
	#de temps en temps la fenêtre reste ouverte
	##############################################################################################################
	
	driver.close()
	driver.quit() 
	return csc_file, im_file
	
def Freeze_site(url,ScreenHeight, ScreenWidth,RequestsOrUrllib):
	# Main method calling all the others
	try:
		os.mkdir(url.split('.')[1]) # Create a folder based on the inserted url, if it does not yet exist
	except:
		pass
	logfile = Create_log(url) # Create logfile
	a = get_server_source_code(RequestsOrUrllib,url,logfile) # Get server source code
	b,c = get_client_source_code_and_Screenshot(url,ScreenHeight, ScreenWidth,logfile) # Get client source code and screenshot
	Close_log(logfile) # Finalise logfile
	# Move all files into created folder
	shutil.move(a, url.split('.')[1])
	shutil.move(b,url.split('.')[1])
	shutil.move(c,url.split('.')[1])
	shutil.move(logfile,url.split('.')[1])
	
def Create_log(url):
	# Creates the logfile and writes input variables into file
	# Returns name of the logfile
	
	# Create name of logfile	
	urlsplit=url.split('.')
	ti = datetime.datetime.utcnow()
	ti_date = str(ti.year) + "_" + str(ti.month) + "_" + str(ti.day)
	ti_time = str(ti.hour) + "_" + str(ti.minute) + "_" + str(ti.second)
	logfile = 'Freeze_site_log_' + ti_date + "_" + ti_time +urlsplit[1]+ '.txt'

	# Write initial parameters into logfile
	with open(logfile,'w') as f:
		f.write("Freeze-site Log\n===============\n")
		f.write("File name:\t\t" + logfile + "\n")
		f.write("Start time (UTC):\t" + str(ti) + "\n")
		f.write("\nInput Variables:\n***************\n")
		f.write("URL: \t\t\t" + url + "\n")
		f.write("Screen height: \t\t" + ScreenHeight + "\n")
		f.write("Screen width: \t\t" + ScreenWidth + "\n")
		f.write("Choice of library: \t" + RequestsOrUrllib + "\n")
        
	return logfile

def Close_log(logfile):
	# Writes final lines to logfile and prints out hash of logfile
	tf = datetime.datetime.utcnow()
    				
	with open(logfile, 'a') as f:
		f.write("\nEnd Time (UTC):\t\t" + str(tf) + "\n")
        
	print "Log saved to:\t" + logfile
	print "Hash of Logfile:\t" + hashimage(logfile)



# Running code
# Initial dialog for Input parameters
i=0
lang = raw_input("Choose language: F (French) or E (English) \n")    
while i==0:
	if lang =="F" or lang =="E":
		i=1
	else:
		lang = raw_input("Choose language: F (French) or E (English) \n")  

if lang == "F":
	url = raw_input("Input de l'url (svp sous la forme http://www.site.aaa)\n")
	ScreenHeight = raw_input("hauteur de l'écran pour screenshot (standard = 1024) \n")					
	ScreenWidth = raw_input("largeur de l'écran pour screenshot (standard = 800) \n")
	RequestsOrUrllib = raw_input("utiliser requests ou urllib pour obtenir le code source? (tout en minuscule) utiliser requests pour des sites qui renvoient du HTTPS\n")
	if RequestsOrUrllib != "requests" or "Requests" or "Urllib" or "urllib":
		pass
	else:
		RequestsOrUrllib = raw_input("utiliser requests ou urllib pour obtenir le code source? (tout en minuscule) \n")
else:
	url = raw_input("Input the url (please use the following form http://www.site.aaa)\n")
	ScreenHeight = raw_input("Input the screen height for the screenshot (standard = 1024) \n")
	ScreenWidth = raw_input("Input the screen width for the screenshot (standard = 800) \n")
	RequestsOrUrllib = raw_input("Use urllib or requests to get the source code? (everything in minuscule) Please use requests for HTTPS sites \n")
	if RequestsOrUrllib != "requests" or "Requests" or "Urllib" or "urllib":
		pass
	else:
		RequestsOrUrllib = raw_input("use urllib or requests to get the source code? (everything in minuscule) \n")

# Execute Freeze site
Freeze_site(url,ScreenHeight, ScreenWidth,RequestsOrUrllib)
