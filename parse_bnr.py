#!/usr/bin/python


import sys
import json
import urllib2
import time

lastId = ""

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


def waitForNotification(type, data, timeout): 
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

waitForNotification("VOLUME",0,5)