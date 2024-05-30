import pandas as pd
import os
from threading import Lock


class CityRepository:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CityRepository, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.cities = pd.read_csv(os.path.dirname(__file__) + r'/../data/city.csv', encoding='gbk')
        self.__initialized = True

    def find_all(self):
        return self.cities

    def find_by_city_names(self, names):
        return self.cities[self.cities['name'].isin(names)]

    def find_by_city_codes(self, codes):
        return self.cities[self.cities['code'].isin(codes)]

    def find_by_city_code(self, code):
        return self.cities.query(f"code == '{code}'")


# 使用单例模式
city_repository = CityRepository()
