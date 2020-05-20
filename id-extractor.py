import xml.etree.ElementTree as etree
import codecs
import csv
import time
import os

PATH_WIKI_XML = '/mnt/d/Experiment/'
FILENAME_WIKI = 'wikidump.xml'
FILENAME_ARTICLES = 'articles.csv'
FILENAME_REDIRECT = 'articles_redirect.csv'
FILENAME_TEMPLATE = 'articles_template.csv'
ENCODING = "utf-8"


# Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def strip_tag_name(t):
    t = elem.tag
    idx = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t


pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)
pathArticles = os.path.join(PATH_WIKI_XML, FILENAME_ARTICLES)
pathArticlesRedirect = os.path.join(PATH_WIKI_XML, FILENAME_REDIRECT)

totalCount = 0
articleCount = 0
redirectCount = 0
templateCount = 0
title = None
start_time = time.time()

with open(pathWikiXML, 'r+') as f:
    line = "<root>"
    content = f.read()
    f.seek(0, 0)
    f.write(line + '\n' + content)

with open(pathWikiXML, 'a') as f:
    line = "</root>"
    f.write(line)

with codecs.open(pathArticles, "a", ENCODING) as articlesFH, \
        codecs.open(pathArticlesRedirect, "a", ENCODING) as redirectFH:
    articlesWriter = csv.writer(articlesFH, quoting=csv.QUOTE_MINIMAL)
    redirectWriter = csv.writer(redirectFH, quoting=csv.QUOTE_MINIMAL)

   # articlesWriter.writerow(['id', 'title'])
   # redirectWriter.writerow(['id', 'title', 'redirect'])

    for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
        
        tname = strip_tag_name(elem.tag)

        if event == 'start':
            if tname == 'page':
                title = ''
                id = -1
                redirect = ''
                inrevision = False
                ns = 0
            elif tname == 'revision':
                # Do not pick up on revision id's
                inrevision = True
        else:
            if tname == 'title':
                title = elem.text
            elif tname == 'id' and not inrevision:
                id = int(elem.text)
            elif tname == 'redirect':
                redirect = elem.attrib['title']
            elif tname == 'ns':
                ns = int(elem.text)
            elif tname == 'page':
                totalCount += 1

                if ns == 10:
                    templateCount += 1
                    # ignoring templates
                elif len(redirect) > 0:
                    redirectCount += 1
                    redirectWriter.writerow([id, title, redirect])
                else:
                    articleCount += 1
                    articlesWriter.writerow([id, title])

                if totalCount > 1 and (totalCount % 100000) == 0:
                    print("{:,}".format(totalCount))

            elem.clear()

"""
elapsed_time = time.time() - start_time

print("Total pages: {:,}".format(totalCount))
print("Template pages: {:,}".format(templateCount))
print("Article pages: {:,}".format(articleCount))
print("Redirect pages: {:,}".format(redirectCount))
print("Elapsed time: {}".format(hms_string(elapsed_time)))
"""
