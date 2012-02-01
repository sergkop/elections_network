# coding=utf8
import json
import os.path
import re

DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'data')

def get_regions_data(name, merged):
    results_data_path = os.path.join(DATA_PATH, 'regions', name+'.json')
    results_data = json.loads(open(results_data_path).read().decode('utf8'))

    regions = []
    for node in results_data:
        if merged==('vrnorg' in node):
            regions.append(node)
        if len(node['sub'])>0 and not node['sub'][0]['name'].startswith(u'УИК'):
            for sub_node in node['sub']:
                if merged==('vrnorg' in sub_node):
                    regions.append(sub_node)

    return sorted(regions, key=lambda region: region['name'])

def merge_data(name, tvd, root, vrnorg, vrnkomis, new_name, x_coord, y_coord):
    results_data_path = os.path.join(DATA_PATH, 'regions', name+'.json')
    results_data = json.loads(open(results_data_path).read().decode('utf8'))

    # find region in results data
    region = None
    for node in results_data:
        if 'vrnorg' not in node and node['tvd']==tvd and node['root']==root:
            region = node
            break
        if len(node['sub'])>0 and not node['sub'][0]['name'].startswith(u'УИК'):
            for sub_node in node['sub']:
                if 'vrnorg' not in sub_node and sub_node['tvd']==tvd and sub_node['root']==root:
                    region = sub_node
                    break

    # find region in info data
    info_data_path = os.path.join(DATA_PATH, 'regions', name+'-info.json')
    info_tiks = json.loads(open(info_data_path).read().decode('windows-1251'))
    info_tik = filter(lambda tik: tik['vrnorg']==vrnorg and tik['vrnkomis']==vrnkomis, info_tiks)[0]

    # merge info
    region.update(info_tik)
    region['name'] = new_name.strip()

    if x_coord and y_coord:
        region['x_coord'], region['y_coord'] = x_coord, y_coord

    with open(results_data_path, 'w') as f:
        f.write(json.dumps(results_data, indent=4, ensure_ascii=False).encode('utf8'))

    # remove merged info
    info_tiks.remove(info_tik)
    with open(info_data_path, 'w') as f:
        f.write(json.dumps(info_tiks, indent=4, ensure_ascii=False).encode('windows-1251'))

def parse_address(address):
    address = address.replace(u'мунициальный', '')
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
            .replace(u'улица', '')

    m = re.match(r'(.+), (\s+\d+)', map_address)
    if m:
        map_address = m.group(1) + ' ' + m.group(2)

    # TODO: remove , in front of house number
    res['map_address'] = map_address

    return res
