import requests
import json
from tqdm import tqdm
import os
from dotenv import load_dotenv
from fake_useragent import UserAgent
from datetime import date

current_date = date.today()

UA = UserAgent()
headers = {"User-Agent": UA.random}

load_dotenv()

vk_params = {'access_token': os.getenv('ACC_TOKEN'), 'v': '5.131'}
vk_base_url = 'https://api.vk.com/method/'
ya_base_url = 'https://cloud-api.yandex.net/v1/disk/resources/'
ya_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': os.getenv('YA_TOKEN')}
ya_params = {'path': f'{current_date}'}


def users_info(user_id):
    url = f'{vk_base_url}users.get'
    params = {'user_ids': user_id}
    response = requests.get(url, headers=headers, params={**vk_params, **params})
    return response.json()


def check_token_ya():
    try:
        response = requests.get('https://cloud-api.yandex.net/v1/disk', headers=ya_headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError as e:
        print("Ошибка подключения: ", e)
        exit(1)
    except requests.Timeout as e:
        print("Ошибка тайм-аута: ", e)
        exit(1)
    except requests.RequestException as e:
        print("Ошибка запроса: ", e)
        exit(1)


def check_token_vk(user_id):
    url = f'{vk_base_url}users.get'
    params = {'user_ids': user_id}
    try:
        response = requests.get(url, headers=headers, params={**vk_params, **params})
        if 'error' in response.json():
            return False
        else:
            return True
    except requests.ConnectionError as e:
        print("Ошибка подключения: ", e)
        exit(1)
    except requests.Timeout as e:
        print("Ошибка тайм-аута: ", e)
        exit(1)
    except requests.RequestException as e:
        print("Ошибка запроса: ", e)
        exit(1)


def json_log(lst):
    f_data = []
    for item in lst:
        f_data.append({
            'file_name': item['file_name'],
            'size': item['size'],
        })
    with open('log.json', 'a', encoding='utf-8') as f:
        json.dump(f_data, f, indent=4, ensure_ascii=False)


def get_photos(user_id, count):
    data_f = []
    url = f'{vk_base_url}photos.get'
    params = {'owner_id': user_id, 'count': count, 'album_id': 'profile', 'extended': 1}
    params.update(vk_params)
    try:
        response = (requests.get(url, headers=headers, params=params))
        for item in tqdm(response.json()['response']['items'], ncols=100, colour='BLUE', desc='Get info about photos'):
            img_info = sorted(item['sizes'], key=lambda k: k['type'], reverse=False)
            img_url = img_info[-1]['url']
            img_size = img_info[-1]['type']
            img_name = item['likes']['count']
            data_f.append({
                'file_name': f'{img_name}.jpg',
                'size': img_size,
                'url': img_url,
            })
        return data_f

    except requests.ConnectionError as e:
        print("Ошибка подключения: ", e)
        exit(1)
    except requests.Timeout as e:
        print("Ошибка тайм-аута: ", e)
        exit(1)
    except requests.RequestException as e:
        print("Ошибка запроса: ", e)
        exit(1)


def mk_dir():
    response = requests.get(ya_base_url, headers=ya_headers, params=ya_params)
    if response.status_code == 404:
        requests.put(ya_base_url, headers=ya_headers, params=ya_params)


def check_name(img_name):
    params = {
        'path': f'{current_date}/{img_name}',
    }
    response = requests.get(ya_base_url, params=params, headers=ya_headers)
    if response.status_code == 200:
        name = f'{str(current_date)}_{img_name}'
    else:
        name = f'{img_name}'
    return name


def ya_upload(data):
    logger = []

    for item in tqdm(data, ncols=100, colour='GREEN', desc='Upload photos'):
        name = check_name(item['file_name'])
        params = {'path': f'{current_date}/{name}',
                  'url': item['url']}
        response = requests.post(f'{ya_base_url}upload', params=params, headers=ya_headers)
        upload_link = response.json()['href']
        requests.put(upload_link, headers=ya_headers)
        logger.append({
            'file_name': name,
            'size': item['size'],
        })
    json_log(logger)


def main():
    valid_input = False
    while not valid_input:
        user_id = input('ID user: ')
        if user_id.isdigit():
            valid_input = True
        else:
            print('ID должен быть числом')
    if check_token_ya() and check_token_vk(user_id):
        valid_num = False
        while not valid_num:
            count = input('Number of photos to download (default - 5): ')
            if count.isdigit():
                valid_num = True
            elif count == '':
                count = 5
                valid_num = True
            else:
                print('Number должен быть числом')
        mk_dir()
        data = get_photos(user_id, count)
        ya_upload(data)
    else:
        print('Один из токенов не валиден')


if __name__ == '__main__':
    main()
