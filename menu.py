
class Menu:
    def __init__(self, cafe_name):
        self.cafe_name = cafe_name
        self.meals = []
    
    # Will need to always add in right order
    def add_meal(self, meal):
        self.meals.append(meal)

    def __str__(self):
        printout = ""
        for meal in self.meals:
            printout += meal.name + "\n"
            for station in meal.stations:
                printout += "\t" + meal.stations[station].name + "\n"
                for special in meal.stations[station].specials:
                    printout += "\t\t" + special["label"] + "\n"
        return printout

class Meal:
    def __init__(self, name):
        self.name = name
        self.stations = {}

    #TODO sort stations before adding items
    def add_station(self, station):
        self.stations[station.name] = station

    #def get_stations(self):
        #return self.stations.sort()

class Station:
    def __init__(self, name):
        self.name = name
        # List of objects with properties
        self.specials = []

    def add_special(self, dish):
        self.specials.append(dish)