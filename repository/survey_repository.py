import threading
from typing import List

from model.survey import SurveyResult
from repository.local import ThreadLocalDataStore

dataStore = ThreadLocalDataStore()

if not hasattr(dataStore, '__surveyResults'):
    dataStore.__surveyResults = []


def get_survey_results() -> List[SurveyResult]:
    return dataStore.__surveyResults


def save_survey_result(result: SurveyResult):
    get_survey_results().append(result)


if __name__ == '__main__':
    print(dataStore.__surveyResults)
