#!/usr/bin/python
import sys
import os
work_folder = '/home/gelado/xscripts'
sys.path.append(os.path.join(work_folder,'common'))
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urlparse import urlparse
import mechanize
import argparse
import re
import time
import datetime
import MySQLdb
from PIL import Image
from cStringIO import StringIO
from xtoolz import get_img_size , is_img_portrait , start_db, load_config, bot_summary, ensure_dir
from timeit import default_timer as timer
from logger import logr
#
#
# functions
def rec_img_indb(db_object,dbfd_uri,dbfd_pstar,img_height,img_width,is_portrait,sample_timestamp):
	# if parse_only: return
	pointer = db_object.cursor()
	query = "INSERT INTO tb_crawler (dbfd_uri,dbfd_pstar,img_height,img_width,is_portrait,sample_timestamp) VALUES (%s, %s,%s, %s, %s, %s)"
	pointer.execute( query, (dbfd_uri,dbfd_pstar,img_height,img_width,is_portrait,sample_timestamp))
	return

def rec_link(url, blogname, imghash):
    pointer = dbconn_tumblr.cursor()
    pointer.execute("INSERT INTO images (db_imagelink,db_blogname,db_imghash) VALUES (%s, %s, %s)", (url,blogname, imghash))
    return

def rec_page(url):
	pointer = dbconn_tumblr.cursor()
	pointer.execute("INSERT INTO pages (db_url,db_completed) VALUES (%s, %s)", (url,"1"))
	return

def check_db_imageurl(url):
	pointer = dbconn_tumblr.cursor()
	query = "SELECT * FROM images WHERE db_imagelink = '%s'" % url
	pointer.execute(query)
	rows = pointer.fetchall()
	return(rows)

def check_db_imagehash(imghash):
	pointer = dbconn_tumblr.cursor()
	query = "SELECT * FROM images WHERE db_imghash = '%s'" % imghash
	pointer.execute(query)
	rows = pointer.fetchall()
	return(rows)

def check_db_page(url):
	pointer = dbconn_tumblr.cursor()
	query = "SELECT * FROM pages WHERE db_url = '%s' AND db_completed = '1'" % url
	pointer.execute(query)
	rows = pointer.fetchall()
	return(rows)


def get_url_archives(url_master):
	global site_errors
	br = mechanize.Browser()
	br.set_handle_robots(False)
	url_array = []
	try:
		br.open(url_master)
		months = ['January','February','March','April','May','June','July','August','September','October','November','December', \
				  'Janvier', 'Fevrier','mars', 'Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre' \
				  'Ocak', 'Subat', 'Mart', 'Nisan', 'Mayis', 'Harizan', 'Temmuz', 'Agustos', 'Eylul', 'Ekim', 'Kasim', 'Aralik']
		for item in br.links():
			if item.text in months:
				parsed = urlparse(item.base_url)
				url_parsed = parsed.scheme + '://' + parsed.netloc
				url = url_parsed + item.url
				url_array.append(url)
	except:
		site_errors.append(url_master)
		logr( 'Site %s not working properly' % url_master)
	return(url_array)


def goodmission(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class" : "photo-wrapper-inner"}) 
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.a.img['src']
		if debug_app : logr( 'img link ' + res_url )
	except:
		try:
			res_url = soup.img['src']
			if debug_app : logr( 'img link ' + res_url )
		except:
			res_url = 'error'
			if debug_app : logr( 'error' )
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url)

def stilettocouture(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class" : "PhotoWrapper"}) 
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.a.img['src']
		if debug_app : logr( 'img link ' + res_url )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url) 

def mejeej(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class" : "photo-wrap"}) 
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.a['href']
		if debug_app : logr( 'img link ' + res_url )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url) 

def heelhunter(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("article")
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	tags = soup.find_all("a")
	soup.decompose()
	try:
		res_url = tags[0].img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url) 

