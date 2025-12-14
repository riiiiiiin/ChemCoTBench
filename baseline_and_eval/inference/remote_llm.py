import requests
from .inference_interface import InferenceInterface
from tqdm import tqdm

class RemoteLLM(InferenceInterface):
    def __init__(self, api_key, base_url, model_name):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
    
    def predict(self, input):
        # not batched for remote api
        response = []
        for request in tqdm(input):
            temperature = request.get("temperature", 0)
            enable_thinking = request.get("enable_thinking", False)
            messages = request.get("messages", [])
            response.append(call_direct(self.api_key, self.base_url, self.model_name,
                            messages,
                            temperature,
                            enable_thinking))
        return response
    
def call_direct(api_key, base_url, model_name, messages, temperature=0, enable_thinking=False):
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "enable_thinking": enable_thinking
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    api_key = "sk-DpoawLJHcGdppEEfbfe7cBB0JUkEK8MTcuDXbhXwbLTEyTkj"
    base_url = "http://35.220.164.252:3888/v1/"
    model_name = "qwen3-8b"
    llm = RemoteLLM(api_key, base_url, model_name)
    llm.predict([{"messages": [{"role": "user", "content": "你好"}]},
                 {"messages": [{"role": "user", "content": "hello"}]}])