from pydantic import BaseModel
from typing import List
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


class Question(BaseModel):
    class Config:
        json_encoders = {
            Type: lambda t: t.value,
        }

    class Configuration(BaseModel):
        class KanoQuestion(BaseModel):
            class Title(BaseModel):
                id: str = None
                description: str

            class Option(BaseModel):
                description: str = None
                baseScore: int

            positive: Title
            negative: Title
            options: List[Option]

        class MaxDiffQuestion(BaseModel):
            class Title(BaseModel):
                id: str = None
                description: str

            class Option(BaseModel):
                id: str = None
                description: str

            taskNumber: int
            attributeNumber: int
            positive: Title
            negative: Title
            options: List[Option]

        class JointAnalysisQuestion(BaseModel):
            class Option(BaseModel):
                id: str
                title: str = None

                class LevelOption(BaseModel):
                    id: str = None
                    title: str

                levelOptions: List[LevelOption]

            chooseNothingLabel: str = None
            allowChooseNothing: bool
            conceptualNumber: int
            taskNumber: int
            options: List[Option]

        required: bool = None
        minMark: int = None
        maxMark: int = None
        minMarkLabel: str = None
        maxMarkLabel: str = None
        presentAnswers: str = None
        allowOtherAnswers: bool = None
        districtCnLevel: str = None
        kanoQuestion: KanoQuestion = None
        maxDiffQuestion: MaxDiffQuestion = None
        jointAnalysisQuestion: JointAnalysisQuestion = None

    class Option(BaseModel):
        id: str
        title: str = None
        baseScore: int = None
        leftWord: str = None
        rightWord: str = None

    id: str
    subject: str = None
    type: Type
    config: Configuration = None
    options: List[Option] = None


class Answer(BaseModel):
    class Answer(BaseModel):
        optionId: str
        score: int

    class AnswerKano(BaseModel):
        positiveScore: int
        negativeScore: int

    class AnswerMaxDiff(BaseModel):
        task: int
        attribute: str
        positive: bool = None
        negative: bool = None

    class AnswerJointAnalysis(BaseModel):
        class Attribute(BaseModel):
            optionId: str
            level: str
        task: int
        attributes: List[Attribute]
        select: bool = None

    questionId: str
    answerOptions: List[str] = None
    answers: List[Answer] = None
    answerScore: int = None
    answerDate: str = None
    answerKano: AnswerKano = None
    answerMaxDiff: List[AnswerMaxDiff] = None
    answerJointAnalysis: List[AnswerJointAnalysis] = None


class SurveyResult(BaseModel):
    agentId: str = None
    results: List[Answer] = None


if __name__ == '__main__':
    import json

    with open('../data/answer.json', 'r') as file:
        # 读取文件内容并解析JSON数据
        data = json.load(file)
    answers: List[Answer] = [Answer(**item) for item in data]
    for data in answers:
        print(data.json(exclude_none=True))
