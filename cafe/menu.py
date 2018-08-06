
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
            meal_string = '\033[4m{:^30}\033[0m\n\n'.format((meal.name).upper())
            printout += meal_string
            for station in meal.stations:
                meal_string = '{:^20}\n'.format((meal.stations[station].name).title())
                #printout += "\t" + meal.stations[station].name + "\n"
                printout += meal_string
                for special in meal.stations[station].specials:
                    # TODO - uppercase first letter
                    printout += "\t\t" + special["label"] + "\t" + special["price"] + "\n"
            printout += "\n"
        return printout
    
    def print(self, price):
        printout = ""
        for meal in self.meals:
            meal_string = '\033[4m{:^30}\033[0m\n\n'.format((meal.name).upper())
            printout += meal_string
            for station in meal.stations:
                meal_string = '{:^20}\n'.format((meal.stations[station].name).title())
                #printout += "\t" + meal.stations[station].name + "\n"
                printout += meal_string
                for special in meal.stations[station].specials:
                    # TODO - uppercase first letter
                    #printout += "\t\t" + special["label"]
                    printout += "{:>10s}".format(special["label"].title())
                    if (price):
                        #printout += "\t" + special["price"]
                        printout += "{:>10s}".format(special["price"])
                    printout += "\n"
            printout += "\n"
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