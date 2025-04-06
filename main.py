'''
скорректированная версия с прямой загрузкой по линку
'''
import requests
from tqdm import tqdm
import os
from dotenv import load_dotenv
from fake_useragent import UserAgent
from datetime import date

current_date = date.today()

UA = UserAgent()
headers = {"User-Agent": UA.random}

load_dotenv()


class VK:
    def __init__(self, access_token=os.getenv('ACC_TOKEN'), version='5.131'):
        self.vk_params = {'access_token': access_token, 'v': version}
        self.vk_base_url = 'https://api.vk.com/method/'
        self.ya_base_url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        self.ya_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': os.getenv('YA_TOKEN')}
        self.ya_params = {'path': f'{current_date}'}

    def users_info(self, user_id):
        url = f'{self.vk_base_url}users.get'
        params = {'user_ids': user_id}
        response = requests.get(url, headers=headers, params={**self.vk_params, **params})
        return response.json()

    def get_photos(self, user_id, count):
        url = f'{self.vk_base_url}photos.get'
        params = {'owner_id': user_id, 'count': count, 'album_id': 'profile', 'extended': 1}
        params.update(self.vk_params)
        response = requests.get(url, headers=headers, params=params)
        requests.put(self.ya_base_url, headers=self.ya_headers, params=self.ya_params)
        for item in tqdm(response.json()['response']['items'], ncols=100, colour='BLUE', desc='Downloading photos'):
            img_url = item['sizes'][-1]['url']
            img_name = item['likes']['count']
            params = {'path': f'{current_date}/{img_name}.jpg',
                       'url': img_url}
            response = requests.post(f'{self.ya_base_url}upload', params=params, headers=self.ya_headers)
            upload_link = response.json()['href']
            requests.put(upload_link, headers=self.ya_headers)

    def get_status(self, user_id):
        url = f'{self.vk_base_url}status.get'
        params = {'owner_id': user_id}
        params.update(self.vk_params)
        response = requests.get(url, headers=headers, params=params)
        return response.json()


if __name__ == '__main__':
    user_id = str(input('ID user: ')).strip()
    count = input('Number of photos to download (default - 5): ')
    if count == '':
        count = 5
    vk = VK()
    vk.get_photos(user_id, count)
