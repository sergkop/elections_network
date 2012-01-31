# coding=utf8
import json
import os.path
import re

from django.conf import settings
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'data')
regions_ids_path = os.path.join(DATA_PATH, 'region_ids.txt')

REGIONS = []
for line in open(regions_ids_path):
    region_title, region_name, region_id = line.split(', ')
    REGIONS.append((region_name, region_title, region_id.strip()))

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

def merge_data(name, tvd, root, vrnorg, vrnkomis, new_name):
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
    region['name'] = new_name
    with open(results_data_path, 'w') as f:
        f.write(json.dumps(results_data, indent=4, ensure_ascii=False).encode('utf8'))

    # remove merged info
    info_tiks.remove(info_tik)
    with open(info_data_path, 'w') as f:
        f.write(json.dumps(info_tiks, indent=4, ensure_ascii=False).encode('windows-1251'))

def main(request):
    # TODO: show number of unmerged entries for each region
    left = []
    for name, title in REGIONS:
        info_data_path = os.path.join(DATA_PATH, 'regions', name+'-info.json')
        left.append((name, title, len(json.loads(open(info_data_path).read().decode('windows-1251')))))

    return render_to_response('main.html', {'REGIONS': left})

def region(request, name):
    region = (filter(lambda region: region[0]==name, REGIONS) or [None])[0]
    if not region:
        return None

    if request.method == 'POST':
        tvd, root = request.POST['result_tik'].split('_')
        vrnorg, vrnkomis = request.POST['info_tik'].split('_')
        merge_data(name, tvd, root, vrnorg, vrnkomis, request.POST['new_name'])

        return redirect('region', name)

    results_lst = get_regions_data(name, False)

    info_data_path = os.path.join(DATA_PATH, 'regions', name+'-info.json')
    info_tiks = json.loads(open(info_data_path).read().decode('windows-1251'))

    for info_tik in info_tiks:
        address = info_tik['address'].replace(u'мунициальный', '')
        parts = [part.strip() for part in address.split(',')]

        # Extract postcode
        m = re.match(r'^\d{6}$', parts[0])
        if m:
            info_tik['postcode'] = parts[0]
            parts.pop(0)

        parts = filter(lambda part: u'область' not in part and part!='.', parts)

        info_tik['address'] = ', '.join(parts)

    context = {
        'name': region[0],
        'title': region[1],
        'region_id': region[2],
        'result_tiks': results_lst,
        'info_tiks': info_tiks,
        'merged_tiks': get_regions_data(name, True),
    }
    return render_to_response('region.html', context_instance=RequestContext(request, context))
