def format_percent(count, total):
    return '%2.2f%%' % (100*float(count)/total)

def results_table_data(protocols, dashes=True):
    protocols = [protocol for protocol in protocols if protocol.p9+protocol.p10>0]

    if len(protocols) == 0:
        symbol = '&mdash;' if dashes else ''
        return {'girinovskiy': symbol, 'zyuganov': symbol, 'mironov': symbol,
                'prokhorov': symbol, 'putin': symbol, 'invalid': symbol}

    data = {}
    for field in ('p9', 'p10', 'p19', 'p20', 'p21', 'p22', 'p23'):
        data[field] = sum(getattr(protocol, field) for protocol in protocols)

    total = data['p9'] + data['p10']

    return {
        'girinovskiy': format_percent(data['p19'], total),
        'zyuganov': format_percent(data['p20'], total),
        'mironov': format_percent(data['p21'], total),
        'prokhorov': format_percent(data['p22'], total),
        'putin': format_percent(data['p23'], total),
        'invalid': format_percent(data['p9'], total),
    }