def haawheels(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class" : "autopagerize_page_element"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	tags = soup.find_all("img")
	soup.decompose()
	try:
		res_url = tags[0]['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url) 

def nicelegsandperspectives(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("ul",{"id" : "posts"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	tags = soup.find_all("section", class_="top")
	soup.decompose()
	try:
		res_url = tags[0].img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url) 

def addicttosex(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class" : "photo-wrapper-inner"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url) 

def sexyonheels(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soup = BeautifulSoup(req.text,"lxml")
	tags = soup.find_all('div')
	soup.decompose()
	pattern = re.compile('src="?\'?([^"\'>]*)')
	try:
		res_url = re.findall(pattern, str(tags[5]))[0]
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url)   

def bestcelebritylegs(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class": "media"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)   


def tuneman86(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("section",{"class": "top media"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)   
	
def highheelsforever(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class": "photo"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def closetheels(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"id": "container"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def naughtylegs(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"id": "posts"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		####### bypass images that are avatars http://apollo:3080/crawler/crawler.2/peeptoeheels.tumblr.com/avatar_f570d9426951_16.png
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def get_sweet(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class": "post"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def lgshls(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class": "photo_post"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url  )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def shoelvr67(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("section",{"class": "top media"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def jjperfectlegs(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("section",{"class": "post"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app : logr( 'img link ' + res_url )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	soup.decompose()
	return(res_url)

def hizzle(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soup = BeautifulSoup(req.text,"lxml")
	tags = soup.find_all('meta')
	soup.decompose()
	if len(tags) == 72:
		res_url = tags[48]['content']
		if re.match(img_pattern,res_url) :
			if debug_app : logr( 'img link ' + res_url )
		else:
			res_url = 'error'
			if debug_app : logr( 'error' )
	else:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url)

def evil(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soup = BeautifulSoup(req.text,"lxml")
	tags = soup.find_all('meta')
	soup.decompose()
	if len(tags) == 63:
		res_url = tags[39]['content']
		if re.match(img_pattern,res_url) :
			if debug_app : logr( 'img link ' + res_url )
		else:
			res_url = 'error'
			if debug_app : logr( 'error' )
	else:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url)

def hotonheels(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"id": "tw_post_container"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	tags = soup.find_all('a')
	soup.decompose()
	try:
		res_url = tags[0].img['src']
		if debug_app : logr( 'img link ' + res_url )
	except:
		res_url = 'error'
		if debug_app : logr( 'error' )
	return(res_url)

def heelsfromhell(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"id": "content"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	tags = soup.find_all('a')
	nxt_soup = BeautifulSoup(str(tags[0]))
	try:
		res_url = nxt_soup.img['src']
		if debug_app : logr( 'img link ' + res_url )
	except:
		tags = soup.find_all('p')
		nxt_soup = BeautifulSoup(str(tags[0]))
		try:
			res_url = nxt_soup.img['src']
			if debug_app : logr( 'img link ' + res_url )
		except:
			if debug_app : logr( 'error' )
			res_url = 'error'
	soup.decompose()
	return(res_url)

def therubik(url):
	req = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies)
	soupfilter = SoupStrainer("div",{"class": "post-content"})
	soup = BeautifulSoup(req.text,"lxml",parse_only=soupfilter)
	try:
		res_url = soup.img['src']
		if debug_app :  logr( 'img link ' + res_url )
	except:
		if debug_app : logr( 'error' )
		res_url = 'error'    
	soup.decompose()       
	return(res_url)

def find_image_urls(page_url):
	array_urls = []
	htmlsource = requests.get(page_url,headers=my_headers,timeout=my_timeout,proxies=my_proxies) 
	soupfilter = SoupStrainer("div",{"class" : "l-content"})
	soup = BeautifulSoup(htmlsource.text,"lxml",parse_only=soupfilter)
	tags = soup.find_all("a")
	all_links_for_page = [link['href'] for link in tags]
	for every_link in all_links_for_page :
		if debug_app : logr( 'post link ' + every_link )
		url_parsed = urlparse(every_link)
		if url_parsed.netloc == 'sweet57334.tumblr.com':
			img_link = get_sweet(every_link)
		elif url_parsed.netloc == 'highheelsandshizzle.tumblr.com':
			img_link = hizzle(every_link)
		elif url_parsed.netloc == 'heelsfromhell.tumblr.com' :
			img_link = heelsfromhell(every_link)
		elif url_parsed.netloc == 'therubik.tumblr.com' :
			img_link = therubik(every_link)
		elif url_parsed.netloc == 'shoelvr67.tumblr.com' :
			img_link = shoelvr67(every_link)
		elif url_parsed.netloc == 'hot-on-heels.com' :
			img_link = hotonheels(every_link)
		elif url_parsed.netloc == 'legsandheels.tumblr.com' :
			img_link = lgshls(every_link)
		elif url_parsed.netloc == 'jjperfectlegs.tumblr.com' or url_parsed.netloc =='classysexypixs.tumblr.com' :
			img_link = jjperfectlegs(every_link)
		elif url_parsed.netloc == 'naughtylegs.tumblr.com' or url_parsed.netloc == 'peeptoeheels.tumblr.com' :
			img_link = naughtylegs(every_link)
		elif url_parsed.netloc == 'closetheels.tumblr.com' :
			img_link = closetheels(every_link)
		elif url_parsed.netloc == 'high-heels-forever.tumblr.com' :
			img_link = highheelsforever(every_link)
		elif url_parsed.netloc == 'tuneman86.tumblr.com' or url_parsed.netloc == 'sluttybimbogirl.tumblr.com' \
		or url_parsed.netloc == 'artandsexy.tumblr.com' :
			img_link = tuneman86(every_link)
		elif url_parsed.netloc == 'bestcelebritylegs.tumblr.com' :
			img_link = bestcelebritylegs(every_link)   
		elif url_parsed.netloc == 'e-v-i-l-f-u-c-k-e-r.tumblr.com' :
			img_link = evil(every_link)
		elif url_parsed.netloc == 'sexy-on-heels.tumblr.com' :
			img_link = sexyonheels(every_link)
		elif url_parsed.netloc == 'addicttosex.tumblr.com' :
			img_link = addicttosex(every_link)
		elif url_parsed.netloc == 'icelegsandperspectives.tumblr.com':
			img_link = nicelegsandperspectives(every_link)
		elif url_parsed.netloc == 'haawheels.tumblr.com':
			img_link = haawheels(every_link)
		elif url_parsed.netloc == 'heelhunter.tumblr.com':
			img_link = heelhunter(every_link)
		elif url_parsed.netloc == 'mejeej.tumblr.com':
			img_link = mejeej(every_link)
		elif url_parsed.netloc == 'stilettocouture.tumblr.com':
			img_link = stilettocouture(every_link)            
		elif url_parsed.netloc == 'goodmission.tumblr.com':
			img_link = goodmission(every_link)
		else:
			logr( every_link )
			img_link = 'error'
		if img_link != 'error' and not re.match('^avatar_.+',img_link.split('/')[-1]) : 
			array_urls.append(img_link)
	return array_urls

def hashmem(im):
	im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
	avg = reduce(lambda x, y: x + y, im.getdata()) / 64.
	return reduce(lambda x, (y, z): x | (z << y),enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),0)

def download_images(url,tumblrblog):  
	global image_counter
	global tot_images
	global page_errors
	global tot_errors
	global imgskiped
	filename = os.path.basename(url)
	sys.stdout.write('Checking ' + url)	
	rows_image_urls = check_db_imageurl(url)
	if len(rows_image_urls) > 0:
		logr('url match')
		return
	try:
		raw_content = requests.get(url,headers=my_headers,timeout=my_timeout,proxies=my_proxies)
		# raw_content = urllib.urlopen(url).read()
	except:
		sys.stdout.write(' error while downloading \n') #
		page_errors += 1
		tot_errors += 1
		return
	# sys.stdout.write('ok')
	try:
		raw_conversion = StringIO(raw_content.content)
		resource_image = Image.open(raw_conversion)
		imghash = hashmem(resource_image)
		rows_images = check_db_imagehash(imghash)
	except:
		sys.stdout.write( ' hash error, image skipped\n' )
		page_errors += 1
		return
	
	if len(rows_images) > 0:
		imgskiped += 1
		logr('image hash match')
		# sys.stdout.write( 'image hash match\n' )
		return
	
	filename = os.path.basename(url)
	save_as = os.path.join(complete_path, filename)

	try:
		image_handle = open(save_as, "w")
		image_handle.write(raw_content.content)
		image_handle.close()
		sys.stdout.write( ' saved' )
	except:
		sys.stdout.write ( '\nerror while saving %s ' + filename + '\n' )
		page_errors += 1
		tot_errors += 1
		return
	dbfd_uri = save_as.replace('/mnt/vol1/','')
	dbfd_pstar = dbfd_uri.split('/')[2]
	img_height,img_width = get_img_size(save_as)
	is_portrait = is_img_portrait(img_height,img_width)
	sample_timestamp = str(os.path.getmtime(save_as)).split('.')[-0]
	rec_img_indb(dbconn_smp,dbfd_uri,dbfd_pstar,img_height,img_width,is_portrait,sample_timestamp)
	rec_link(url, urlparse(tumblrblog).netloc, imghash)
	sys.stdout.write( ' inserted into db\n' )
	image_counter += 1
	tot_images += 1
	return

def bot(url_list,opt_proxy,random_mode,target_url,debug):
	script_start = timer()
	global complete_path
	global tumblrblog
	# global image_link
	global dbconn_tumblr
	global dbconn_smp
	global debug_app
	global my_proxies
	global my_headers
	global my_timeout
	global site_errors
	global image_counter
	global tot_images
	global page_errors
	global tot_errors
	global imgskiped
	global parse_only
	debug_app = debug
	if opt_proxy == 'none':
		my_proxies = {}
	else:
		my_proxies = {"http" : opt_proxy }
	start_path = '/mnt/vol1/crawler/crawler.4/'
	credentials_path = os.path.join(work_folder,'api_settings', 'config')
	user_agent_string = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'
	my_headers = {'User-Agent' : user_agent_string , 
				  'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' , 
				  'Accept-Language' : 'en-US,en;q=0.5' ,
				  'Accept-Encoding' : 'gzip, deflate' ,
				  'Referer': "http://www.tumblr.com" }

	my_timeout = 10
	image_counter = 0
	tot_images = 0
	tot_errors = 0
	imgskiped = 0
	max_pages_per_blog = 99
	max_images_per_page = 999999
	sleep_time = 5
	site_errors = []
	# Database Connection Setup
	db_server  = 'prometheus'
	(db_user,db_pass) = load_config(credentials_path)['databases'][db_server]
	dbconn_tumblr = MySQLdb.connect(host=db_server,user=db_user,passwd=db_pass,db='tumblr')
	dbconn_smp = MySQLdb.connect(host=db_server,user=db_user,passwd=db_pass,db='samplesdb')
	dbconn_tumblr.autocommit(True)
	dbconn_smp.autocommit(True)
	###########################
	img_pattern = re.compile('.+\.(jpg|png|gif)$')
	today = datetime.datetime.now()
	if target_url != 'none':
		sites_list = [target_url]
	else:
		sites_list = open(url_list).read()
		sites_list = [ line for line in sites_list.split('\n') if re.match('^http://.+', line) ]
	for tumblrblog in sites_list:
		page_counter = 1
		image_counter = 1
		complete_path = start_path + str(urlparse(tumblrblog).hostname)
		ensure_dir(complete_path)
		lista_paginas = get_url_archives(tumblrblog)
		if len(lista_paginas) == 0:
			continue
		for pagina in lista_paginas:                        #url archive pages by month       
			parsed_obj = urlparse(pagina)
			url_path = parsed_obj.path
			url_path_split = url_path.split('/')    
			url_year = url_path_split[2]
			url_month = url_path_split[3]
			if (str(today.month) == url_month) and (str(today.year) == url_year):
				pass
			else:
				rows_pages = check_db_page(pagina)
				if len(rows_pages) > 0:
					logr('page match')
					continue                                
			logr( 'Looking at Page %s ...' % pagina )
			page_errors = 0
			logr( 'Getting list of urls' )
			list_image_links = find_image_urls(pagina)	
			for image_link in list_image_links:
				download_images(image_link,tumblrblog)
				if image_counter > max_images_per_page:
					break
			if page_errors == 0:
				rec_page(pagina)
			page_counter += 1
			time.sleep(sleep_time)
			if page_counter > max_pages_per_blog:
				page_counter -= 1
				logr( 'Reached max number of %s blog pages for %s' % (page_counter, tumblrblog) )
				break 
	dbconn_tumblr.close()
	dbconn_smp.close()
	elapsed_time = timer() - script_start
	# logr("I've done my job!")
	bot_summary('tumblrbot',tot_images,tot_errors,imgskiped,elapsed_time)


if __name__ == '__main__':
		parser = argparse.ArgumentParser(prog='tumblrbot.py' , description='Tumblr Image Downloader')
		parser.add_argument('-x' , '--proxy', nargs='?', const='dynamic' , default='none')
		parser.add_argument('-d' , '--debug_app', action="store_true", help=("prints debug messages"))
		parser.add_argument('-u' , '--url', nargs='?', const='dynamic' , default='none')
		parser.add_argument('-f' , '--file' , nargs='?', const='dynamic' , default='./curated_urls')
		parser.add_argument("-r", "--random", action="store_true", help=("randomizes  playlist"))
		args = parser.parse_args()
		if os.path.isfile(args.file) or re.match(r'^http://.+\.',args.url) :
			bot(args.file,args.proxy,args.random,args.url,args.debug_app)
		else:
			logr('not a valid download_list file or url')