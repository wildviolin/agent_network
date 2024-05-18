from typing import List
from networkx import DiGraph
import numpy as np
import uuid


class Agent:
    def __init__(self, label=None, city_code=None, age=None, gender=None, social_ability=None,
                 random_preference=None):
        self.id = str(uuid.uuid4()).replace('-', '')
        self.label = label
        self.city = city_code
        self.age = age if age is not None else np.random.randint(15, 64)
        self.gender = gender if gender is not None else np.random.randint(2)  #1男0女
        self.social_ability = max(
            min(social_ability if social_ability is not None else np.random.normal(0.5, 0.15), 1), 0)
        self.max_out_bound = int(self.social_ability * 10)

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


class SocialNetwork:

    def __init__(self):
        self.__agents: List[Agent] = []
        self.__graph = DiGraph()

    def add_agent(self, agent: Agent):
        self.__agents.append(agent)
        self.__graph.add_node(agent.id, agent=agent)

    def get_agents(self) -> List[Agent]:
        return self.__agents

    def get_relations(self) -> DiGraph:
        return self.__graph

    def update_relation(self, source: Agent, target: Agent):
        # 更新node_from的出度和node_to的入度
        # 检查边是否存在
        if not self.__graph.has_edge(source.id, target.id):
            # 更新节点的出入度数
            source.out_degree += 1
            target.in_degree += 1
            # 更新节点B的优先因子
            target.priority_factor = target.in_degree
            self.__graph.add_edge(source.id, target.id, weight=1)
        else:
            e = self.__graph[source.id][target.id]
            e['weight'] += 1

    def get_relation_weight_from_agents(self, source: Agent, target: Agent):
        return self.__graph[source.id].get(target.id, {}).get('weight', 0)

    def sum_in_weight_by_sources(self, target: Agent, sources: List[Agent]):
        # 计算源节点到某一目标节点的权重总和。
        # 对于指向target节点的sources节点中的每一个节点s：
        # 节点s的入度越高对target的吸引力越高，s对target的关注越多对target吸引力越高。
        return sum(s.in_degree + self.get_relation_weight_from_agents(s, target)
                   for s in sources)
