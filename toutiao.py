import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool

def get_page(offset):
    params = {
        'aid': '24',
        'app_name':	'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': '杨洋美图',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.ConnectionError:
        return None

def get_images(json):
    if json.get('data'):
        for data in json.get('data'):
            if data.get('image_list'):
                images = data.get('image_list')
                for image in images:
                    yield{
                        'image': image.get('url'),
                        'title': data.get('title')
                    }

def save_image(image):
    path = os.path.join('/home/hy/python/yangyang',image.get('title'))
    if not os.path.exists(path):
        os.mkdir(path)
    try:
        response = requests.get(image.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(path,md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
            else:
                print('already download')
    except requests.ConnectionError:
        return None

def main(offset):
    page_json = get_page(offset)
    for image in get_images(page_json):
        save_image(image)
    print('success')

start = 0
end = 2

if __name__ == '__main__':
    group = [x*20 for x in range(start,end)]
    p = Pool()
    p.map(main,group)
    p.close()
    p.join()

        