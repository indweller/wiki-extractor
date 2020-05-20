import xml.etree.ElementTree as etree
import codecs
import csv
import time
import os
import re

PATH_WIKI_XML = '/mnt/d/Experiment/'
FILENAME_WIKI = 'wikidump.xml'
FILENAME_ARTICLES = 'articles.csv'
FILENAME_SURFACE_NAMES = 'surface_names.csv'
FILENAME_SENTENCES = 'sentences.csv'
FILENAME_REDIRECT = 'articles_redirect.csv'
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

def clean_text(text):
    text = _remove_appendices(text)
    text = _remove_file_links(text)
    text = _remove_image_links(text)
    # text = _remove_external_links(text)
    text = _remove_categories(text)
    text = _remove_refs(text)
    text = _remove_emphasises(text)
    text = _remove_comments(text)
    text = _remove_langs(text)
    text = _remove_choices(text)
    text = _remove_templates(text)
    text = _remove_htmls(text)
    text = _remove_lists(text)
    text = _remove_indents(text)
    text = _remove_styles(text)
    text = _remove_spaces(text)
    text = _remove_titles(text)
    text = _remove_continuous_newlines(text)
    return text.strip()

def _remove_appendices(text):
    pattern_list = ['See also', 'References', 'Notes', 'Sources', 'External Links', 'Further reading', 'Works cited'
    'Secondary sources','Citations', 'Bibliography', 'Footnotes', 'Endnotes']
    for pattern in pattern_list:
        if re.search(r'(={2,6})\s*%s\s*\1' % pattern, text, re.IGNORECASE) != None:
            begin = re.search(r'(={2,6})\s*%s\s*\1' % pattern, text, re.IGNORECASE).start()
            text = text[:begin]
    return text

def _remove_categories(text):
    return re.sub(r'\[\[Category\s*(.*?)\s*\]\]', '', text)

def _remove_file_links(text):
    """Remove links like `[[File:*]]`"""
    text = _remove_resource_links(text, 'File')
    text = re.sub(r'^File:.*$', '', text, flags=re.MULTILINE)
    return text

def _remove_image_links(text):
    """Remove links like `[[File:*]]`"""
    return _remove_resource_links(text, 'Image')

def _remove_resource_links(text, resource):
    """Remove links likes `[[*:*]]`"""
    pattern = '[[' + resource + ':'
    pattern_begin = text.find(pattern)
    if pattern_begin == -1:
        return text
    begin, removed = 0, ''
    while begin < len(text):
        if pattern_begin > begin:
            removed += text[begin:pattern_begin]
        pattern_end, depth = pattern_begin + 2, 2
        while pattern_end < len(text):
            ch = text[pattern_end]
            pattern_end += 1
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    break
        if depth == 0:
            begin = pattern_end
        else:
            removed += "[["
            begin += pattern_begin + 2
        pattern_begin = text.find(pattern, begin)
        if pattern_begin == -1:
            break
    if len(text) > begin:
        removed += text[begin:]
    return removed

def _remove_external_links(text):
    """Remove links like [*]"""
    return re.sub(r'\[h[^ ]+ (.*?)\]', r'\1', text)

