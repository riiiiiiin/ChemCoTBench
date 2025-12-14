from abc import ABC, abstractmethod

class InferenceInterface(ABC):
    @abstractmethod
    def predict(self, input:list[dict]) -> list[dict]:
        '''
        abstract method for inference
        
        input[i]: {'messages': [{'role': str,'content': str},], 'meta': {'tempeture': int,'enable_thinking': boolean}}
        
        output[i]: {'choices': [{'message': {'content': str}},]}
        '''
        pass
    