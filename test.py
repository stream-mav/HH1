#!/usr/bin/python2.7

from pexpect import pxssh
import urllib, json
import getpass
import ConfigParser

name_config = 'config'
global ip_addr_hh
global ip_addr


#################################################
#init
def init():
	
	global s
	global configParser

	# OPEN confige file
	configParser = ConfigParser.RawConfigParser()
	configFilePath = name_config
	configParser.read(configFilePath)

	ip_addr = configParser.get('server', 'ip')
	ip_addr_hh = configParser.get('server', 'ip_hh')

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

def compare_json(file1, file2):
	with open(file1) as outfile1:
		data1 = json.load(outfile1)

	with open(file2) as outfile2:
		data2 = json.load(outfile2)

	for x in range(0, len(data,['trackList']['track'])):
		if(data1,['trackList']['track'][x]['artistNameNormalized'] == data2,['trackList']['track'][x]['artistNameNormalized']):
			print('zhoda data '+ x)


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

#################################################

init()
#create_link()
#add_remove('step1')
readJson()



s.logout()
