#!/usr/bin/python3
import json
import re
from urllib.request import urlopen
from urllib.parse import quote_plus as ursafe
import random
import string
import hashlib
import xml.etree.ElementTree as ET
from thefuzz import fuzz
from datetime import datetime
import os

if not os.path.exists("./.subsonic_creds"):
	if not os.path.exists(os.getenv("HOME")+"/.subsonic_creds"):
		print("No credentials file exists")
		quit(1);
	else:
		CRED=os.getenv("HOME")+"/.subsonic_creds"
else:
	CRED="./.subsonic_creds"
		
f = open(CRED, "r")
user=f.readline().strip()
passa=f.readline().strip()
subsonic=f.readline().strip()
lbuser=f.readline().strip()


salt='%030x' % random.randrange(16**30)
cram=passa+salt
token=hashlib.md5(cram.encode()).hexdigest()
print(salt+"\n"+token)
songs2add=[]


url = "https://api.listenbrainz.org/1/user/"+lbuser+"/playlists/createdfor" #URL for playlists generated for your user by LB
data = urlopen(url)
playlists = json.loads(data.read())
for playlist in playlists["playlists"]:
    if playlist["playlist"]["extension"]["https://musicbrainz.org/doc/jspf#playlist"]["additional_metadata"]["algorithm_metadata"]["source_patch"] == "weekly-jams":
        result=playlist["playlist"]["identifier"]
        plsplit=re.split('/',result)
        pl=plsplit[len(plsplit)-1]
        url = "https://api.listenbrainz.org/1/playlist/"+pl
        data = urlopen(url)
        lb_playlist = json.loads(data.read())
        break


plcdate=datetime.strptime(re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}",lb_playlist["playlist"]["date"]).group(), "%Y-%m-%d").strftime("%Y-%m-%d")
plname="LB "+plcdate

url = subsonic+"/rest/getPlaylists?u="+user+"&s="+salt+"&t="+token+"&v=1.15.0&c=python&username="+user
data = urlopen(url)
airsonicplaylists = ET.fromstring(data.read())
apl = airsonicplaylists[0]
for potpl in apl:
    if potpl.attrib["name"] == plname:
        print("playlist exists, quitting")
        quit()

songlist=lb_playlist["playlist"]["track"]
for song in songlist:
    result=song['creator']+" - "+song['title']
    url = subsonic+"/rest/search3?u="+user+"&s="+salt+"&t="+token+"&v=1.15.0&c=python&query="+ursafe(result)+"&artistCount=0&albumCount=0&songCount=1&musicFolderId=0"
    data = urlopen(url)
    search = ET.fromstring(data.read())
    searchj = search[0][0].attrib
    subguess=searchj["artist"]+" - "+searchj["title"]
    fratio=fuzz.ratio(result, subguess)
    if fratio != 100:
        ftrratio=fuzz.token_sort_ratio(result, subguess)
        fteratio=fuzz.token_set_ratio(result,subguess)
        fpratio=fuzz.partial_ratio(result,subguess)
        if ( fratio + ftrratio + fteratio + fpratio ) /4 > 75:
            sid=searchj["id"]
            songs2add.append(sid)
    else:
        sid=searchj["id"]
        songs2add.append(sid)


url = subsonic+"/rest/createPlaylist?u="+user+"&s="+salt+"&t="+token+"&v=1.15.0&c=python&name="+ursafe(plname)
data = urlopen(url)

url = subsonic+"/rest/getPlaylists?u="+user+"&s="+salt+"&t="+token+"&v=1.15.0&c=python&username="+user
data = urlopen(url)
airsonicplaylists = ET.fromstring(data.read())
apl = airsonicplaylists[0]
for potpl in apl:
    if potpl.attrib["name"] == plname:
        plid = potpl.attrib["id"]
try:
    for addsong in songs2add:
        url = subsonic+"/rest/updatePlaylist?u="+user+"&s="+salt+"&t="+token+"&v=1.15.0&c=python&playlistId="+plid+"&songIdToAdd="+addsong
        data = urlopen(url)

except:
    quit()
