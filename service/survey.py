import itertools
import math
from typing import List, Dict, Any

from sklearn.tree import DecisionTreeClassifier

from model.survey import Question, Answer, SurveyResult, QuestionIdx, Type
from model.agent import Agent
import repository.survey_repository as sv_repo
import repository.agent_repository as ag_repo
import random
import numpy as np
import pandas as pd


def survey_simulate(questions: List[Question]) -> List[SurveyResult]:
    for respondent in ag_repo.all_agents_list():
        survey_from_agent(questions, respondent)
    return sv_repo.all_survey_results()


def survey_from_agent(questions: List[Question], respondent: Agent):
    # 获取respondent关注的所有agent，并计算agent的in_degree, 和关注权重。
    # 查询关注的这些agents的答卷，筛选出有答卷的agents，并计算其权重。
    # 根据权重计算出标准正态分布的sigma。
    # 迭代每一个问题，加权计算关注的agents的答题的μ，并根据μ和σ，生成respondent的结果。

    # 从所关注的人中，再筛选出答题的人。
    influencers = list(ag_repo.get_social_network().successors(respondent.id))
    references = sv_repo.survey_results_from_agents(influencers)
    agent_ids = {i.agent_id for i in references}
    ref_weights = {
        inf: ag_repo.relation_weight_by_agent_ids(respondent.id, inf)
        for inf in influencers
        if inf in agent_ids
    }
    for q in questions:
        # 如果问题问的是性别、年龄、所在城市，则利用语言模型来回答标准答案
        res_ans = ask_lang_model(q, respondent)
        if res_ans:
            sv_repo.save_survey_answer(respondent.id, res_ans)
            continue
        res_ans = Answer(questionId=q.id)
        if respondent.random_preference > np.random.rand():
            answer_question(q, res_ans)
        else:
            # 受到好友影响来回答该问题
            q_refs: List[QuestionIdx] = []
            for r in references:
                ans = sv_repo.answer_by_agent_id_question_id(r.agent_id, q.id)
                if ans:
                    q_refs.append(QuestionIdx(r.agent_id, q.id, ans))
            # 利用q_refs计算该问题的新的result
            if q_refs:
                answer_question_by_weighted_refs(q, res_ans, q_refs, ref_weights)
            else:
                answer_question(q, res_ans)
        sv_repo.save_survey_answer(respondent.id, res_ans)


# todo 利用语言模型来回答性别、年龄、所在城市
def ask_lang_model(question: Question, respondent: Agent) -> Answer | None:
    if question.type in [Type.DISTRICT_CN, Type.TEXT, Type.SINGLE_SELECT,
                         Type.DATE, Type.LOCATION, Type.ADDRESS]:
        return None
    return None


