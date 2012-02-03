# coding=utf8
import json
import os.path
import re

DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'data')

def get_regions_data(name):
    results_data_path = os.path.join(DATA_PATH, 'regions', name+'.json')
    results_data = json.loads(open(results_data_path).read().decode('utf8'))
    return sorted(results_data, key=lambda region: region['name'])

def get_merge_data(name):
    merge_data_path = os.path.join(DATA_PATH, 'regions', name+'-merge.json')
    try:
        return json.loads(open(merge_data_path).read().decode('utf8'))
    except IOError:
        return []

def merge_data(name, tvd, root, vrnorg, vrnkomis, new_name, x_coord, y_coord, postcode, address):
    results_data_path = os.path.join(DATA_PATH, 'regions', name+'.json')
    results_data = json.loads(open(results_data_path).read().decode('utf8'))
    result_tik = filter(lambda node: node['tvd']==tvd and node['root']==root, results_data)[0]

    # find region in info data
    info_data_path = os.path.join(DATA_PATH, 'regions', name+'-info.json')
    info_tiks = json.loads(open(info_data_path).read().decode('windows-1251'))
    info_tik = filter(lambda tik: tik['vrnorg']==vrnorg and tik['vrnkomis']==vrnkomis, info_tiks)[0]

    # merge info
    result_tik['old_name'] = result_tik['name']
    result_tik.update(info_tik)
    result_tik['tik_name'] = info_tik['name']
    result_tik['name'] = new_name.strip()
    result_tik['postcode'] = postcode
    result_tik['address'] = address

    if x_coord and y_coord:
        result_tik['x_coord'], result_tik['y_coord'] = x_coord, y_coord

    merge_data = get_merge_data(name)
    merge_data.append(result_tik)

    merge_data_path = os.path.join(DATA_PATH, 'regions', name+'-merge.json')
    with open(merge_data_path, 'w') as f:
        f.write(json.dumps(merge_data, indent=4, ensure_ascii=False).encode('utf8'))

def parse_address(address):
    address = address.replace(u'мунициальный ', '')
    parts = [part.strip() for part in address.split(',')]

    res = {}

    # Extract postcode
    m = re.match(r'^\d{6}$', parts[0])
    if m:
        res['postcode'] = parts[0]
        parts.pop(0)

    parts = filter(lambda part: u'область' not in part and part!='.' and part!='', parts)
    address = ', '.join(parts)

    map_parts = list(parts)

    # Address displayed to users
    res['address'] = address.replace(u'муниципальный', '').strip()

    """
    1) В адресе для яндекс карт перед номером дома не должно быть запятой
    2) Всяческие префиксы (п., г., итп) препятствуют распознаванию адреса
    3) В глубинке номера домов, а иногда и улицы, не нанесены на карту. В этом случае
       помечать населенный пункт
    """

    # Address used for Yandex maps
    map_address = res['address']

    map_address = ', '.join(filter(lambda part: u'район' not in part and \
            u'комн.' not in part and u'кабинет' not in part, map_address.split(',')))

    map_address = map_address.replace(u'ул.', '').replace(u'с.', '').replace(u'п.', '') \
            .replace(u'г.', '').replace(u'город ', '').replace(u'прос ', '').replace(u'пл.', '') \
            .replace(u'д.', '').replace(u'дом', '').replace(u'городской', '').replace(u'округ', '') \
            .replace(u'улица', '').replace(u'ст.', '').replace(u'ст-ца', '') \
            .replace(u'пгт', '').replace(u'поселок городского типа', '') \
            .replace(u'ЗАО', '').replace(u'ЮАО', '').replace(u'рабочий поселок', '') \
            .replace(u'муниципальный район', '')

    m = re.match(r'(.+), (\s+\d+)', map_address)
    if m:
        map_address = m.group(1) + ' ' + m.group(2)

    # TODO: remove , in front of house number
    res['map_address'] = map_address

    return res
