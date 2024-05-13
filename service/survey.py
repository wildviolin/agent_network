from typing import List
from model.survey import Question, Answer, SurveyResult
from model.agent import Agent, SocialNetwork
import repository.survey_repository as sv_repo


def survey_simulate(questions: List[Question], sn: SocialNetwork) -> List[SurveyResult]:
    results = [survey_from_agent(questions, sn, respondent, results) for respondent in sn.get_agents()]
    return results


def survey_from_agent(questions: List[Question], sn: SocialNetwork, respondent: Agent) -> SurveyResult:
    # 获取respondent关注的所有agent，并计算agent的in_degree, 和关注权重。

    return


