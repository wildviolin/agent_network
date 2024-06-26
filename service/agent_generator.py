import numpy as np
import random
from model.agent import Agent
import repository.agent_repository as ag_repo


def calculate_city_ratio(cities):
    sum_population = cities['population'].sum()
    return {k: v for k, v in zip(cities['code'], cities['population'] / sum_population)}


def preference_select(agents, attr_name, normalized=True) -> Agent:
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
            ag_repo.add_agent(agent)


def build_relations():
    agents_candidate = ag_repo.all_agents_dict()
    while agents_candidate:  # fixme 会在此处卡死，全部城市，400节点，需要增加进度条
        node_a = agents_candidate[random.choice(list(agents_candidate.keys()))]
        if ag_repo.agent_out_degree(node_a.id) >= min(node_a.attention_limit, ag_repo.count_agents() - 1):
            agents_candidate.pop(node_a.id, None)
            continue

        threshold_random = np.random.rand()
        threshold_mobility = np.random.rand()
        # 高移动性在所有城市中选择节点
        others = ag_repo.agents_exclude_one(node_a.id)  # fixme 会在此处卡死
        to_agents = [agent for agent in others if  # fixme 会在此处卡死
                     threshold_mobility < node_a.mobility or agent.city_code == node_a.city_code]
        if not to_agents:
            print("to_agents none")
        if threshold_random < node_a.random_preference:  # 高随机性按吸引力选择节点
            node_b = preference_select(to_agents if to_agents else others, "attractiveness", normalized=False)
        else:
            node_b = comprehensive_preference(to_agents if to_agents else others, node_a)

        ag_repo.update_relation(node_a, node_b)

        if ag_repo.agent_out_degree(node_a.id) >= node_a.attention_limit:
            agents_candidate.pop(node_a.id, None)
            continue


def comprehensive_preference(to_agents, from_agent) -> Agent:
    total_attr = ag_repo.sum_in_weight_from_sources(from_agent, to_agents)
    if total_attr == 0:
        return np.random.choice(to_agents)

    weights = [ag_repo.agent_in_degree(a.id) + ag_repo.relation_weight_by_agents(a, from_agent) for a in to_agents]
    node_to = random.choices(to_agents, weights=weights, k=1)[0]

    if node_to is None:
        node_to = np.random.choice(to_agents)
    return node_to
