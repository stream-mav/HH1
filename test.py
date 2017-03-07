#!/usr/bin/python2.7

################################
#
# read list from server, and searching 
# difference betweet server and template
#
################################

from pexpect import pxssh
import urllib, json
import getpass
import ConfigParser

name_config = 'config'
global ip_addr_hh
global ip_addr

import sys
import json
import urllib2
import time

lastId = ""

########################################################
def iterload(url):
	print("=== fetching " + url + " ===")
	try:
		handle = urllib2.urlopen(url)
	except:
		raise Exception("unable to open");
		return

	buffer = ""
	dec = json.JSONDecoder()

	while(True):
		try:
			line = handle.read(1)
			if len(line)==0:
				return
		except:
			print("== unable to read")
			raise Exception("unable to read")
			return

		# print(line)
		buffer = buffer.strip(" \n\r\t") + line.strip(" \n\r\t")
		while(True):
			try:
				r = dec.raw_decode(buffer)
			except:
				break
			yield r[0]
			buffer = buffer[r[1]:].strip(" \n\r\t")

################################
# reading notifications from HH1
#  and return searched notification
def waitForNotification(type, data, timeout):
	# todo replace hardcoded ip
	url = "http://192.168.1.137:8080/BeoNotify/Notifications"
	start = time.time()
	end = 0


	while(True):
		try:
			if (end == 1):
				break

			for o in iterload(url + lastId):
				n = o["notification"];
				if (n.has_key("id")):
					lastId = "?lastId=" + str(n["id"])

				# VYPIS	
				if (n["type"] == type):				
					print(n["timestamp"] + ": " + n["type"] + ": " + json.dumps(n["data"]))	

				# ZAPIS PLAY/ STOP STATUS
				f = open('workfile', 'a')

				if(n["type"].find("PROGRESS_INFORMATION") > -1):
					if( (json.dumps(n["data"]["state"]).find("play")) > -1):
						f.write("1")
					else:
						f.write("0")
				f.close()	

				# Check time
				if ( time.time()-start > timeout):
					end = 1
					break		

		except:
			lastId = ""
			time.sleep(1)

#################################################
# initialization connection at server, IP address
def init():
	
	global s
	global configParser

	# OPEN confige file
	configParser = ConfigParser.RawConfigParser()
	configFilePath = name_config
	configParser.read(configFilePath)

	ip_addr = configParser.get('server', 'ip')
	ip_addr_hh = configParser.get('server', 'ip_hh1')

	# OPEN SSH
	try:
	    s = pxssh.pxssh()
	    s.login(
	    	ip_addr, 
	    	configParser.get('server', 'login'), 
	    	configParser.get('server', 'pass')
	    	)
	    
	except pxssh.ExceptionPxssh, e:
	    print "pxssh failed on login."
	    print str(e)

	# change PATH
	s.sendline('cd ' + configParser.get('server', 'path'))
	s.prompt()

##############
# remove/ add links
def add_remove(step_name):
	add = configParser.get(step_name, 'add[]').split('\n')
	rem = configParser.get(step_name, 'del[]').split('\n')
	
	for x in range(0, len(add)):
		s.sendline("ln -ns \"/volume1/music/Kenni's music/Seagate Expansion Drive/music/collection/"+add[x]+"\" -t .")
		s.prompt()

	for x in range(0, len(rem)):
		s.sendline('rm ' + '"' + rem[x] + '"') 
		s.prompt()


##############
# create links
def create_link():
	s.sendline("ln -ns \"/volume1/music/Kenni's music/Seagate Expansion Drive/music/collection/\"* -t .")
	s.prompt()

##############
# delete ID from url links
def del_id(str1):
	# find '\' in url
	position_last = -1
	if ( str1.find('gracenote') == -1):
		position_last = str1.rfind('/')

	if(position_last > -1):
		return str1[0:position_last+1] 

	return -1

def del_ids(inx):
	try:
		tmp = del_id(data['trackList']['track'][inx]['artist'][0]['image'][0]['url']) 
		if( tmp > -1):
			data['trackList']['track'][inx]['artist'][0]['image'][0]['url'] = tmp
	except:
		pass

	try:
		tmp = del_id(data['trackList']['track'][inx]['image'][0]['url']) 
		if( tmp > -1):
			data['trackList']['track'][inx]['image'][0]['url'] = tmp
	except:
		pass	

	try:
		tmp = del_id(data['trackList']['track'][inx]['parentAlbum']['image'][0]['url']) 
		if( tmp > -1):
			data['trackList']['track'][inx]['parentAlbum']['image'][0]['url'] = tmp
	except:
		pass		

