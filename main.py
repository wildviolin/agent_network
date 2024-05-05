import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from service.agent_generator import networkGenerator as netGen
from repository.city_repository import cityRepository as cityRepo


def input_city_names():
    df_city = cityRepo.find_all()
    all_city_codes = df_city['name'].to_list()
    print(all_city_codes)
    input_str = input("请选择要生成的智能体城市并用空格分隔:")
    names = input_str.split()
    return names


# 提供方法来确定生成智能体的总量
def input_total_num():
    total_agents = int(input("请输入生成智能体的数量:"))
    return total_agents


def draw_network():
    pos = nx.spring_layout(netGen.G, k=0.5, scale=5)
    nx.draw(netGen.G,
            pos=pos,
            with_labels=True,
            font_size=6,
            arrows=True)
    plt.axis("off")
    plt.show()
    plt.savefig("output/network.png")


# 生成入度直方图
def draw_in_degree_histogram():
    # 统计每个智能体的入度数
    in_degree_counts = {}
    for agent in netGen.agents:
        if agent.in_degree in in_degree_counts:
            in_degree_counts[agent.in_degree] += 1
        else:
            in_degree_counts[agent.in_degree] = 1
    # 绘制直方图
    plt.bar(in_degree_counts.keys(), in_degree_counts.values(), color='blue')
    plt.xlabel('In-Degree')
    plt.ylabel('Frequency')
    plt.title('In-Degree Distribution of Agents')
    plt.show()
    plt.savefig("output/degree.png")


# 排序生成入度直方图
def draw_histogram_bins():
    # 获取所有智能体的入度并排序
    sorted_in_degrees = sorted([agent.in_degree for agent in netGen.agents], reverse=True)
    target_bins = input("请输入期望的组数")
    # 如果未指定target_bins，自动设置为列表长度的平方根作为起始初始值
    # 以获得较平均的分组
    if target_bins == "":
        target_bins = int(len(sorted_in_degrees) ** 0.5)
    target_bins = int(target_bins)
    # 确保目标组数不超过列表长度
    target_bins = min(target_bins, len(sorted_in_degrees))
    # 计算每组的理想大小和最后一组的额外元素
    group_size = len(sorted_in_degrees) // target_bins
    remainder = len(sorted_in_degrees) % target_bins
    # 每组数据之和
    bins_sums = []
    # 开始指针
    start_index = 0
    # 区间列表
    group_edges = [0]
    for i in range(target_bins):
        # 最后一组可能比其他组多一个元素
        end_index = start_index + group_size + (1 if i < remainder else 0)
        bin_sum = sum(sorted_in_degrees[start_index:end_index])
        bins_sums.append(bin_sum)
        group_edges.append(end_index)
        start_index = end_index
    group_edges = np.array(group_edges)
    # 计算区间中点作为横轴的刻度
    group_centers = (group_edges[:-1] + group_edges[1:]) / 2
    plt.figure(figsize=(10, 6))
    plt.bar(group_centers, bins_sums, width=(group_edges[1] - group_edges[0]) / 2, color='blue')
    plt.xlabel('Group Centers')
    plt.ylabel('Sum of In-Degrees')
    plt.title('In-Degree Sum by Group')
    plt.xticks(group_centers)
    plt.show()


# 生成出度直方图
def generate_out_degree_histogram(self):
    # 统计每个智能体的出度数
    out_degree_counts = {}
    for agent in self.agents:
        if agent.out_degree in out_degree_counts:
            out_degree_counts[agent.out_degree] += 1
        else:
            out_degree_counts[agent.out_degree] = 1
    # 绘制直方图
    plt.bar(out_degree_counts.keys(), out_degree_counts.values(), color='blue')
    plt.xlabel('Out-Degree')
    plt.ylabel('Frequency')
    plt.title('Out-Degree Distribution of Agents')
    plt.show()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    input_cities = input_city_names()
    cities = cityRepo.find_all() if len(input_cities) == 0 else cityRepo.find_by_city_names(input_cities)
    total = input_total_num()

    netGen.init_agents(cities, total)
    netGen.build_relations()

    draw_network()
    draw_in_degree_histogram()
    draw_histogram_bins()

    # todo 画一个吸引力系数的直方图
    # todo 画一个移动力系数的直方图
    # todo 画一个随机性偏好的直方图
