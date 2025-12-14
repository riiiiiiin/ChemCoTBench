from .preprocessor import Preprocessor
import regex as re
import json

class RXNPreprocessor(Preprocessor):
    def __init__(self, data_path, task):
        super().__init__(data_path, task)
    def _extract(self, data):
        request_dict = super()._extract(data)
        request_dict['gt'] = data['gt']
        
        return request_dict
    
def get_preprocessors(path):
    def get_preprocessor(task):
        return RXNPreprocessor(f'{path}/rxn/{task}.json', task)
    return [
        get_preprocessor(task) for task in ['fs', 'mechsel', 'nepp', 'rcr', 'retro']
    ]