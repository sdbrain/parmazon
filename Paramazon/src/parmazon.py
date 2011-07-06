'''
Created on Jul 6, 2011

@author: fisheye
'''
from subprocess import Popen
from subprocess import PIPE
import sys


if len(sys.argv) < 2:
    print "crap u dude...give some file name"
    sys.exit(2)

#file name
amz = sys.argv[1]
