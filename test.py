from pydantic import BaseModel, Field

class MyModel(BaseModel):
    name: str
    description: str = Field(default=None, alias='desc')  # 可以为 None 的字段

    class Config:
        # 允许通过字段名来设置字段的值
        allow_population_by_field_name = True
        # 定义 None 值在序列化时的行为
        json_encoders = {
            dict: lambda v: {k: None if v[k] is None else v[k] for k in v}
        }

# 创建一个实例
model_instance = MyModel(name='Example')

# 序列化为 JSON
json_output = model_instance.json()
print(json_output)  # 输出: {"name": "Example"}