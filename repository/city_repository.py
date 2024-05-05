# from model.city import City
import pandas as pd
import os


class CityRepository:
    # cities=City()
    def __init__(self):
        self.cities = pd.read_csv(os.path.dirname(__file__) + r'/../data/city.csv', encoding='gbk')

    def find_all(self):
        return self.cities

    def find_by_city_names(self, names):
        return self.cities[self.cities['name'].isin(names)]

    def find_by_city_codes(self, codes):
        return self.cities[self.cities['code'].isin(codes)]

    def find_by_city_code(self, code):
        return self.cities.query(f"code == '{code}'")


cityRepository = CityRepository()
