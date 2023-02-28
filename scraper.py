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

myconn = mysql.connector.connect(host=host,
                                 database=database,
                                 user=myuser,
                                 password=mypass)

g_query = input('[+] Search Term: ')
u_total_search = input('[+] Number of Url Results: ')
u_total_scan = input('[+] Number of Pages to Scan: ')
g_total = int(u_total_search)
g_urls = []
for j in search(g_query,
                tld='com',
                num=int(g_total),
                stop=int(g_total),
                pause=2):
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

for user_urls in g_urls:
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
			path = url[:url.rfind('/') + 1] if '/' in parts.path else url
			print('[%d] Processing %s' % (count, url))

			try:
				response = requests.get(url)
			except (requests.exceptions.MissingSchema,
			        requests.exceptions.ConnectionError):
				continue

			new_emails = set(
			 re.findall(r'[a-z0-9\.\-+]+@[a-z0-9\.\-+]+\.[a-z]+', response.text, re.I))
			emails.update(new_emails)

			for l in emails:
				NULL_ = None
				date_time = datetime.datetime.now()
				_date = str(date_time.date())
				_time = str(date_time.strftime('%X'))
				cursor = myconn.cursor(buffered=True)
				emailBulk = (NULL_, g_query, l, _date, _time)
				sql = 'INSERT INTO `emailbulk` (`ID`, `searchterm`, `email`, `date`, `time`) VALUES(%s,%s,%s,%s,%s)'
				cursor.execute(sql, emailBulk)
				myconn.commit()

			soup = BeautifulSoup(response.text, features='lxml')

			for anchor in soup.find_all('a'):
				link = anchor.attrs['href'] if 'gref' in anchor.attrs else ''
				if link.startswith('/'):
					link = base_url + link
				elif not link.startswith('http'):
					link = path + link
				if not link in urls and not link in scrapped_urls:
					urls.append(link)
	except KeyboardInterrupt:
		count = 0
		print('[-] Closing')
print('-' * 80)

for mail in emails:
	print(mail)
	NULL_ = None
	date_time = datetime.datetime.now()
	_date = str(date_time.date())
	_time = str(date_time.strftime('%X'))
	cursor = myconn.cursor(buffered=True)
	emails_scrapped = (NULL_, g_query, mail, _date, _time)
	sql = 'insert into `emails` (`ID`, `search_term`, `email`, `date`, `time`) values(%s,%s,%s,%s,%s)'
	cursor.execute(sql, emails_scrapped)
	myconn.commit()

no_del = 0
