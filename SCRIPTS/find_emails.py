#!/usr/bin/env python
import urllib2
import re
import sys

def unique_list(old_list):
    new_list = []
    if old_list != []:
        for x in old_list:
            if x not in new_list:
                new_list.append(x)
    return new_list

def parse_emails(text, domain):
    reg_emails = re.compile('[a-zA-Z0-9\.\-_]+@[a-zA-Z0-9\.\-]*' + domain)
    return reg_emails.findall(text)

def email_search(url, domain, user_agent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)", offset=1, maxoffset=0):
    all_emails = []
    current_offset = 0
    data = None
    while current_offset <= maxoffset:
        temp_url = re.sub(r'\[\[OFFSET\]\]', str(current_offset), url)
        try:
            headers = { 'User-Agent' : user_agent }
            req = urllib2.Request(temp_url, None, headers)
            data = urllib2.urlopen(req).read()
        except Exception, e:
            print e
        all_emails += parse_emails(data, domain)
        current_offset += offset
    return all_emails


def gather(domain, maxoffset=500):
    # Currently searches [google, bing, ask, dogpile, yandex, baidu, yahoo]
    # There is currently an issue with duckduckgo
    all_emails = []

    all_emails += email_search(url="http://www.google.com/search?num=100&start=[[OFFSET]]&hl=en&meta=&q=%40\"" + domain + "\"", domain=domain, offset=100, maxoffset=maxoffset)
    all_emails += email_search(url="http://www.bing.com/search?q=" + domain + "&count=50&first=[[OFFSET]]", domain=domain, offset=50, maxoffset=maxoffset)
    all_emails += email_search(url="http://www.ask.com/web?q=%40" + domain + "&pu=100&page=[[OFFSET]]", domain=domain, offset=100, maxoffset=maxoffset)
    all_emails += email_search(url="http://www.dogpile.com/search/web?qsi=[[OFFSET]]&q=\"%40" + domain + "\"", domain=domain, offset=10, maxoffset=maxoffset/10)
    all_emails += email_search(url="http://www.yandex.com/search?text=%40" + domain + "&numdoc=50&lr=[[OFFSET]]", domain=domain, offset=50, maxoffset=maxoffset)
    all_emails += email_search(url="http://www.baidu.com/s?wd=%40" + domain + "&pn=[[OFFSET]]", domain=domain, offset=10, maxoffset=maxoffset/10)
    all_emails += email_search(url="https://search.yahoo.com/search?p=\"%40" + domain + "\"&b=[[OFFSET]]&pz=10", domain=domain, offset=10, maxoffset=maxoffset/10)
    all_emails += email_search(url="https://duckduckgo.com/html?q=\"%40" + domain + "\"", domain=domain)
    all_emails += email_search(url="https://duckduckgo.com/lite?q=\"%40" + domain + "\"", domain=domain)

    return unique_list(all_emails)

if __name__ == "__main__":
    print gather("example.com")
