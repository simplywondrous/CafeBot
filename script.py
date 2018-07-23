# From https://github.com/Machyne/pal/blob/master/api/bonapp/bon_api.py
import requests
import re, json

# Constants
CAFE_NAMES = ['bullseye-cafe', 'cafe-target', 'north-campus']
CAFE_URL = 'https://target.cafebonappetit.com/cafe/{cafe_name}/{date}/'
RE_CAFE_NAME = r'Bamco.current_cafe\s+=\s+(?:[^;]+)name:\s+\'(.*?)\'(?:[^;]+);' #TODO make sense of
RE_MENU_ITEMS = r'Bamco.menu_items\s+=\s+(.+);'
RE_DAYPARTS = r'Bamco.dayparts\[\'(\d+)\'\]\s+=\s+([^;]+);'

def get_page(cafe_name, date):
    """Doc"""
    url = CAFE_URL.format(cafe_name=cafe_name, date=date.isoformat())
    response = requests.get(url, timeout=5.0, verify=False)
    return response.text

def save_page():
    file = open('cafe_menu.html', 'w+')
    from datetime import date
    file.write(get_page(CAFE_NAMES[1], date.today()))
    file.close()

def get_data_from_page(page):
    # Find the cafe
    name_data = re.findall(RE_CAFE_NAME, page)
    name = name_data[0]

    menu_data = re.findall(RE_MENU_ITEMS, page)
    #print(menu)
    menu = json.loads(menu_data[0]) if menu_data else None #TODO why only first item?

    dayparts = {}
    dayparts_nodes = re.findall(RE_DAYPARTS, page)
    for part in dayparts_nodes:
        part_num, data = part
        dayparts[int(part_num)] = json.loads(data)

    return name, menu, dayparts

if __name__ == '__main__':
    from datetime import date
    #save_page()
    response = get_page(CAFE_NAMES[1], date.today())
    print(get_data_from_page(response))
    get_data_from_page(response)