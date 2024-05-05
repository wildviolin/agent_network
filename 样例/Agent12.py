import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd

df_city=pd.read_csv('../data/city.csv', encoding='gbk')
total_sum=df_city['population'].sum()
df_city['percentage']=df_city['population']/total_sum
#城市列表
city_codes=df_city['name'].to_list()
#城市比例列表
city_population_distribution=df_city['percentage'].to_list()

#参数
def agent_num():
    total_agents=int(input("请输入生成智能体的数量:"))
    return total_agents



class Agent:
    def __init__(self,agent_id,city_code,age=None,gender=None,social_ability=None,random_preference=None):
        self.id=agent_id
        self.city=city_code
        self.age=age if age is not None else np.random.randint(15,64)
        self.gender=gender if gender is not None else np.random.randint(2)#1男0女
        self.social_ability=social_ability if social_ability is not None else np.random.normal(0.5,0.15)
        self.maxOutBound=self.social_ability*10
        self.random_preference=random_preference if random_preference is not None else np.random.normal(0.5,0.15)
        self.attractiveness=self.calculate_attractiveness()
        self.mobility=self.calculate_mobility()
        self.in_degree=0
        self.out_degree=0
        self.priority_factor=1/total_agents

    def calculate_attractiveness(self):
        if self.gender==1:
            n=40
            if self.age<=n:
                n=self.age
        else:
            n=30
            if self.age<=n:
                n=self.age
        return np.sum([np.random.binomial(1, 0.5) for _ in range(n)])/n

    def calculate_mobility(self):
        return np.sum([np.random.binomial(1, 0.5) for _ in range(50)])/50

class Network:
    def __init__(self,total_agents,city_codes,city_population_distribution):
        self.agents=[]
        self.edges={}

        #分配智能体到各个城市
        for city_code,pop_ratio in zip(city_codes,city_population_distribution):
            num_agents_in_city=int(total_agents*pop_ratio)
            for _ in range(num_agents_in_city):
                agent=Agent(len(self.agents)+1,city_code)
                self.agents.append(agent)
        self.G = nx.DiGraph()

    #生成关系
    def generate_relations(self):

        # 添加节点
        for agent in self.agents:
            self.G.add_node(agent.id, agent=agent)
        while True:
            #对没有达到maxOutBound的节点进行处理
            for node_A in self.agents:
                if node_A.out_degree<node_A.maxOutBound:
                    random_value1=np.random.rand()
                    random_value2=np.random.rand()
                    if random_value1<node_A.random_preference:
                        if random_value2<node_A.mobility:
                            #从城市中按照吸引力系数为权重随机选择一个节点作为目的节点B
                            node_B=self.select_node_in_city(node_A.city,node_A)
                        else:
                            #从所有节点中按照吸引力系数为权重随机挑选一个节点作为目的节点B
                            node_B=self.select_node_globally(node_A)
                    else:
                        #按照入度优先选择一个节点作为目的节点B
                        node_B=self.select_by_in_degree(node_A)

                    #处理边的创建和权重的增加
                    updates={(node_A.id,node_B.id):{'weight':1}}
                    self.update_edges(self.G,updates)
                    #更新节点A的出度
                    node_A.out_degree+=1
                #退出条件
                if all(agent.out_degree>=agent.maxOutBound for agent in self.agents):
                    break
            pos = nx.spring_layout(self.G, k=0.5, scale=5)
            nx.draw(self.G,
                    pos=pos,
                    with_labels=True,
                    font_size=6,
                    arrows=True)
            plt.axis("off")
            plt.show()
            break

    def select_agent_by_attractiveness(self,dict,random1):
        df = pd.DataFrame(columns=['id', 'attractiveness'])
        df = pd.DataFrame(dict, columns=['id', 'attractiveness'])
        total_sum = df['attractiveness'].sum()
        new_column_values = []
        for index, row in df.iterrows():
            if index == 0:
                new_value = 0
                new_column_values.append(new_value)
            else:
                new_value = df.head(index)['attractiveness'].sum() / total_sum
                new_column_values.append(new_value)
        df['起始值'] = new_column_values
        df['终止值'] = df['起始值'].shift(-1)
        df.iloc[len(dict) - 1, 3] = 1
        index = 0
        for index, row in df.iterrows():
            a_val = row['起始值']
            b_val = row['终止值']
            index += 1
            if random1 - a_val >= 0 and b_val - random1 > 0:
                break
        return df.iloc[index - 1]['id']


    def select_node_in_city(self,city_code,node_A):
        if self.edges:
             node_B=self.first_add()
        else:
            city_agents=[agent for agent in self.agents if agent.city==city_code and agent.id!=node_A.id]
            dict=[]
            random1=random.random()
            for agent in city_agents:
                value1=agent.id
                value2=agent.attractiveness
                example={'id':value1,'attractiveness':value2}
                dict.append(example)
            node_B_id=self.select_agent_by_attractiveness(dict,random1)
            for agent in self.agents:
                if agent.id==node_B_id:
                    node_B=agent
                    break
        # 更新节点B的入度数
        node_B.in_degree += 1
        # 更新节点B的优先因子
        sum = 0
        for agent in self.agents:
            sum += agent.in_degree * agent.attractiveness
        node_B.priority_factor = node_B.in_degree * node_B.attractiveness / sum
        return  node_B

    def select_node_globally(self,node_A):
        if self.edges:
            node_B = self.first_add()
        else:
            global_agents=[agent for agent in self.agents if agent.id != node_A.id]
            dict = []
            random1 = random.random()
            for agent in global_agents:
                value1 = agent.id
                value2 = agent.attractiveness
                example = {'id': value1, 'attractiveness': value2}
                dict.append(example)
            node_B_id = self.select_agent_by_attractiveness(dict, random1)
            for agent in self.agents:
                if agent.id==node_B_id:
                    node_B=agent
                    break
        # 更新节点B的入度数
        node_B.in_degree += 1
        # 更新节点B的优先因子
        sum=0
        for agent in self.agents:
            sum+=agent.in_degree*agent.attractiveness
        node_B.priority_factor = node_B.in_degree * node_B.attractiveness / sum
        return node_B

    def select_by_in_degree(self,node_A):
        if self.edges:
            node_B = self.first_add()
        else:
            new_agents=[agent for agent in self.agents if agent.id != node_A.id]
            sorted_agents=sorted(new_agents,key=lambda x:x.priority_factor,reverse=True)
            node_B=sorted_agents[0]
        # 更新节点B的入度数
        node_B.in_degree += 1
        # 更新节点B的优先因子
        sum = 0
        for agent in self.agents:
            sum += agent.in_degree * agent.attractiveness
        node_B.priority_factor = node_B.in_degree * node_B.attractiveness / sum
        return node_B

    #第一次添加节点
    def first_add(self):
        node_B = np.random.choice(self.agents)
        return node_B
    def update_edges(self,G,updates):
        for (u,v),attrs in updates.items():
            if (u,v) in G.edges():
                attrs['weight']+=1
                G[u][v].update(attrs)
            else:
                G.add_edge(u,v,**attrs)



total_agents=agent_num()
network=Network(total_agents,city_codes,city_population_distribution)
network.generate_relations()




