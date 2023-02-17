#!/bin/python3
from hashlib import new
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
from googlesearch import search
import datetime
import mysql.connector
import xlsxwriter
import os
from config import host, database, myuser, mypass, badwords

myconn = mysql.connector.connect(host=host, database=database, user=myuser, password=mypass)

g_query = input('[+] Search Term: ')
u_total_search = input('[+] Number of Url Results: ')
u_total_scan = input('[+] Number of Pages to Scan: ')
g_total = int(u_total_search)
g_urls = []
for j in search(g_query, tld='com', num=int(g_total), stop=int(g_total), pause=2):
	g_urls.append(j)
print('Collecting URLs')
print('-' * 80)
g_count = 0

for k in g_urls:
	g_count += 1
	print('[' + str(g_count) + '] ' + k)
user_total = int(u_total_scan)
scrapped_urls = set()
emails = set()
count = 0

if user_urls in g_urls:
	urls = deque([user_urls])
	print('-' * 80)
	try:
		while len(urls):
			if count == int(user_total):
				count = 0
				break

			count += 1
			url = urls.popleft()
			scrapped_urls.add(url)
			parts = urllib.parse.urlsplit(url)
			base_url = '{0.scheme}://{0.netloc}'.format(parts)
			path = url[:url.rfind('/')+1] if '/' in parts.path else url
			print('[%d] Processing %s' % (count, url))