import networkx as nx
import numpy as np
import random
from model.agent import Agent


def calculate_city_ratio(cities):
    sum_population = cities['population'].sum()
    return {k: v for k, v in zip(cities['code'], cities['population'] / sum_population)}


def preference_select(agents, attr_name, normalized=True):
    total_attr = 1 if normalized else sum(getattr(o, attr_name) for o in agents)
    bound = 0
    seed = random.random()
    node_to = None
    for a in agents:
        bound_next = bound + getattr(a, attr_name) / total_attr
        if bound <= seed <= bound_next:
            node_to = a
            break
        bound = bound_next
    if node_to is None:
        node_to = np.random.choice(agents)
    return node_to


class NetworkGenerator:
    def __init__(self):
        self.agents = []
        self.G = nx.DiGraph()

    # 分配智能体
    def init_agents(self, cities, total):
        # 城市比例系数
        cities_portion = calculate_city_ratio(cities)
        city_num = len(cities)
        c = 0
        n = 0
        agent_id = 0
        for code, pop in cities_portion.items():
            c += 1
            if c == city_num:
                agent_num_in_city = total - n
            else:
                agent_num_in_city = int(total * pop)
                n += agent_num_in_city

            for _ in range(agent_num_in_city):
                agent_id += 1
                agent = Agent(agent_id, code)
                self.agents.append(agent)

    # 生成关系
    def build_relations(self):
        # 添加节点
        for agent in self.agents:
            self.G.add_node(agent.id, agent=agent)
        agents_candidate = {obj.id: obj for obj in self.agents}
        while agents_candidate:
            node_a = agents_candidate[random.choice(list(agents_candidate.keys()))]
            if node_a.out_degree >= min(node_a.max_out_bound,len(self.agents)-1):
                agents_candidate.pop(node_a.id, None)
                continue

            threshold_random = np.random.rand()
            threshold_mobility = np.random.rand()
            # 高移动性在所有城市中选择节点
            others = [agent for agent in self.agents if agent.id != node_a.id]
            to_agents = [agent for agent in others if
                         threshold_mobility < node_a.mobility or agent.city == node_a.city]
            if not to_agents:
                print("to_agents none")
            if threshold_random < node_a.random_preference:  # 高随机性按吸引力选择节点
                node_b = preference_select(to_agents if to_agents else others, "attractiveness", normalized=False)
            else:
                node_b = preference_select(to_agents if to_agents else others, "priority_factor", normalized=False)
            # 更新node_A的出度和node_B的入度
            # 检查边是否存在
            if not self.G.has_edge(node_a.id, node_b.id):
                # 更新节点的出入度数
                node_a.out_degree += 1
                node_b.in_degree += 1
                # 更新节点B的优先因子
                node_b.priority_factor = node_b.in_degree
                self.G.add_edge(node_a.id, node_b.id, weight=1)
            else:
                e = self.G[node_a.id][node_b.id]
                e['weight'] += 1

            if node_a.out_degree >= node_a.max_out_bound:
                agents_candidate.pop(node_a.id, None)
                continue


networkGenerator = NetworkGenerator()
