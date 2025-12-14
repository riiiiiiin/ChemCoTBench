# %%
from preprocess.preprocess import get_preprocessors
from inference.remote_llm import RemoteLLM
import json
from postprocess_eval.moledit_eval import evaluate_moledit_score
from postprocess_eval.molopt_eval import evaluate_molopt_score
from postprocess_eval.molund_eval import evaluate_molund_score
from postprocess_eval.rxn_eval import evaluate_rxn_score

preprocessors = get_preprocessors('/home/myc/ChemCoTTest/bench')
api_key = "sk-DpoawLJHcGdppEEfbfe7cBB0JUkEK8MTcuDXbhXwbLTEyTkj"
base_url = "http://35.220.164.252:3888/v1/"
model_name = "qwen3-8b"
llm = RemoteLLM(api_key, base_url, model_name)

for preprocessor in preprocessors:
    continue
    preprocessor.preprocess()
    requests = preprocessor.get_all_requests()
    responses = llm.predict([request for request in requests])
# %%
    responses = [response['choices'][0]['message']['content'] for response in responses]
# %%
    for i, request in enumerate(preprocessor.get_all_data()):
        request['json_response' if preprocessor.task in ['fs', 'mechsel', 'nepp', 'RCR', 'retro'] else 'json_results'] = responses[i]
        
    json.dump(preprocessor.get_all_data(), open(f'{preprocessor.task}.json', 'w'), indent=4)

# %%

# evaluate_moledit_score(model_name)
# evaluate_molopt_score(model_name)
# evaluate_molund_score(model_name)
evaluate_rxn_score(model_name)