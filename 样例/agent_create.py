import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random


class Agent:
    def __init__(self,agent_id):
        self.id=agent_id #智能体的唯一标识符
        self.attributes={}#智能体属性
        self.decision_model=None #智能体的决策模型

    def set_age(self,attribute_name,attribute_value):
        ''' 设置智能体年龄'''
        self.attributes[attribute_name]=attribute_value

    def get_age(self,attribute_name):
        '''获取智能体的年龄'''
        return self.attributes.get(attribute_name)

    def set_gender(self, attribute_name, attribute_value):
        ''' 设置智能体性别'''
        self.attributes[attribute_name] = attribute_value

    def get_gender(self, attribute_name):
        '''获取智能体的性别'''
        return self.attributes.get(attribute_name)

    def set_social_ability(self, attribute_name, attribute_value):
        ''' 设置智能体的社交能力系数'''
        self.attributes[attribute_name] = attribute_value

    def get_social_ability(self, attribute_name):
        '''获取智能体的社交能力系数'''
        return self.attributes.get(attribute_name)

    def set_randomness_preference(self, attribute_name, attribute_value):
        ''' 设置智能体随机性偏好'''
        self.attributes[attribute_name] = attribute_value

    def get_randomness_preference(self, attribute_name):
        '''获取智能体的随机性偏好'''
        return self.attributes.get(attribute_name)

    def set_attraction_cofficient(self, attribute_name, attribute_value):
        ''' 设置智能体吸引力系数'''
        self.attributes[attribute_name] = attribute_value

    def get_attraction_cofficient(self, attribute_name):
        '''获取智能体的吸引力系数'''
        return self.attributes.get(attribute_name)

    def set_in_degree(self, attribute_name, attribute_value):
        ''' 设置智能体入度数'''
        self.attributes[attribute_name] = attribute_value

    def get_in_degree(self, attribute_name):
        '''获取智能体的入度数'''
        return self.attributes.get(attribute_name)

    def set_city(self,attribute_name, attribute_value):
        ''' 设置智能体所属城市'''
        self.attributes[attribute_name] = attribute_value

    def get_city(self, attribute_name):
        '''获取智能体所属城市'''
        return self.attributes.get(attribute_name)

    def make_decision(self,questionnaire):
        '''根据问卷内容做出决策'''
        pass

    def interact_with_neighbors(self):
        '''与邻居智能体进行交互'''
        pass

    def fill_questionnaire(self,questionnaire):
        '''填写问卷并返回决策结果'''
        pass

#生成智能体及其生物体特征
def gengerate_agents(total_agents,coefficients):
    agents = []
    for city, coeff in coefficients.items():
        # 按照城市比例系数生成智能体数量
        num_city_agents = int(total_agents * coeff)
        for _ in range(num_city_agents):
            agent=Agent(len(agents)+1)
            # 生成智能体的生物特征
            agent.set_age('age',np.random.uniform(15, 65))
            agent.set_gender('gender',np.random.randint(2))
            agent.set_social_ability('social_ability',np.random.normal(0.5, 0.15))
            agent.set_randomness_preference('randomness_preference',np.random.normal(0.5, 0.15))
            agent.set_attraction_cofficient('attraction_cofficient',np.sum([np.random.binomial(1, 0.5) for _ in range(30)]))
            agent.set_in_degree('in_degree',0)
            agent.set_city('city',city)
            # 添加智能体到列表
            agents.append(agent)
    return agents

#根据BA模型生成网络关系
def generate_network(agents,m):#m表示每次添加节点加入的边数
    G=nx.Graph()

    #添加节点
    for agent in agents:
       G.add_node(agent.id,agent=agent)

    #根据BA模型生成边
    for node in G.nodes():
        # 随机性:随机生成一个节点进行连接
        neighbor = np.random.choice(list(G.nodes()))
        while neighbor == node:
            neighbor = np.random.choice(list(G.nodes()))
        G.add_edge(node, neighbor)
        #跟新入度数
        for agent in agents:
            if agent.id==neighbor:
                degree=agent.get_in_degree('in_degree')
                agent.set_in_degree('in_degree',degree+1)

        #随机性:规则
        #根据优先因子选择连边:城市系数*入度系数*吸引力系数
        scores = []
        for neighbor1 in agents:
            city_score =city_coefficients[neighbor1.get_city('city')]
            in_degree_score = neighbor1.get_in_degree('in_degree')
            attraction_score = neighbor1.get_attraction_cofficient('attraction_cofficient')
            score = city_score * in_degree_score * attraction_score
            scores.append((neighbor1, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        neighbor1 = scores[0][0]
        if neighbor1.id==node or neighbor1.id==neighbor:
            neighbor1=scores[1][0]
            if neighbor1.id==node or neighbor1.id==neighbor:
                neighbor1=scores[2][0]
                G.add_edge(node, neighbor1.id)
                degree = neighbor1.get_in_degree('in_degree')
                neighbor1.set_in_degree('in_degree', degree + 1)
            else:
                G.add_edge(node, neighbor1.id)
                degree = neighbor1.get_in_degree('in_degree')
                neighbor1.set_in_degree('in_degree', degree + 1)
        else:
            G.add_edge(node, neighbor1.id)
            degree = neighbor1.get_in_degree('in_degree')
            neighbor1.set_in_degree('in_degree', degree + 1)

    return G
#假设的城市比例系数
city_coefficients={'CityA':0.3,'CityB':0.2,'CityC':0.4}
total_agents=100
m=2

#生成智能体
agents=gengerate_agents(total_agents,city_coefficients)

#生成网络
G=generate_network(agents,m)





pos=nx.spring_layout(G,k=0.5,scale=5)

nx.draw(G,
        pos=pos,
        with_labels=True,

        font_size=6,
        arrows=True)
plt.axis("off")
plt.show()


