from abc import ABC, abstractmethod
import json
import os

class Preprocessor(ABC):
    """
    Abstract class for preprocessor
    """
    def __init__(self, raw_data_path, task, task_key = 'task'):
        self.path = raw_data_path
        self.task = task
        self.task_key = task_key
        
    def preprocess(self):
        self.data = []
        with open(self.path, 'r') as f:
            data = json.load(f)
            self.data = [self._extract(d) for d in data]
            
    @abstractmethod
    def _extract(self, data: dict) -> dict:
        result = {}
        result['id'] = data['id']
        result[self.task_key] = self.task
        result['query'] = data['query']
        return result
    
    def get_all_requests(self):
        return [{"messages": [{"role": "user", "content": d['query']}]} for d in self.data]
    
    def get_all_data(self):
        return self.data
    
    def save(self, base_path):
        def last_two_parts(path: str) -> str:
            parent, last = os.path.split(path)
            _, second_last = os.path.split(parent)
            return second_last, os.path.join(second_last, last)
        second_last, last_two = last_two_parts(self.path)
        os.makedirs(os.path.join(base_path, second_last), exist_ok=True)
        with open(os.path.join(base_path, last_two), 'w') as f:
            json.dump(self.data, f, indent=4)