def answer_question(question: Question, answer: Answer):
    if question.type in [Type.SINGLE_SELECT, Type.SCORE_SINGLE_SELECT]:
        opt: Question.Option = random.choice(question.options)
        answer.answer_options = [opt.id]
    elif question.type in [Type.MULTI_SELECT, Type.SCORE_MULTI_SELECT]:
        choices = random.randint(1, len(question.options))
        answer.answer_options = [item.id for item in random.sample(question.options, choices)]
    elif question.type in [Type.SINGLE_EVALUATION, Type.MULTI_EVALUATION]:
        if not answer.answers:
            answer.answers = []
        for opt in question.options:
            answer.answers.append(Answer.Answer(optionId=opt.id, score=random.randint(1, opt.base_score)))
    elif question.type == Type.SCORE_SLIDE:
        score = random.randint(question.config.min_mark, question.config.max_mark)
        answer.answer_score = score
    elif question.type == Type.AUTO_FILL:
        if question.config.preset_answers:
            answer.answer_auto_fill = random.choice(question.config.preset_answers.split("\n"))
    elif question.type == Type.KANO:
        answer.answer_kano = Answer.AnswerKano(
            positiveScore=random.choice(question.config.kano_question.options).baseScore,
            negativeScore=random.choice(question.config.kano_question.options).baseScore
        )
    elif question.type == Type.MAX_DIFF:
        task_number = question.config.max_diff_question.task_number
        attr_number = question.config.max_diff_question.attribute_number
        if not answer.answer_max_diff:
            answer.answer_max_diff = []
        for t in range(task_number):
            maxdiff_options: List[Question.Configuration.MaxDiffQuestion.Option] = random.sample(
                question.config.max_diff_question.options, attr_number)
            [pos_option, neg_option] = random.sample(maxdiff_options, 2)
            for maxdiff_opt in maxdiff_options:
                answer.answer_max_diff.append(Answer.AnswerMaxDiff(task=t + 1, attribute=maxdiff_opt.description,
                                                                   positive=pos_option.id == maxdiff_opt.id,
                                                                   negative=neg_option.id == maxdiff_opt.id))
    elif question.type == Type.JOINT_ANALYSIS:
        # print(f"随机回答{question.type}")
        answer.answer_joint_analysis = []
        task_number = question.config.joint_analysis_question.task_number
        concept_number = question.config.joint_analysis_question.conceptual_number
        joint_options = build_joint_options(question)
        for t in range(task_number):
            candidates = random.sample(joint_options, concept_number)
            # print(candidates)
            # print("*"*100)
            result = random.choice(candidates)
            result_opts = [] if not result else [(r["option_id"], r["level_id"]) for r in result]
            # print(result_opts)
            for c in candidates:
                attrs: List[Answer.AnswerJointAnalysis.Attribute] = []
                select = True
                for a in c:
                    attrs.append(Answer.AnswerJointAnalysis.Attribute(optionId=a["option_id"], level=a["level"]))
                    if not result_opts or (a["option_id"], a["level_id"]) not in result_opts:
                        select = False
                # print(select)
                answer.answer_joint_analysis.append(
                    Answer.AnswerJointAnalysis(task=t + 1, attributes=attrs, select=select))

    return answer


def build_joint_options(question: Question) -> List | None:
    if question.type != Type.JOINT_ANALYSIS:
        return None
    if not sv_repo.get_joint_options_by_question(question.id):
        opt_lists = []
        for ja_opt in question.config.joint_analysis_question.options:
            opt_items = []
            for ja_lvl in ja_opt.level_options:
                opt_items.append({"option_id": ja_opt.id, "level_id": ja_lvl.id, "level": ja_lvl.title, })
            opt_lists.append(opt_items)
        cartesian_product = list(itertools.product(*opt_lists))
        sv_repo.flush_joint_options(question.id, cartesian_product)
        return cartesian_product


def __choice_options_by_weight_dict(weights: Dict[Any, float], choices: int = 1) -> List:
    values = np.array(list(weights.values()))
    if values.sum() == 0:
        return [None]
    keys = np.array(list(weights.keys()))
    arr_length = len(keys)
    if choices > arr_length:
        choices = arr_length
    return np.random.choice(keys, size=choices, replace=False, p=values / values.sum()).tolist()


def __choice_options_by_refs(q_refs: List[QuestionIdx], relation_weights: Dict[str, float], choices=1) -> List[str]:
    opt_weight = {}
    for q_idx in q_refs:
        for opt_id in q_idx.answer.answer_options:
            opt_weight[opt_id] = relation_weights[q_idx.agent_id] \
                if opt_id not in opt_weight else opt_weight[opt_id] + relation_weights[q_idx.agent_id]
    return __choice_options_by_weight_dict(weights=opt_weight, choices=choices)


def __score_by_norm_distribution(score_dict: Dict[str, int], weight_dict: Dict[str, float],
                                 agent_ids: List[str]) -> int:
    ans_count = sum(weight_dict[agt_id] for agt_id in agent_ids)
    ans_mean = sum(score_dict[agt_id] * weight_dict[agt_id] for agt_id in agent_ids) / ans_count
    ans_std = math.sqrt(
        sum(weight_dict[agt_id] * ((score_dict[agt_id] - ans_mean) ** 2) for agt_id in agent_ids) / ans_count
    )
    return round(np.random.normal(ans_mean, ans_std))


