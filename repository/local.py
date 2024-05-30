import threading
from typing import Dict, List

from networkx import DiGraph


class ThreadLocalDataStore:
    _instance = None
    _lock = threading.Lock()
    _collection_social_network = "__socialNetwork"
    _collection_survey_results = "__surveyResults"
    _collection_joint_options = "__jointOptions"

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ThreadLocalDataStore, cls).__new__(cls)
                cls._instance.dataStore = threading.local()
        return cls._instance

    def get_social_network(self) -> DiGraph:
        if not hasattr(self.dataStore, ThreadLocalDataStore._collection_social_network):
            setattr(self.dataStore, ThreadLocalDataStore._collection_social_network, DiGraph())
        return getattr(self.dataStore, ThreadLocalDataStore._collection_social_network)

    def get_survey_results(self) -> Dict:
        if not hasattr(self.dataStore, ThreadLocalDataStore._collection_survey_results):
            setattr(self.dataStore, ThreadLocalDataStore._collection_survey_results, {})
        return getattr(self.dataStore, ThreadLocalDataStore._collection_survey_results)

    def get_joint_options(self) -> Dict:
        if not hasattr(self.dataStore, ThreadLocalDataStore._collection_joint_options):
            setattr(self.dataStore, ThreadLocalDataStore._collection_joint_options, {})
        return getattr(self.dataStore, ThreadLocalDataStore._collection_joint_options)
