import pandas as pd

df=pd.read_csv('../data/city.csv', encoding='gbk')
total_sum=df['population'].sum()
df['percentage']=df['population']/total_sum
print(df)
city_name_list=df['name'].to_list()
print(city_name_list)
print(type(city_name_list))
city_percentage_list=df['percentage'].to_list()
print(type(city_percentage_list))
