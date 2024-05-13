from typing import List

from networkx import DiGraph

from model.agent import SocialNetwork, Agent
from repository.local import ThreadLocalDataStore

dataStore = ThreadLocalDataStore()

if not hasattr(dataStore, '__socialNetwork'):
    dataStore.__socialNetwork = SocialNetwork()


def get_social_network() -> SocialNetwork:
    return dataStore.__socialNetwork


def update_survey_result(sn: SocialNetwork):
    dataStore.__socialNetwork = sn


def get_agents() -> List[Agent]:
    return dataStore.__socialNetwork.get_agents()


def get_relations() -> DiGraph:
    return dataStore.__socialNetwork.get_relations()
