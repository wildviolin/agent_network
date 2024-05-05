import numpy as np


class Agent:
    def __init__(self, agent_id, city_code, age=None, gender=None, social_ability=None,
                 random_preference=None):
        self.id = agent_id
        self.city = city_code
        self.age = age if age is not None else np.random.randint(15, 64)
        self.gender = gender if gender is not None else np.random.randint(2)  #1男0女
        self.social_ability = social_ability if social_ability is not None else np.random.normal(0.5, 0.15)
        self.social_ability = 0 if self.social_ability < 0 else self.social_ability
        self.social_ability = 1 if self.social_ability > 1 else self.social_ability
        self.max_out_bound = int(self.social_ability * 20)

        # 随机性偏好越低，越倾向于优先链接。越高越倾向于随机链接节点。
        self.random_preference = max(
            min(random_preference if random_preference is not None else np.random.normal(0.25, 0.1), 1), 0)
        self.attractiveness = self.calculate_attractiveness()
        self.mobility = self.calculate_mobility()
        self.in_degree = 0
        self.out_degree = 0
        self.priority_factor = 1

    def calculate_attractiveness(self):
        growth = 40 if self.gender == 1 else 30
        return min(np.random.binomial(max(self.age, growth), 0.5) / growth, 1)

    # 计算移动性，移动性越高，越倾向于链接不同城市智能体，移动性越低越倾向于链接同城智能体
    def calculate_mobility(self):
        truncate = 40
        return min(np.random.binomial(max(self.age, truncate), 0.1) / truncate, 1)
