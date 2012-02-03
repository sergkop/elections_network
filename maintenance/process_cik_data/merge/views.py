# coding=utf8
import json
import os.path
import re

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from merge.utils import DATA_PATH, get_regions_data, get_merge_data, merge_data, parse_address

regions_ids_path = os.path.join(DATA_PATH, 'region_ids.txt')

REGIONS = []
for line in open(regions_ids_path):
    region_title, region_name, region_id = line.split(', ')
    REGIONS.append((region_name, region_title, region_id.strip()))

def main(request):
    # TODO: show number of unmerged entries for each region
    left = []
    for name, title, region_id in REGIONS:
        merged_data = get_merge_data(name)
        merged_tvds = [tik_merged['tvd'] for tik_merged in merged_data]

        results_lst = filter(lambda result_tik: result_tik['tvd'] not in merged_tvds, get_regions_data(name))

        left.append((name, title, float(len(merged_data))/(len(merged_data)+len(results_lst)+0.01)*100))

    return render_to_response('main.html', {'REGIONS': left})

def region(request, name):
    region = (filter(lambda region: region[0]==name, REGIONS) or [None])[0]
    if not region:
        return None

    if request.method == 'POST':
        if 'result_tik' not in request.POST:
            return HttpResponse(u'Выбирите округ в правой таблице')
        tvd, root = request.POST['result_tik'].split('_')
        vrnorg, vrnkomis = request.POST['info_tik'].split('_')

        if 'add_geo' in request.POST:
            try:
                x_coord, y_coord = float(request.POST['x_coord']), float(request.POST['y_coord'])
            except ValueError:
                return HttpResponse(u'Вы забыли найти координаты ТИКа')
        else:
            x_coord, y_coord = None, None

        try:
            int(request.POST['postcode'])
        except ValueError:
            return HttpResponse(u'Не введен почтовый код (не обрабатывайте этот ТИК)')

        merge_data(name, tvd, root, vrnorg, vrnkomis, request.POST['new_name'], x_coord, y_coord,
                int(request.POST['postcode']), request.POST['address'])

        return redirect('region', name)

    merge_data_path = os.path.join(DATA_PATH, 'regions', name+'-merge.json')
    try:
        merged_data = json.loads(open(merge_data_path).read().decode('utf8'))
    except IOError:
        merged_data = []

    merged_vrnorgs = [tik_merged['vrnorg'] for tik_merged in merged_data]
    merged_tvds = [tik_merged['tvd'] for tik_merged in merged_data]

    results_lst = filter(lambda result_tik: result_tik['tvd'] not in merged_tvds, get_regions_data(name))

    info_data_path = os.path.join(DATA_PATH, 'regions', name+'-info.json')
    info_tiks = json.loads(open(info_data_path).read().decode('windows-1251'))

    info_tiks = filter(lambda info_tik: info_tik['vrnorg'] not in merged_vrnorgs, info_tiks)

    for info_tik in info_tiks:
        info_tik.update(parse_address(info_tik['address']))

        for ending in (u'ого района', u'ого округа'):
            index = info_tik['name'].find(ending)
            if index != -1:
                suffix = info_tik['name'][index+len(ending):]
                if any(word in suffix for word in (u'края', u'области', u'города')):
                    info_tik['name'] = info_tik['name'][:index+len(ending)]

        info_tik['name'] = info_tik['name'] \
                .replace(u'муниципального ', '') \
                .replace(u'ная районная', u'ный район').replace(u'кая районная', u'кий район') \
                .replace(u'кого района', u'кий район').replace(u'ного района', u'ный район') \
                .replace(u'г.', '').replace(u'города', '')

    context = {
        'name': region[0],
        'title': region[1],
        'region_id': region[2],
        'result_tiks': results_lst,
        'info_tiks': info_tiks,
        'merged_tiks': merged_data,
    }
    return render_to_response('region.html', context_instance=RequestContext(request, context))

def cancel(request, name, tvd):
    merged_data = get_merge_data(name)

    merged_data = filter(lambda data: data['tvd']!=tvd, merged_data)
    merge_data_path = os.path.join(DATA_PATH, 'regions', name+'-merge.json')
    with open(merge_data_path, 'w') as f:
        f.write(json.dumps(merged_data, indent=4, ensure_ascii=False).encode('utf8'))

    return redirect('region', name)
