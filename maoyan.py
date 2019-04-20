#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from requests.exceptions import RequestException
import re
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import json
import time

def get_one_page(url):
    r = requests.get(url)
    try:
        if r.status_code == 200:
            return r.text
        return None
    except RequestException:
        return None

'''
def parse_one_page(html): #generator
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(.*?)</a>'
                            +'.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                            +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
    items = re.findall(pattern,html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2].strip(),
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5].strip() + item[6].strip()
        }

def parse_one_page(html): #generator
    soup = BeautifulSoup(html,'lxml')
    for dd in soup.find_all(name='dd'):
        yield {
            'index': dd.find(class_='board-index').string,
            'image': dd.find_all(name='img')[1]['data-src'],           
            'title': dd.find(class_='name').a.string.strip(),
            'actor': dd.find(class_='star').string.strip()[3:],
            'time': dd.find(class_='releasetime').string.strip()[5:],
            'score': dd.find(class_='integer').string.strip() + dd.find(class_='fraction').string.strip()
        }
'''

def parse_one_page(html): #generator
    doc = pq(html)
    for dd in doc('dd').items():
        yield {
            'index': dd('.board-index').text(),
            'image': dd('img:last-child').attr('data-src'),
            'title': dd('.name a').text().strip(),
            'actor': dd('.star').text().strip()[3:],
            'time': dd('.releasetime').text().strip()[5:],
            'score': dd('.integer').text().strip() + dd('.fraction').text().strip()
        }


def write_to_json(content):
    with open('maoyanresult.json','a',encoding='utf-8') as file:
        file.write(json.dumps(content,indent=2,ensure_ascii=False)+'\n')
        

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        write_to_json(item)

if __name__ == '__main__':
    for i in range(10):
        main(i*10)
        time.sleep(1)
