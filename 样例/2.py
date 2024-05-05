import json

person={"name":"job","age":32,"telp":['12345','123456'],"isonly":True}
print(person)
#person-->json
#indent=4让字符串可以进行缩进
#sort_keys=True让字符串按照字母顺序排序
job=json.dumps(person,indent=4,sort_keys=True)
print(job)
print(type(job))

json.dump(person,open('data.json','w'),indent=4,sort_keys=True)

#从json转换为python对象
#json.load(fp)  json.loads()
person1=json.load(open('data.json','r'))
print(person1)
person2=json.loads(job)
print(person2)
s='["A",1,"age",{"age":15,"hobby":"computer"}]'
s1=json.loads(s)
print(s1)