import matplotlib.pyplot as plt
import numpy as np

# 示例数据，这里是10组数据的和
group_sums = np.array([15, 20, 25, 30, 35, 40, 45, 50, 55, 60])

# 假设每组数据的区间端点是这样的
group_edges = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

# 计算区间中点作为横轴的刻度
group_centers = (group_edges[:-1] + group_edges[1:]) / 2

# 绘制直方图
plt.figure(figsize=(10, 6))
plt.bar(group_centers, group_sums, width=(group_edges[1] - group_edges[0]) / 2, color='blue')
plt.xlabel('Group Centers')
plt.ylabel('Sum of In-Degrees')
plt.title('In-Degree Sum by Group')
plt.xticks(group_centers)
plt.show()