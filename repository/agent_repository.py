from typing import List, Dict

from networkx import DiGraph

from model.agent import Agent
from repository.local import ThreadLocalDataStore

dataStore = ThreadLocalDataStore()

if not hasattr(dataStore, '__socialNetwork'):
    dataStore.__socialNetwork = DiGraph()


def get_social_network() -> DiGraph:
    return dataStore.__socialNetwork


def add_agent(agent: Agent):
    get_social_network().add_node(agent.id, agent=agent)


def all_agents_list() -> List[Agent]:
    return [data['agent'] for node, data in get_social_network().nodes(data=True)]


def all_agents_dict() -> Dict[str, Agent]:
    return {node: data['agent'] for node, data in get_social_network().nodes(data=True)}


def count_agents() -> int:
    return get_social_network().number_of_nodes()


def agents_exclude_one(agent_id: str) -> List[Agent]:
    return [agent for agent in all_agents_list() if agent.id != agent_id]


def agent_out_degree(agent_id: str) -> int:
    social_network = get_social_network()
    return social_network.out_degree[agent_id]


def agent_in_degree(agent_id: str) -> int:
    social_network = get_social_network()
    return social_network.in_degree[agent_id]


def update_relation(source: Agent, target: Agent):
    # 更新node_from的出度和node_to的入度
    # 检查边是否存在
    if not get_social_network().has_edge(source.id, target.id):
        # 更新节点B的优先因子
        get_social_network().add_edge(source.id, target.id, weight=1)
        target.priority_factor = agent_in_degree(target.id)
    else:
        e = get_social_network()[source.id][target.id]
        e['weight'] += 1


def relation_weight_by_agents(source: Agent, target: Agent):
    return get_social_network()[source.id].get(target.id, {}).get('weight', 0)


def sum_in_weight_from_sources(target: Agent, sources: List[Agent]):
    # 计算源节点到某一目标节点的权重总和。
    # 对于指向target节点的sources节点中的每一个节点s：
    # 节点s的入度越高对target的吸引力越高，s对target的关注越多对target吸引力越高。
    return sum(agent_in_degree(s.id) + relation_weight_by_agents(s, target) for s in sources)