def answer_question_by_weighted_refs(question: Question, answer: Answer,
                                     q_refs: List[QuestionIdx], weights: Dict[str, float]):
    if question.type in [Type.SINGLE_SELECT, Type.SCORE_SINGLE_SELECT]:
        answer.answer_options = __choice_options_by_refs(q_refs, weights)
    elif question.type in [Type.MULTI_SELECT, Type.SCORE_MULTI_SELECT]:
        choices = random.randint(1, len(question.options))
        answer.answer_options = __choice_options_by_refs(q_refs=q_refs, relation_weights=weights, choices=choices)
    elif question.type in [Type.SINGLE_EVALUATION, Type.MULTI_EVALUATION]:
        opt_weight = {}
        for opt in question.options:
            opt_weight[opt.id] = {}
        for q_idx in q_refs:
            for ans in q_idx.answer.answers:
                if int(ans.score) not in opt_weight[ans.option_id]:
                    opt_weight[ans.option_id][int(ans.score)] = 0
                opt_weight[ans.option_id][int(ans.score)] += weights[q_idx.agent_id]
        if not answer.answers:
            answer.answers = []
        for opt in question.options:
            choose_keys = list(opt_weight[opt.id].keys())
            choose_values = list(opt_weight[opt.id].values())
            score = random.choices(choose_keys, weights=choose_values, k=1)[0]
            answer.answers.append(Answer.Answer(optionId=opt.id, score=score))
    elif question.type == Type.SCORE_SLIDE:
        score_dict = {}
        weight_dict = {}
        agent_ids = []
        for q_idx in q_refs:
            score_dict[q_idx.agent_id] = q_idx.answer.answer_score
            weight_dict[q_idx.agent_id] = weights[q_idx.agent_id]
            agent_ids.append(q_idx.agent_id)
        score = max(
            question.config.min_mark, min(
                question.config.max_mark, __score_by_norm_distribution(
                    score_dict=score_dict,
                    weight_dict=weight_dict,
                    agent_ids=agent_ids
                )
            )
        )
        answer.answer_score = score
    elif question.type == Type.AUTO_FILL:
        ans_weights = {}
        for q_idx in q_refs:
            if q_idx.answer.answer_auto_fill not in ans_weights:
                ans_weights[q_idx.answer.answer_auto_fill] = 0
            ans_weights[q_idx.answer.answer_auto_fill] += weights[q_idx.agent_id]
        answer.answer_auto_fill = __choice_options_by_weight_dict(weights=ans_weights)[0]
    elif question.type == Type.KANO:
        pos_weight = {}
        neg_weight = {}
        for q_idx in q_refs:
            if q_idx.answer.answer_kano.positive_score not in pos_weight:
                pos_weight[q_idx.answer.answer_kano.positive_score] = 0
            if q_idx.answer.answer_kano.negative_score not in neg_weight:
                neg_weight[q_idx.answer.answer_kano.negative_score] = 0
            pos_weight[q_idx.answer.answer_kano.positive_score] += weights[q_idx.agent_id]
            neg_weight[q_idx.answer.answer_kano.negative_score] += weights[q_idx.agent_id]
        answer.answer_kano = Answer.AnswerKano(
            positiveScore=__choice_options_by_weight_dict(weights=pos_weight)[0],
            negativeScore=__choice_options_by_weight_dict(weights=neg_weight)[0]
        )
    elif question.type == Type.MAX_DIFF:
        if not answer.answer_max_diff:
            answer.answer_max_diff = []
        task_number = question.config.max_diff_question.task_number
        attr_number = question.config.max_diff_question.attribute_number
        pos_weights = {}
        neg_weights = {}
        for q_idx in q_refs:
            for ans in q_idx.answer.answer_max_diff:
                if ans.attribute not in pos_weights:
                    pos_weights[ans.attribute] = 0
                if ans.attribute not in neg_weights:
                    neg_weights[ans.attribute] = 0
                if ans.positive:
                    pos_weights[ans.attribute] += weights[q_idx.agent_id]
                if ans.negative:
                    neg_weights[ans.attribute] += weights[q_idx.agent_id]
        for t in range(task_number):
            maxdiff_options: List[Question.Configuration.MaxDiffQuestion.Option] = random.sample(
                question.config.max_diff_question.options, attr_number)
            task_pos = {mo.description: pos_weights[mo.description]
                        for mo in maxdiff_options if mo.description in pos_weights}
            task_neg = {mo.description: neg_weights[mo.description]
                        for mo in maxdiff_options if mo.description in neg_weights}
            pos_option: Question.Configuration.MaxDiffQuestion.Option = \
                __choice_options_by_weight_dict(weights=task_pos)[0]
            neg_option: Question.Configuration.MaxDiffQuestion.Option = \
                __choice_options_by_weight_dict(weights=task_neg)[0]
            for maxdiff_opt in maxdiff_options:
                answer.answer_max_diff.append(Answer.AnswerMaxDiff(task=t + 1, attribute=maxdiff_opt.description,
                                                                   positive=pos_option == maxdiff_opt.description,
                                                                   negative=neg_option == maxdiff_opt.description))
    elif question.type == Type.JOINT_ANALYSIS:
        model = __train_joint_analysis_decision_tree(question, q_refs, weights)
        answer.answer_joint_analysis = []
        task_number = question.config.joint_analysis_question.task_number
        concept_number = question.config.joint_analysis_question.conceptual_number
        cartesian_product = build_joint_options(question)
        for t in range(task_number):
            candidates = random.sample(cartesian_product, concept_number)
            for c in candidates:
                cols = pd.DataFrame(columns=__build_joint_analysis_onehot_columns(question))
                row = {}
                attrs: List[Answer.AnswerJointAnalysis.Attribute] = []
                for a in c:
                    row[a["option_id"]+"_"+a["level"]] = 1
                    attrs.append(Answer.AnswerJointAnalysis.Attribute(optionId=a["option_id"], level=a["level"]))
                df = pd.concat([cols, pd.DataFrame([row])], ignore_index=True)
                df = df.infer_objects(copy=False)
                df.fillna(0, inplace=True)
                y_predict = model.predict(df)
                answer.answer_joint_analysis.append(
                    Answer.AnswerJointAnalysis(task=t + 1, attributes=attrs, select=(y_predict[0] == "1")))

    return answer


