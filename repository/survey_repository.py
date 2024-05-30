from typing import List, Dict

from model.survey import SurveyResult, Answer
from model.agent import Agent
from repository.local import ThreadLocalDataStore


def get_survey_results() -> {}:
    return ThreadLocalDataStore().get_survey_results()


def all_survey_results() -> List[SurveyResult]:
    res = []
    for k, v in get_survey_results().items():
        res.append(SurveyResult(agent_id=k, results=list(v.values())))
    return res


def survey_results_by_agent_id(agent_id: str) -> SurveyResult:
    return SurveyResult(agent_id=agent_id, results=list(get_survey_results()[agent_id].values()))


def survey_results_from_agents(agent_ids: List[str]) -> List[SurveyResult]:
    filtered_results = [result for result in all_survey_results() if result.agent_id in agent_ids]
    return filtered_results


def answer_by_agent_id_question_id(agent_id: str, question_id: str) -> Answer | None:
    if agent_id not in get_survey_results():
        return None
    if question_id not in get_survey_results()[agent_id]:
        return None
    return get_survey_results()[agent_id][question_id]


def save_survey_answer(agent_id: str, answer: Answer):
    if agent_id not in get_survey_results():
        get_survey_results()[agent_id] = {}
    get_survey_results()[agent_id][answer.question_id] = answer


def get_joint_options_by_question(question_id: str) -> List | None:
    if question_id in ThreadLocalDataStore().get_joint_options():
        return ThreadLocalDataStore().get_joint_options()[question_id]
    else:
        return None


def flush_joint_options(question_id: str, options: List):
    ThreadLocalDataStore().get_joint_options()[str] = options


if __name__ == '__main__':
    print(get_survey_results())
