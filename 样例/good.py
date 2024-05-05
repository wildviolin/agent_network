import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

"""
智能体生成
1、输入：生成智能体的总量，分布的城市列表
2、按照城市系数比例，作为生成个体的数量做循环
3、每个城市进行循环生成智能体及其生物特征：
    年龄：默认范围15~64，均匀分布 Numpy/radom
    性别：1/0，1-0分布
    （先天）社交能力系数：0~1，正态分布，μ=0.5，σ=0.15
    随机性偏好：0~1，正态分布，μ=0.5，σ=0.15
    吸引力系数：从0岁开始，循环到30岁，每次循环叠加一个二项分布。
    入度数；
4、重新遍历所有节点，按照BA模型生成关系。
    随机性：随机
        从所有节点中随机挑选一个节点进行关注。
    随机性：规则
        优先因子：城市系数 & 入度系数 & 吸引力系数
"""

#假设的城市比例系数
city_coefficients={'CityA':0.3,'CityB':0.2,'CityC':0.4}

#生成智能体及其生物体特征
def gengerate_agents(total_agents,coefficients):
    agents=[]
    for city,coeff in coefficients.items():
        #按照城市比例系数生成智能体数量
        num_city_agents=int(total_agents*coeff)
        for _ in range(num_city_agents):
            #生成智能体的生物特征
            age=np.random.uniform(15,65)
            gender = np.random.randint(2)  # 性别取值 0 1
            social_ability = np.random.normal(0.5, 0.15)  # 社交能力系数生成均值为0.5，标准差为0.15的正态分布
            randomness_preference = np.random.normal(0.5, 0.15)  # 随机性偏好

            # 吸引力系数:从0循环到30岁，每次循环添加一个二项分布
            attraction_cofficient = np.sum([np.random.binomial(1, 0.5) for _ in range(30)])

            #初始化入度数为0
            in_degree=0

            #添加智能体到列表
            agents.append({'id':len(agents)+1,'city':city,'age':age,'gender':gender,
               'social_ability':social_ability,'randomness_preference':randomness_preference,
               'attraction_cofficient':attraction_cofficient,'in_degree':in_degree})
    return agents

#根据BA模型生成网络关系
def generate_network(agents,m):#m表示每次添加节点加入的边数
    G=nx.DiGraph()

    #添加节点
    for agent in agents:
       G.add_node(agent['id'],**agent)

    #根据BA模型生成边
    for node in G.nodes():
        #判断条件
        judging_condition=[]

        #随机性:随机生成一个节点进行连接
        existing_node = np.random.choice(list(G.nodes()))
        if(G.nodes[node]['id']!=G.nodes[existing_node]['id']):
            G.add_edge(node, existing_node)
            #跟新连接节点的入度
            G.nodes[existing_node]['in_degree'] += 1

        #随机性:规则
        #根据优先因子选择连边:城市系数*入度系数*吸引力系数
        for _ in range(m - 1):
            scores = []
            for existing_node1 in G.nodes():
                city_score = city_coefficients[G.nodes[existing_node1]['city']]
                in_degree_score = G.nodes[existing_node1]['in_degree']
                attraction_score = G.nodes[existing_node1]['attraction_cofficient']
                score = city_score * in_degree_score * attraction_score
                scores.append((existing_node1, score))
            scores.sort(key=lambda x: x[1], reverse=True)
            existing_node1 = scores[0][0]
            if (G.nodes[node]['id'] != G.nodes[existing_node1]['id'] & G.nodes[existing_node1]['id'] !=
                    G.nodes[existing_node]['id']):
                G.add_edge(node, existing_node1)
                G.nodes[existing_node1]['in_degree'] += 1
    return G
total_agents=100
m=2

#生成智能体
agents=gengerate_agents(total_agents,city_coefficients)

#生成网络
G=generate_network(agents,m)

nx.draw(G,with_labels=True)
plt.show()

