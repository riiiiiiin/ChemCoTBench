# %%
from preprocess.preprocess import get_preprocessors
from inference.remote_llm import RemoteLLM
import json
from postprocess_eval.moledit_eval import evaluate_moledit_score
from postprocess_eval.molopt_eval import evaluate_molopt_score
from postprocess_eval.molund_eval import evaluate_molund_score
from postprocess_eval.rxn_eval import evaluate_rxn_score
import logging
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--model_name', type=str, default='qwen3-8b')
parser.add_argument('--api_key', type=str, default='')
parser.add_argument('--base_url', type=str, default='')
args = parser.parse_args()

# %%
logger = logging.getLogger()
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
# %%
preprocessors = get_preprocessors('/home/myc/ChemCoTTest/bench')
api_key = args.api_key
base_url = args.base_url
model_name = args.model_name
llm = RemoteLLM(api_key, base_url, model_name)
log_name = model_name.split('/')[-1]

# %%
for preprocessor in preprocessors:
    preprocessor.preprocess()
    requests = preprocessor.get_all_requests()
    responses = llm.predict([request for request in requests])
    responses = [response['choices'][0]['message']['content'] for response in responses]
    for i, request in enumerate(preprocessor.get_all_data()):
        request['json_response' if preprocessor.task in ['fs', 'mechsel', 'nepp', 'RCR', 'retro'] else 'json_results'] = responses[i]
        
    json.dump(preprocessor.get_all_data(), open(f'logs/{preprocessor.task}/{log_name}.json', 'w'), indent=4)

# %%

moledit_results = evaluate_moledit_score(log_name)
molopt_results = evaluate_molopt_score(log_name)
molund_results = evaluate_molund_score(log_name)
rxn_results = evaluate_rxn_score(log_name)

all_results = {
    'moledit': moledit_results,
    'molopt': molopt_results,
    'molund': molund_results,
    'rxn': rxn_results
}

os.makedirs('results/all_results')
json.dump(all_results, open(f'results/all_results/{log_name}.json', 'w'), indent=4)