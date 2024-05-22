import os
from typing import List
from model.survey import Question, Answer, SurveyResult
from model.agent import Agent
import repository.survey_repository as sv_repo
import repository.agent_repository as ag_repo
import random
import json

with open(os.path.dirname(__file__) + '/../data/answer.json', 'r', encoding='utf-8') as file:
    # 读取文件内容并解析JSON数据
    data = json.load(file)
    answers: List[Answer] = [Answer(**item) for item in data]


def survey_simulate(questions: List[Question]) -> List[SurveyResult]:
    sn = ag_repo.get_social_network()
    for respondent in sn.get_agents():
        sv_repo.save_survey_result(respondent.id, answers)
    return sv_repo.get_survey_results()


def survey_from_agent(questions: List[Question], respondent: Agent):
    # 获取respondent关注的所有agent，并计算agent的in_degree, 和关注权重。
    # 查询关注的这些agents的答卷，筛选出有答卷的agents，并计算其权重。
    # 根据权重计算出标准正态分布的sigma。
    # 迭代每一个问题，加权计算关注的agents的答题的μ，并根据μ和σ，生成respondent的结果。
    nweight = {}
    nodes = []
    # for (from_id, to_id, attrs) in sn.get_relations().out_edges(respondent.id):
    #     nodes.append(sv_repo.index_survey[to_id])
    # if nodes:
    #     result = random.choice(nodes)
    # sv_repo.save_survey_result(respondent.id, answers)
