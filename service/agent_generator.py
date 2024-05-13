import numpy as np
import random
from model.agent import Agent, SocialNetwork


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


def init_social_network(cities, total):
    sn = SocialNetwork()
    # 城市比例系数
    cities_portion = calculate_city_ratio(cities)
    city_num = len(cities)
    c = 0
    n = 0
    agent_num = 0
    for code, pop in cities_portion.items():
        c += 1
        if c == city_num:
            agent_num_in_city = total - n
        else:
            agent_num_in_city = int(total * pop)
            n += agent_num_in_city

        for _ in range(agent_num_in_city):
            agent_num += 1
            agent = Agent(label=str(agent_num), city_code=code)
            sn.add_agent(agent)
    return sn


def build_relations(sn: SocialNetwork):
    agents_candidate = {obj.id: obj for obj in sn.get_agents()}
    while agents_candidate:
        node_a = agents_candidate[random.choice(list(agents_candidate.keys()))]
        if node_a.out_degree >= min(node_a.max_out_bound, len(sn.get_agents()) - 1):
            agents_candidate.pop(node_a.id, None)
            continue

        threshold_random = np.random.rand()
        threshold_mobility = np.random.rand()
        # 高移动性在所有城市中选择节点
        others = [agent for agent in sn.get_agents() if agent.id != node_a.id]
        to_agents = [agent for agent in others if
                     threshold_mobility < node_a.mobility or agent.city == node_a.city]
        if not to_agents:
            print("to_agents none")
        if threshold_random < node_a.random_preference:  # 高随机性按吸引力选择节点
            node_b = preference_select(to_agents if to_agents else others, "attractiveness", normalized=False)
        else:
            node_b = comprehensive_preference(sn, to_agents if to_agents else others, node_a)

        sn.update_relation(node_a, node_b)

        if node_a.out_degree >= node_a.max_out_bound:
            agents_candidate.pop(node_a.id, None)
            continue


def comprehensive_preference(sn: SocialNetwork, to_agents, from_agent):
    total_attr = sn.sum_in_weight_by_sources(from_agent, to_agents)
    if total_attr == 0:
        return np.random.choice(to_agents)
    bound = 0
    seed = random.random()
    node_to = None
    for a in to_agents:
        bound_next = (bound + (
                a.in_degree + sn.get_relation_weight_from_agents(a, from_agent)
                ) / total_attr)
        if bound <= seed <= bound_next:
            node_to = a
            break
        bound = bound_next
    if node_to is None:
        node_to = np.random.choice(to_agents)
    return node_to
