# Modified from https://github.com/Machyne/pal/blob/master/api/bonapp/bon_api.py
import requests
import re, json
import cafe.menu as menu
import sys

# Constants
CAFE_NAMES = ['bullseye-cafe', 'cafe-target', 'north-campus']
CAFE_URL = 'https://target.cafebonappetit.com/cafe/{cafe_name}/{date}/'
RE_CAFE_NAME = r'Bamco.current_cafe\s+=\s+(?:[^;]+)name:\s+\'(.*?)\'(?:[^;]+);'
RE_MENU_ITEMS = r'Bamco.menu_items\s+=\s+(.+);'
RE_DAYPARTS = r'Bamco.dayparts\[\'(\d+)\'\]\s+=\s+([^;]+);'
RE_STATION_EXTRA = r'<(.*?)>@?'

# Constants for parsing menu
NAME_FIELDS = [u'id', u'label']
INFO_FIELDS = [u'description', u'cor_icon', u'price']
EXTRA_FIELDS = [u'nutrition_details']
MENU_FIELDS = NAME_FIELDS + INFO_FIELDS + EXTRA_FIELDS

def get_page(cafe_name, date):
    """Doc"""
    url = CAFE_URL.format(cafe_name=cafe_name, date=date.isoformat())
    response = requests.get(url, timeout=5.0, verify=False)
    return response.text

def get_data_from_page(page):
    name_data = re.findall(RE_CAFE_NAME, page)
    name = name_data[0]

    menu_data = re.findall(RE_MENU_ITEMS, page)
    menu = json.loads(menu_data[0]) if menu_data else None

    dayparts = {}
    dayparts_nodes = re.findall(RE_DAYPARTS, page)
    for part in dayparts_nodes:
        part_num, data = part
        dayparts[int(part_num)] = json.loads(data)

    return name, menu, dayparts

def combine(data):
    """ Get the specials of the day, under correct daypart and station """
    menu_data = data[1]
    dayparts = data[2]

    final_menu = menu.Menu(data[0])

    # Get meal
    for daypart_id in dayparts:
        meal = menu.Meal(dayparts[daypart_id]["label"])
        # Get specials
        specials = get_specials(menu_data)
        for item in specials:
            # Make shortened item
            short_item = {}
            for field in MENU_FIELDS:
                short_item[field] = item[field]
            # Get station / add station to meal
            station_name = re.sub(RE_STATION_EXTRA, "", item["station"])
            if station_name not in meal.stations:
                station = menu.Station(station_name)
                meal.add_station(station)
            station = meal.stations[station_name]
            # Add item to station
            station.add_special(short_item)

        final_menu.add_meal(meal)
    return final_menu

def get_specials(menu):
    specials = []
    for item_id in menu:
        if menu[item_id]["special"]:
            specials.append(menu[item_id])
    return specials

# Bullseye cafe = CC, Cafe Target = TPS / TPN, TNC
def get_menu(cafe_name):
    from datetime import date
    response = get_page(cafe_name, date.today())
    data = get_data_from_page(response)
    return combine(data)

# arg0 = cafe-name, arg1 = bool show price
if __name__ == '__main__':
    menu = get_menu(sys.argv[0])
    menu.print(sys.argv[1])
