import json
import urllib2
import re
import os

class Cloner(object):
    def __init__(self, url, path):
        self.start_url = url
        self.path = os.getcwd() + "/" + path
        self.user_agent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)"

    # ######################################3
    # Utility Functions
    # ######################################3
    
    def get_url(self, url):
        headers = { 'User-Agent' : self.user_agent }
        try:
            req = urllib2.Request(url, None, headers)
            return urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            print 'We failed with error code - %s.' % e.code
            if e.code == 404:
                return ""
            else:
                return ""

    def download_binary(self, url):
        filename = ""
        if url.startswith(self.start_url):
            filename = url[len(self.start_url):]
        else:
            return
       
        data = self.get_url(url)
        if (data == ""):
            return
        self.writeoutfile(data, filename)
        return

    def writeoutfile(self, data, filename):
        if filename.startswith("/"):
            filename = filename[1:]
        
        fullfilename = self.path + "/" + filename
        if not os.path.exists(os.path.dirname(fullfilename)):
            os.makedirs(os.path.dirname(fullfilename))

        print "WRITING OUT FILE    [%s]" % (filename)

        f = open(fullfilename, 'a')
        f.write(data)
        f.close()        

    def unique_list(self, old_list):
        new_list = []
        if old_list != []:
            for x in old_list:
                if x not in new_list:
                    new_list.append(x)
        return new_list

    # ######################################3
    # html and link processing functions
    # ######################################3
    
    def process_links(self, links):
        new_links = []
        for link in links:
            if (link.endswith(".css")  or 
                link.endswith(".js")   or
                link.endswith(".ico")  or
                link.endswith(".png")  or
                link.endswith(".jpg")  or
                link.endswith(".jpeg") or
                link.endswith(".bmp")  or
                link.endswith(".gif")
               ):
                new_links.append(link)
        return new_links
    
    def clone(self, url="", base=""):
        if (url == ""):
            url = self.start_url

        if (base == ""):
            base = self.start_url

        html = self.get_url(url)
        if (html == ""):
            return

        filename = ""
        if url.startswith(base):
            filename = url[len(base):]
            if (filename == ""):
                filename = "index.html"
        else:
            print "BAD URL             [%s]" % (url)
            return

        print "CLONING URL         [%s]" % (url)

        # find links
        links = re.findall(r"<link.*?\s*href=\"(.*?)\".*?>", html)
        links += re.findall(r"<script.*?\s*src=\"(.*?)\".*?>", html)
        links += re.findall(r"<img.*?\s*src=\"(.*?)\".*?>", html)
        links += re.findall(r"\"(.*?)\"", html)
        links += re.findall(r"url(\"(.*?)\");", html)

        links = self.process_links(self.unique_list(links))

        # loop over the links
        for link in links:
            new_link = link
            if link.lower().startswith("http"):
                new_link = link
            elif link.startswith("/"):
                new_link = base + link
            elif link.startswith("../"):
                new_link = base + "/" + link[3:]
            else:
                new_link = base + "/" + link

            print "FOUND A NEW LINK    [%s]" % (new_link)
    
            # switch out new_link for link
            html = html.replace("\"" + link + "\"", "\"" + new_link + "\"")

            # handle "../" properly
            # recursively call process_html on each non-image link

            if (link.endswith(".css")  or
                link.endswith(".js")
               ):
                if base != self.start_url:
                    self.clone(url=new_link, base=os.path.dirname(url))
                else:
                    self.clone(url=new_link)
            else:
                self.download_binary(new_link)
  
        self.writeoutfile(html, filename)
        return
        
c = Cloner("http://www.exploitsearch.net", "clonedsite")
c.clone()