def __build_joint_analysis_onehot_columns(question) -> List[str]:
    columns = []
    for o in question.config.joint_analysis_question.options:
        for lvl in o.level_options:
            columns.append(o.id + "_" + lvl.title)
    return columns


def __train_joint_analysis_decision_tree(question: Question, q_refs: List[QuestionIdx],
                                         relation_weights: Dict[str, float]):
    # 构建训练数据
    columns = __build_joint_analysis_onehot_columns(question)
    columns.append("_target")
    data = []
    # joint_options = build_joint_options(question)
    # for jo in joint_options:
    #     new_row = {}
    #     for col in jo:
    #         new_row[col["option_id"]] = col["level"]
    #     new_row["_target"] = 0.5
    #     df = df.append(new_row, ignore_index=True)

    # 构造数据集
    for q_idx in q_refs:
        for ans in q_idx.answer.answer_joint_analysis:
            new_row = {}
            for col in ans.attributes:
                new_row[col.option_id + "_" + col.level] = 1
            new_row["_target"] = "1" if ans.select else "0"
            for _ in range(int(relation_weights[q_idx.agent_id])):
                data.append(new_row)
    df = pd.DataFrame(data, columns=columns)
    df.fillna(0, inplace=True)

    x = df.iloc[:, 0:-1]
    y = df.iloc[:, -1]
    clf = DecisionTreeClassifier()
    clf.fit(x, y)
    return clf
