import threading


class ThreadLocalDataStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadLocalDataStore, cls).__new__(cls)
            cls._instance.dataStore = threading.local()
        return cls._instance.dataStore
