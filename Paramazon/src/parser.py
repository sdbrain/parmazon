"""
Pymazon - A Python based downloader for the Amazon.com MP3 store
Copyright (c) 2010 Steven C. Colbert

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from collections import defaultdict
from xml.parsers import expat

from decryptor import AmzDecryptor

class ParseException(Exception):
    pass


class AmzParser(object):
    def __init__(self):
        self.parser = None
        self.parsed_objects = []
        self.current_track = None
        self.in_tracklist = False
        self.now_url = False
        self.now_artist = False
        self.now_album = False
        self.now_title = False
        self.now_image = False
        self.now_tracknum = False
        self.now_filesize = False
        self.now_tracktype = False

    def start_element(self, name, attrs):
        if name == 'trackList':
            self.in_tracklist = True
        if self.in_tracklist:
            if name == 'track':
                self.current_track = defaultdict(str)
            elif name == 'location':
                self.now_url = True
            elif name == 'creator':
                self.now_artist = True
            elif name == 'album':
                self.now_album = True
            elif name == 'title':
                self.now_title = True
            elif name == 'image':
                self.now_image = True
            elif name == 'trackNum':
                self.now_tracknum = True
            elif name == 'meta':
                if attrs['rel'].endswith('fileSize'):
                    self.now_filesize = True
                elif attrs['rel'].endswith('trackType'):
                    self.now_tracktype = True

    def end_element(self, name):
        if name == 'trackList':
            self.in_tracklist = False
        if self.in_tracklist:
            if name == 'track':
                self.add_track()
            elif name == 'location':
                self.now_url = False
            elif name == 'creator':
                self.now_artist = False
            elif name == 'album':
                self.now_album = False
            elif name == 'title':
                self.now_title = False
            elif name == 'image':
                self.now_image = False
            elif name == 'trackNum':
                self.now_tracknum = False
            elif name == 'meta':
                if self.now_filesize:
                    self.now_filesize = False
                elif self.now_tracktype:
                    self.now_tracktype = False

    def character_data(self, data):
        if self.now_url:
            self.current_track['url'] += data
        elif self.now_artist:
            self.current_track['artist'] += data
        elif self.now_album:
            self.current_track['album'] += data
        elif self.now_title:
            self.current_track['title'] += data
        elif self.now_image:
            self.current_track['image'] += data
        elif self.now_tracknum:
            self.current_track['tracknum'] += data
        elif self.now_filesize:
            self.current_track['filesize'] += data
        elif self.now_tracktype:
            self.current_track['tracktype'] += data

    def add_track(self):
        track = (self.current_track["url"], self.current_track["album"], self.current_track["title"], self.current_track["filesize"])
        self.parsed_objects.append(track)

    def create_new_parser(self):
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.parser.CharacterDataHandler = self.character_data

    def parse(self, amz):
        amz_data = open(amz).read()
        decryptor = AmzDecryptor()
        xml = decryptor.decrypt(amz_data)
        self.create_new_parser()
        self.parser.Parse(xml)

    def get_parsed_objects(self):
        return self.parsed_objects


if __name__ == '__main__':
    p = AmzParser()
    p.parse("/home/fisheye/Music/c.amz")
    print len(p.parsed_objects)


