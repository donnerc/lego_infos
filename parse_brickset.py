from bs4 import BeautifulSoup
import requests
import os.path

def load_models(models_file='models.txt'):
    models = []
    with open(models_file, 'r', encoding='utf-8') as fd:
        for line in fd:
            if line != '':
                models += [int(line.strip())]
    return models


def cached_request(set_no):
    filename = str(set_no) + '.html'
    cachedir = 'cache'
    filepath = os.path.join(cachedir, filename)

    if os.path.isfile(filepath):
        print('cache hit for model', set_no)
        with open(filepath, 'r', encoding='utf-8') as fd:
            html = fd.read()

    else:

        url = 'https://brickset.com/sets/' + str(set_no)
        cookies = {
            'ActualCountry' : 'CountryCode=CH&CountryName=Switzerland',
            'PreferredCountry2' : 'CountryCode=CH&CountryName=Switzerland',
            'ASP.NET_SessionId' : 'gvnhcykabcaiyojst0s5orm5',
            '__atuvc' : '0%7C29%2C0%7C30%2C0%7C31%2C9%7C32%2C12%7C33'
        }

        html =  requests.get(url, cookies=cookies).text
        try:
            with open(filepath, 'w', encoding='utf-8') as fd:
                fd.write(html)
        except Exception as e:
            print('Unable to write to file', filepath, str(e))

    return html

def get_set_infos(set_no):
    html = cached_request(set_no)
    soup = BeautifulSoup(html, 'html.parser')

    parsed_features = {}
    
    try:
        features = soup.select('section.featurebox')[0].select('dt')
        for feature in features:
            feature_key = feature.contents[0]
            feature_value = feature.find_next_sibling('dd')

            if feature_value.find('a'):
                feature_value = [x.string for x in feature_value.find_all('a')]
                if isinstance(feature_value, list) and len(feature_value) == 1:
                    feature_value = feature_value[0]
            else:
                feature_value = feature_value.string

            parsed_features[feature_key] = feature_value

        image = soup.find('meta', property='og:image')
        parsed_features['Image'] = image['content']
    except:
        return {}
            
    return parsed_features


def generate_html_table(models):
    
    features = [
        'Minifigs',
        'Theme group',
        'Year released',
        'Dimensions',
        'Rating',
        'LEGO item numbers',
        'Notes',
        'Name',
        'Theme',
        'Pieces',
        'Current value',
        'Packaging',
        'Set type',
        'RRP',
        'Tags',
        'Set number',
        'Price per piece',
        'Weight',
        'Barcodes',
        'Subtheme',
        'Image',
    ]

    # Transforms
    identity = lambda x: str(x)
    image = lambda x: '<img src="{src}" width="400px" >'.format(src=x)
    def split_current_value(x):
        if isinstance(x, list):
            return x[1].split('Fr')[1]
        else:
            return ''

    features_to_show = [
        ('Set number', identity),  
        #('Image', image),
        ('Current value', split_current_value),  
        ('Name', identity),  
        ('Year released', identity),  
        ('Minifigs', identity),  
        ('Rating', identity),  
        ('Pieces', identity),  
        ('Weight', identity),  
    ]

    html = '''
        <html>
        <head>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css" integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
        </head>
        <body>
        <table class="table">
            <thead>
                <tr><td>
                {headers}
                </td></tr>
            </thead>
            <tbody>
                {tbody}
            </tbody>
        </table>
        </body>
        </html>
        '''
    
    tbody = ''
    for m in models:
        print('parsing model', m)
        model_features = get_set_infos(m)
        if model_features:
            cells = '<tr>' + '\n'.join(
                ['<td>' + func(model_features.get(key, None)) +'</td>' for key, func in features_to_show ] 
            ) + '</tr>'
            tbody += cells

    

    headers = '</td><td>'.join([x[0] for x in features_to_show])

    with open('table.html', 'w', encoding='utf-8') as fd:
        table = html.format(headers=headers, tbody=tbody)
        fd.write(table)

    


def total_value(models):
    result = 0

    for m in models:
        try:
            features = get_set_infos(m)
            model_value = features['Current value'][1].split('Fr')[1]
        except:
            model_value = 0
        result += model_value

        print('model', m, ".value = ", model_value)



    return result

models = load_models()

#print('Total value : ', total_value(models))
print(generate_html_table(models))