##############
# compare two JSON, return add or delete track index - name, artis, album
def compare_json_names():
	for ind_1 in range(len(data1['trackList']['track'])):
		err = 1
		for ind_2 in range(len(data2['trackList']['track'])):
			if((data1['trackList']['track'][ind_1]['artist'][0]['name'] == data2['trackList']['track'][ind_2]['artist'][0]['name']) and
				(data1['trackList']['track'][ind_1]['name'] == data2['trackList']['track'][ind_2]['name']) and
				(data1['trackList']['track'][ind_1]['parentAlbum']['name'] == data2['trackList']['track'][ind_2]['parentAlbum']['name'])):
				err = 0
		if(err):
			print('=== ADD ID: ' + str(ind_1) )
			print('Artis: ' + data1['trackList']['track'][ind_1]['artist'][0]['name'])
			print('Name: ' + data1['trackList']['track'][ind_1]['name'])
			print('Album: ' + data1['trackList']['track'][ind_1]['parentAlbum']['name'])

	for ind_2 in range(len(data2['trackList']['track'])):
		err = 1
		for ind_1 in range(len(data1['trackList']['track'])):
			if((data2['trackList']['track'][ind_2]['artist'][0]['name'] == data1['trackList']['track'][ind_1]['artist'][0]['name']) and
				(data2['trackList']['track'][ind_2]['name'] == data1['trackList']['track'][ind_1]['name']) and
				(data2['trackList']['track'][ind_2]['parentAlbum']['name'] == data1['trackList']['track'][ind_1]['parentAlbum']['name'])):
				err = 0
		if(err):
			print('=== DEL ID: ' + str(ind_2) )
			print('Artis: ' + data1['trackList']['track'][ind_1]['artist'][0]['name'])
			print('Name: ' + data1['trackList']['track'][ind_1]['name'])
			print('Album: ' + data1['trackList']['track'][ind_1]['parentAlbum']['name'])


##############
# compare two JSON databases, first find correct index database 1 with database 2
# after find difference betweet databases
def compare_json():

	array_ind = [None] * len(data1['trackList']['track'])

	for ind_1 in range(len(data1['trackList']['track'])):
		for ind_2 in range(len(data2['trackList']['track'])):
			if((data1['trackList']['track'][ind_1]['artist'][0]['name'] == data2['trackList']['track'][ind_2]['artist'][0]['name']) and
				(data1['trackList']['track'][ind_1]['name'] == data2['trackList']['track'][ind_2]['name']) and
				(data1['trackList']['track'][ind_1]['parentAlbum']['name'] == data2['trackList']['track'][ind_2]['parentAlbum']['name'])):
					array_ind[ind_1] = ind_2
					break

	for x in range(len(array_ind)):	
		if(array_ind[x] == None):
			continue
		if( compareParsedJson(data1['trackList']['track'][x], data2['trackList']['track'][array_ind[x]]) == False):
			print('Track id = ' + str(x))

##############
# recursive function for compare_json()
def compareParsedJson(example_json, target_json):   

	if( (type(example_json) == int) or (type(example_json) == unicode) or (type(example_json) ==bool) ):
		if(example_json == target_json):
			return True
		else:
			print('example: ' + example_json )
			print('target: ' + target_json)
			return False

	for x in example_json:	
		try:
			if(compareParsedJson(example_json[x], target_json[x]) == False):
				return False
		except:
			try:
				if(compareParsedJson(example_json[0], target_json[0]) == False):
					return False
			except:
				pass

	return True


##############
# filtering JSON databae (delete ID, delete links)
def readJson():
	jsonurl = "http://192.168.1.177:8080/BeoContent/music/dlnaProfile/track/"
	response = urllib.urlopen(jsonurl)
	global data 
	data = json.loads(response.read())

	# delete ID and ID img
	size = len(data['trackList']['track'])
	for index in range(0, size): 
		data['trackList']['track'][index]['id']=""
		data['trackList']['track'][index]['artist'][0]['id']="" 
		data['trackList']['track'][index]['artist'][0]['dlna']['id']="" 
		data['trackList']['track'][index]['parentAlbum']['id']="" 
		data['trackList']['track'][index]['parentAlbum']['dlna']['id']="" 
		data['trackList']['track'][index]['dlna']['id']="" 
		del data['trackList']['track'][index]['_links']
		del_ids(index)

	with open('data.json', 'w') as outfile:
		json.dump(data, outfile)

		compare_json('data1.json','data2.json')

##############
# read JSON databases
def read_file(file1, file2):
	global data1, data2

	with open(file1) as outfile1:
		data1 = json.load(outfile1)

	with open(file2) as outfile2:
		data2 = json.load(outfile2)

#################################################

read_file('data1.json','data2.json')
compare_json()
compare_json_names()
