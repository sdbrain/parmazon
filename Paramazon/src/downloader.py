import pycurl
import os
import stat

'''
Created on Jul 6, 2011

@author: fisheye
'''

class Downloader:
    '''
        Downloads the list of songs provided in
        a highly parallelized fashion...
    '''
    def __init__(self,base_dir, songlist, num_conn=5):
        self.songlist = songlist
        self.num_conn = num_conn
        self.base_dir = base_dir

    def downloadfiles(self):
        """
            Download the file using pycurl
        """
        num_urls = len(self.songlist)
        num_conn = min(self.num_conn, num_urls)
        # Pre-allocate a list of curl objects
        m = pycurl.CurlMulti()
        m.handles = []
        for i in range(self.num_conn):
            c = pycurl.Curl()
            c.fp = None
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT, 30)
            c.setopt(pycurl.TIMEOUT, 300)
            c.setopt(pycurl.NOSIGNAL, 1)
            m.handles.append(c)


        # Main loop
        freelist = m.handles[:]
        num_processed = 0
        while num_processed < num_urls:
            # If there is an url to process and a free curl object, add to multi stack
            while self.songlist and freelist:
                song = self.songlist.pop(0)
                url = song[0].encode("utf-8")

                #create the album dirs
                path = "%s/%s" %(self.base_dir, song[1])
                if not os.path.exists(path):
                    os.makedirs(path)

                filename = "%s/%s.mp3" % (path, song[2])

                c = freelist.pop()

                #progress meter does not take the
                #already downloaded size into consideration
                basesize = 0
                #file download resume logic
                if(os.path.exists(filename)):
                    remaining = long(song[3])- os.path.getsize(filename)
                    print "resuming download of %s...remaining %s" % (filename,
                            format_number(remaining))
                    offset = os.stat(filename)[stat.ST_SIZE]
                    basesize = offset
                    c.setopt(pycurl.RESUME_FROM, offset)
                else:
                    print "going to download %s" % filename

                c.fp = open(filename, "ab")
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.NOPROGRESS, 0)
                prg = Progress(song[2], basesize)
                c.setopt(pycurl.PROGRESSFUNCTION, prg.progress)
                c.setopt(pycurl.WRITEDATA, c.fp)
                # store some info
                c.filename = song[2]
                c.url = url
                m.add_handle(c)
            # Run the internal curl state machine for the multi stack
            while 1:
                ret, num_handles = m.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            # Check for curl objects which have terminated, and add them to the freelist
            while 1:
                num_q, ok_list, err_list = m.info_read()
                for c in ok_list:
                    c.fp.close()
                    c.fp = None
                    m.remove_handle(c)
                    print "Download complete:", c.filename
                    freelist.append(c)
                for c, errno, errmsg in err_list:
                    c.fp.close()
                    c.fp = None
                    m.remove_handle(c)
                    print "Failed: ", c.filename , errno, errmsg
                    freelist.append(c)
                num_processed = num_processed + len(ok_list) + len(err_list)
                if num_q == 0:
                    break
            # Currently no more I/O is pending, could do something in the meantime
            # (display a progress bar, etc.).
            # We just call select() to sleep until some more data is available.
            m.select(1.0)


        # Cleanup
        for c in m.handles:
            if c.fp is not None:
                c.fp.close()
                c.fp = None
            c.close()
        m.close()

class Progress:

    def __init__(self, filename, basesize):
        self.filename = filename
        self.basesize = basesize

    ## Callback function invoked when download/upload has progress
    def progress(self, download_t, download_d, upload_t, upload_d):
        print "%s downloaded of %s - %s" % (format_number(self.basesize+download_d), format_number(self.basesize+download_t) , self.filename)

# Borrowed from the urlgrabber source
def format_number(number, SI=0, space=' '):
    """Turn numbers into human-readable metric-like numbers"""
    symbols = ['',  # (none)
               'k', # kilo
               'M', # mega
               'G', # giga
               'T', # tera
               'P', # peta
               'E', # exa
               'Z', # zetta
               'Y'] # yotta

    if SI: step = 1000.0
    else: step = 1024.0

    thresh = 999
    depth = 0
    max_depth = len(symbols) - 1

    # we want numbers between 0 and thresh, but don't exceed the length
    # of our list.  In that event, the formatting will be screwed up,
    # but it'll still show the right number.
    while number > thresh and depth < max_depth:
        depth  = depth + 1
        number = number / step

    if type(number) == type(1) or type(number) == type(1L):
        # it's an int or a long, which means it didn't get divided,
        # which means it's already short enough
        format = '%i%s%s'
    elif number < 9.95:
        # must use 9.95 for proper sizing.  For example, 9.99 will be
        # rounded to 10.0 with the .1f format string (which is too long)
        format = '%.1f%s%s'
    else:
        format = '%.0f%s%s'

    return(format % (float(number or 0), space, symbols[depth]))
