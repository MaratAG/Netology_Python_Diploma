"""Дипломное задание по курсу Нетология Пайтон."""
import json
import time

import progressbar

import requests


VERSION = '5.78'
TOKEN = \
    '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b' \
    '480b7d9fb59859870658c4a0b8fdc4dd494db19099'


class Api_VK():
    """Класс для работы с API VK."""

    uri = 'https://api.vk.com/method/'
    token = None
    version = None

    def __init__(self, token, version):
        """Инициализация параметров подключения к API VK."""
        self.token = token
        self.version = version

    def get_response_api_vk(self, method, params, key_response=None):
        """Получение данных с помощью API VK."""
        message_error = 'error'
        error_code_request = 6
        count_errors = 0
        max_errors = 10
        time_for_wait_sec = 1

        response = None
        result_json = []

        full_uri = ''.join([self.uri, method])
        params['access_token'] = self.token
        params['v'] = self.version

        while (response is None) and (count_errors <= max_errors):
            response = requests.get(full_uri, params)
            result_json = response.json()
            if message_error in result_json:
                if result_json[message_error]['error_code'] \
                        == error_code_request:
                    response = None
                    count_errors += 1
                    time.sleep(time_for_wait_sec)
            else:
                result_json = response.json()['response']
                if key_response is not None:
                    result_json = result_json[key_response]

        return result_json


def get_user_id(api_vk, user_ids):
    """Получение ID пользователя VK."""
    user_id = None
    message_error = 'error'
    params = {
        'user_ids': user_ids
    }
    info_about_user = api_vk.get_response_api_vk('users.get', params)
    if message_error not in info_about_user:
        user_id = info_about_user[0]['id']

    return user_id


def get_groups_of_user(api_vk, user_id):
    """Получение списка групп, в которых состоит пользователь."""
    params = {
        'user_id': user_id
    }
    return api_vk.get_response_api_vk('groups.get', params, 'items')


def get_friends_of_user(api_vk, user_id):
    """Получения списка друзей пользователя."""
    params = {
        'user_id': user_id
    }
    return api_vk.get_response_api_vk('friends.get', params, 'items')


def get_info_about_groups(api_vk, groups):
    """Получение необходимой информации о группе."""
    params = {
        'group_id': groups,
        'fields': 'members_count'
    }

    result_of_request = api_vk.get_response_api_vk('groups.getById', params)[0]
    information_about_group = {
        'gid': result_of_request['id'],
        'name': result_of_request['name'],
        'members_count': result_of_request['members_count']
    }
    return information_about_group


def get_info_and_write_json_about_groups(api_vk, groups):
    """Компонвка финального датасета и запись в файл."""
    data_for_json = list()

    for group in groups:
        info_about_groups = get_info_about_groups(api_vk, group)
        data_for_json.append(info_about_groups)

    with open('groups.json', 'w', encoding='utf8') as file_json:
        json.dump(data_for_json, file_json, indent=4,
                  sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    print('Результаты работы программы записаны в файл.')


def get_groups_of_friends(api_vk, friends_of_user):
    """Подготовка множества групп, в которые входят друзья пользователя."""
    count_of_friends = len(friends_of_user)
    pbar = \
        progressbar.ProgressBar(
            count_of_friends,
            widgets=[progressbar.Bar(),
                     progressbar.Percentage(), ' ',
                     progressbar.ETA()])

    groups_of_friends = set()
    for item_of_friend in pbar(range(count_of_friends)):
        groups_of_friends = \
            groups_of_friends | \
            set(get_groups_of_user(api_vk, friends_of_user[item_of_friend]))

    return groups_of_friends


def main():
    """Инициализация программы и вывод результатов."""
    api_vk = Api_VK(TOKEN, VERSION)

    user_ids = input('Введите имя пользователя или его ID ').strip()

    if len(user_ids) == 0:
        print('Вы не ввели необходимые данные. Используем демоданные')
        user_ids = 'tim_leary'

    user_id = get_user_id(api_vk, user_ids)

    if user_id is not None:
        groups_of_user = set(get_groups_of_user(api_vk, user_id))

        friends_of_user = get_friends_of_user(api_vk, user_id)
        groups_of_friends = get_groups_of_friends(api_vk, friends_of_user)

        result_groups = list(groups_of_user - groups_of_friends)

        get_info_and_write_json_about_groups(api_vk, result_groups)
    else:
        print(
            'Данные о пользователе {} не найдены.'.format(user_ids))


main()
