from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Type(Enum):
    SINGLE_SELECT = "SINGLE_SELECT"
    MULTI_SELECT = "MULTI_SELECT"
    SCORE_SINGLE_SELECT = "SCORE_SINGLE_SELECT"
    SCORE_MULTI_SELECT = "SCORE_MULTI_SELECT"
    SCORE_SLIDE = "SCORE_SLIDE"
    SINGLE_EVALUATION = "SINGLE_EVALUATION"
    MULTI_EVALUATION = "MULTI_EVALUATION"
    AUTO_FILL = "AUTO_FILL"
    DATE = "DATE"
    DISTRICT_CN = "DISTRICT_CN"
    LOCATION = "LOCATION"
    ADDRESS = "ADDRESS"
    MAX_DIFF = "MAX_DIFF"
    KANO = "KANO"
    JOINT_ANALYSIS = "JOINT_ANALYSIS"
    TEXT = "TEXT"


class Question(BaseModel):
    class Config:
        populate_by_name = True
        json_encoders = {
            Type: lambda t: t.value,
        }

    class Configuration(BaseModel):
        class KanoQuestion(BaseModel):
            class Title(BaseModel):
                id: Optional[str] = None
                description: str

            class Option(BaseModel):
                description: Optional[str] = None
                baseScore: int

            positive: Title
            negative: Title
            options: List[Option]

        class MaxDiffQuestion(BaseModel):
            class Title(BaseModel):
                id: Optional[str] = None
                description: str

            class Option(BaseModel):
                id: Optional[str] = None
                description: str

            task_number: int = Field(..., alias='taskNumber')
            attribute_number: int = Field(..., alias='attributeNumber')
            positive: Title
            negative: Title
            options: List[Option]

        class JointAnalysisQuestion(BaseModel):
            class Option(BaseModel):
                id: str
                title: Optional[str] = None

                class LevelOption(BaseModel):
                    id: Optional[str] = None
                    title: str

                level_options: List[LevelOption] = Field(..., alias='levelOptions')

            choose_nothing_label: Optional[str] = Field(default=None, alias='chooseNothingLabel')
            allow_choose_nothing: bool = Field(..., alias='allowChooseNothing')
            conceptual_number: int = Field(..., alias='conceptualNumber')
            task_number: int = Field(..., alias='taskNumber')
            options: List[Option]

        required: Optional[bool] = None
        min_mark: Optional[int] = Field(default=None, alias='minMark')
        max_mark: Optional[int] = Field(default=None, alias='maxMark')
        min_mark_label: Optional[str] = Field(default=None, alias='minMarkLabel')
        max_mark_label: Optional[str] = Field(default=None, alias='maxMarkLabel')
        preset_answers: Optional[str] = Field(default=None, alias='presetAnswers')
        allow_other_answers: Optional[bool] = Field(default=None, alias='allowOtherAnswers')
        district_cn_level: Optional[str] = Field(default=None, alias='districtCnLevel')
        kano_question: Optional[KanoQuestion] = Field(default=None, alias='kanoQuestion')
        max_diff_question: Optional[MaxDiffQuestion] = Field(default=None, alias='maxDiffQuestion')
        joint_analysis_question: Optional[JointAnalysisQuestion] = Field(default=None, alias='jointAnalysisQuestion')

    class Option(BaseModel):
        id: str
        title: Optional[str] = None
        base_score: Optional[int] = Field(default=None, alias='baseScore')
        left_word: Optional[str] = Field(default=None, alias='leftWord')
        right_word: Optional[str] = Field(default=None, alias='rightWord')

    id: str
    subject: Optional[str] = None
    type: Type
    config: Optional[Configuration] = None
    options: Optional[List[Option]] = None


class Answer(BaseModel):
    class Answer(BaseModel):
        option_id: str = Field(..., alias='optionId')
        score: int

    class AnswerKano(BaseModel):
        positive_score: int = Field(..., alias='positiveScore')
        negative_score: int = Field(..., alias='negativeScore')

    class AnswerMaxDiff(BaseModel):
        task: int
        attribute: str
        positive: Optional[bool] = None
        negative: Optional[bool] = None

    class AnswerJointAnalysis(BaseModel):
        class Attribute(BaseModel):
            option_id: str = Field(..., alias='optionId')
            level: str

            def __eq__(self, other):
                if isinstance(other, Answer.AnswerJointAnalysis.Attribute):
                    return self.option_id == other.option_id and self.level == other.level
                return False

            def __hash__(self):
                return hash(self.option_id + self.level)

        task: int
        attributes: List[Attribute]
        select: Optional[bool] = None

    question_id: str = Field(..., alias='questionId')
    answer_options: List[str] = Field(default=None, alias='answerOptions')
    answers: List[Answer] = None
    answer_auto_fill: Optional[str] = Field(default=None, alias='answerAutoFill')
    answer_score: Optional[int] = Field(default=None, alias='answerScore')
    answer_date: Optional[str] = Field(default=None, alias='answerDate')
    answer_kano: Optional[AnswerKano] = Field(default=None, alias='answerKano')
    answer_max_diff: Optional[List[AnswerMaxDiff]] = Field(default=None, alias='answerMaxDiff')
    answer_joint_analysis: Optional[List[AnswerJointAnalysis]] = Field(default=None, alias='answerJointAnalysis')


class SurveyResult(BaseModel):
    agent_id: str
    results: List[Answer] = []


class QuestionIdx:
    def __init__(self, agent_id: str, question_id: str, answer: Answer):
        self.agent_id = agent_id
        self.question_id = question_id
        self.answer = answer


if __name__ == '__main__':
    import json

    with open('../data/question.json', 'r') as file:
        # 读取文件内容并解析JSON数据
        data_test = json.load(file)
    items: List[Question] = [Question(**item) for item in data_test]
    for data_test in items:
        print(data_test.json(exclude_none=True, by_alias=True))
