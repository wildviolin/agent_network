from typing import List

from model.survey import SurveyResult, Answer
from repository.local import ThreadLocalDataStore

dataStore = ThreadLocalDataStore()

if not hasattr(dataStore, '__surveyResults'):
    dataStore.__survey_results = []
    dataStore.index_survey = {}


def get_survey_results() -> List[SurveyResult]:
    return dataStore.__survey_results


def save_survey_answer(agent_id: str, answer: Answer):
    if not dataStore.index_survey[agent_id]:
        dataStore.index_survey[agent_id] = {}
    dataStore.index_survey[agent_id][answer.questionId] = answer

def save_survey_result(agent_id: str, answers: List[Answer]):
    result = SurveyResult()
    result.agentId = agent_id
    result.results = answers
    get_survey_results().append(result)
    dataStore.index_survey[result.agentId] = {}
    for item in result.results:
        dataStore.index_survey[result.agentId][item.questionId] = item


if __name__ == '__main__':
    print(dataStore.__survey_results)