def _remove_refs(text):
    """Remove patterns like <ref*>*</ref>"""
    text = re.sub(r'<ref[^/]*?/>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<ref.*?</ref>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # text = re.sub(r'{{Refbegin.*?Refend}}', '', text, flags=re.IGNORECASE | re.DOTALL)
    return text

def _remove_emphasises(text):
    """Remove patterns like '''*'''"""
    text = re.sub(r"'''(.*?)'''", r'\1', text, flags=re.DOTALL)
    text = re.sub(r"''(.*?)''", r'\1', text, flags=re.DOTALL)
    return text

def _remove_comments(text):
    """Remove patterns like <!--*-->"""
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

def _remove_langs(text):
    """Remove pattenrs like {{lang-*|*}}}"""
    return re.sub(r'{{lang(-|\|).*?\|(.*?)}}', r'\2', text, flags=re.IGNORECASE | re.DOTALL)

def _remove_titles(text):
    """Remove patterns like ==*=="""
    return re.sub(r'(={2,6})\s*(.*?)\s*\1', '', text)

def _remove_choices(text):
    """Remove patterns like -{zh-hans:*; zh-hant:*}-"""
    text = re.sub(
        r'-{.{,100}?zh(-hans|-cn|-hk|):(.{,100}?)(;.{,100}?}-|}-)',
        r'\2', text,
        flags=re.DOTALL
    )
    text = re.sub(r'-{.{,100}?:(.{,100}?)(;.{,100}?}-|}-)', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'-{(.{,100}?)}-', r'\1', text, flags=re.DOTALL)
    return text

def _remove_templates(text):
    """Remove patterns like {{*}}"""
    begin, removed = 0, ''
    while begin < len(text):
        pattern_begin = text.find('{{', begin)
        if pattern_begin == -1:
            if begin == 0:
                removed = text
            else:
                removed += text[begin:]
            break
        if pattern_begin > begin:
            removed += text[begin:pattern_begin]
        pattern_end, depth = pattern_begin + 2, 2
        while pattern_end < len(text):
            ch = text[pattern_end]
            pattern_end += 1
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    link = text[pattern_begin + 2:pattern_end - 2]
                    parts = link.split('|')
                    template_type = parts[0].split(' ')[0].lower()
                    if len(parts) == 1:
                        if all(map(lambda x: x in {'"', "'", ' '}, parts[0][:])):
                            removed += parts[0].replace(' ', '')
                    elif len(parts) in [2, 3]:
                        if template_type in {'le'} or template_type.startswith('link-'):
                            removed += parts[1]
                    break
        begin = pattern_end
    return removed

def _remove_htmls(text):
    return re.sub(r'<(.*?)>', '', text, flags=re.DOTALL)

def _remove_lists(text):
    return re.sub(r'^\s*[\*#]\s*', '', text, flags=re.MULTILINE)

def _remove_indents(text):
    return re.sub(r'^\s*[:;]\s*', '', text, flags=re.MULTILINE)

def _remove_styles(text):
    return re.sub(r':?{\| (style|class)=.*?\|}', '', text, flags=re.IGNORECASE | re.DOTALL)

def _remove_spaces(text):
    return text.replace('\u200b', '')

def _remove_continuous_newlines(text):
    return re.sub(r'\n{2,}', '\n', text)

def parse_sentence(text):
    pattern = '[['
    pattern_begin = text.find(pattern)
    dest_list = []
    sn_list = []
    if pattern_begin == -1:
        return dest_list, sn_list
    begin, removed = 0, ''
    while begin < len(text):
        if pattern_begin > begin:
            removed += text[begin:pattern_begin]
            # print("removed ", removed)
        pattern_end, depth = pattern_begin + 2, 2
        dest = ''
        sn = ''
        used = False
        while pattern_end < len(text):
            ch = text[pattern_end]
            # print("ch ", ch)
            pattern_end += 1
            if ch == '|':
                used = True
                break
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    break
            else:
                dest += ch
        if not used:
            sn = dest
        else:
            while pattern_end < len(text):
                ch = text[pattern_end]
                # print("ch ", ch)
                pattern_end += 1
                if ch == ']':
                    depth -= 1
                    if depth == 0:
                        break
                else:
                    sn += ch

        dest_list.append(dest)
        sn_list.append(sn)
        # print("depth ", depth)
        # print("dest ", dest)
        if depth == 0:
            begin = pattern_end
        else:
            removed += text[begin]
            begin += 1
        pattern_begin = text.find(pattern, begin)
        if pattern_begin == -1:
            break
    if len(text) > begin:
        removed += text[begin:]
    # print("removed ", removed)
    return dest_list, sn_list

def split_lines(text):
    text_lines =[]
    inside_sn = False
    line = ""
    depth = 0
    # flag = False
    cnt = 0
    for ch in text:
        cnt += 1
        # if flag:
        #     print(ch)
        if ch == '.' and inside_sn:
            line += ch
        elif ch == '.' and not inside_sn:
            # print(line[-4:])
            # if len(line) == 112 and line[-4:] == 'Rand':
                # flag = True
            text_lines.append(line.strip())
            line = ""
        elif ch == '[':
            line += ch
            inside_sn = True
            depth += 1
        elif ch == ']':
            line += ch
            depth -= 1
            if depth == 0:
                inside_sn = False
        else:
            line += ch
    if len(line) > 0:
        text_lines.append(line.strip())
    return text_lines

if __name__ == "__main__":
    pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)
    pathSurfaceNames = os.path.join(PATH_WIKI_XML, FILENAME_SURFACE_NAMES)
    pathArticles = os.path.join(PATH_WIKI_XML, FILENAME_ARTICLES)
    pathSentences = os.path.join(PATH_WIKI_XML, FILENAME_SENTENCES)
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
        line = "\n</root>"
        f.write(line)
    """
    with codecs.open(pathArticles, "r", ENCODING) as articlesFH:
        articlesReader = csv.reader(articlesFH, delimiter=',')
        article_dict = {row[1] : row[0] for row in articlesReader}
        del article_dict['title']

    with codecs.open(pathArticlesRedirect, "r", ENCODING) as redirectFH:
        redirectReader = csv.reader(redirectFH, delimiter=',')
        redirect_dict = {row[1] : row[2] for row in redirectReader}
        del redirect_dict['title']
    """
    with codecs.open(pathSurfaceNames, "a", ENCODING) as surfaceFH, codecs.open(pathSentences, "a", ENCODING) as sentenceFH:

        surface_namesWriter = csv.writer(surfaceFH, quoting=csv.QUOTE_MINIMAL)
        sentencesWriter = csv.writer(sentenceFH, quoting=csv.QUOTE_MINIMAL)

        # surface_namesWriter.writerow(['sentence_id', 'source', 'destination', 'surface_name'])
        # sentencesWriter.writerow(['sentence_id', 'sentence'])

        for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
            
            tname = strip_tag_name(elem.tag)
            is_article = False

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
                        continue
                        # ignoring templates
                    elif len(redirect) > 0:
                        continue
                    else:
                        is_article = True
                        articleCount += 1
                        
                    if totalCount > 1 and (totalCount % 100000) == 0:
                        print("{:,}".format(totalCount))

                if tname =="text":
                    content = elem.text
                if is_article:
                    content = clean_text(content)
                    # _, links = build_links(content)
                    # print(links)
                    # print(content)
                    local_id = 0
                    # sn_list = []
                    content_lines = split_lines(content)
                    for line in content_lines:
                        # print(line)
                        destination, surface_names = parse_sentence(line)
                        if destination:
                            local_id += 1
                            index = str(id) + '.' + str(local_id)
                            sentencesWriter.writerow([index, line])
                            for (dest, sn) in zip(destination, surface_names):
                                # sn_list.append(sn)
                                """
                                if dest in article_dict.keys():
                                    dest_id = article_dict[dest]
                                elif dest in redirect_dict.keys():
                                    dest_id = redirect_dict[dest]
                                else:
                                    dest_id = -1
                                """
                                surface_namesWriter.writerow([index, title, dest, sn])
                    
                    # for item in links:
                    #     if item['text'] not in sn_list:
                    #         print(title, item['link'], item['text'])
                    
                elem.clear()
"""
    elapsed_time = time.time() - start_time

    print("Total pages: {:,}".format(totalCount))
    print("Template pages: {:,}".format(templateCount))
    print("Article pages: {:,}".format(articleCount))
    print("Redirect pages: {:,}".format(redirectCount))
    print("Elapsed time: {}".format(hms_string(elapsed_time)))
"""
