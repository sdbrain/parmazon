'''
Created on Jul 6, 2011

@author: fisheye
'''
import sys
from parser import AmzParser
from downloader import Downloader

if len(sys.argv) < 2:
    print "crap u dude...give some file name"
    sys.exit(2)

#file name
amz = sys.argv[1]
base_dir = "/home/fisheye/Music/Amazon"

#parse the amz file
amzpar = AmzParser()
amzpar.parse(amz)

#get the parsed data in tuples
songs = amzpar.parsed_objects

print "%i songs are going to be downloaded now" % len(songs)

#now pass it to the downloader and
#sip some green tea..:D
dwnldr = Downloader(base_dir, songs,5)
dwnldr.downloadfiles()
