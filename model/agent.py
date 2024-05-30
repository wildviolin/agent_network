import numpy as np
import uuid


class Agent:
    """
    Agent class represents an agent's profile

    Attributes:
        label: Usually a series number to plot.
        city_code: The city code of the agent.
        age: Age of the agent.
        gender: Gender of the agent, 1 represents male and 0 for female.
        social_ability: Social ability represents the index of an agent's ability to connect to other agents, [0,1].
        attention_limit: Attention limitation is a specific manifestation of social ability, representing the maximum
            number of other agents an agent can connect to.
        random_preference: An index represents the probability of an agent to discover agents randomly.
        attractiveness: The natural growth-generated attractiveness indicates that agents with higher attractiveness
            are more likely to receive connections from other agents.
        mobility: The agents with higher mobility have high probability to discover agents cross cities.
    """
    def __init__(self, label=None, city_code=None, age=None, gender=None, social_ability=None,
                 random_preference=None):
        self.id = str(uuid.uuid4()).replace('-', '')
        self.label = label
        self.city_code = city_code
        self.age = age if age is not None else np.random.randint(15, 64)
        self.gender = gender if gender is not None else np.random.randint(2)
        self.social_ability = max(
            min(social_ability if social_ability is not None else np.random.normal(0.5, 0.15), 1), 0)
        self.attention_limit = int(self.social_ability * 10)

        # 随机性偏好越低，越倾向于优先链接。越高越倾向于随机链接节点。
        self.random_preference = max(
            min(random_preference if random_preference is not None else np.random.normal(0.25, 0.1), 1), 0)
        self.attractiveness = self.calculate_attractiveness()
        self.mobility = self.calculate_mobility()
        self.priority_factor = 1

    def calculate_attractiveness(self):
        growth = 40 if self.gender == 1 else 30
        return min(np.random.binomial(max(self.age, growth), 0.5) / growth, 1)

    # 计算移动性，移动性越高，越倾向于链接不同城市智能体，移动性越低越倾向于链接同城智能体
    def calculate_mobility(self):
        truncate = 40
        return min(np.random.binomial(max(self.age, truncate), 0.1) / truncate, 1)
