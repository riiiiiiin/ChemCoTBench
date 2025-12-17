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
parser.add_argument('--log_name', type=str, default=None)
parser.add_argument('--api_key', type=str, default='')
parser.add_argument('--base_url', type=str, default='')
parser.add_argument('--streaming', type=bool, default=False)
parser.add_argument('--enable_thinking', type=bool, default=False)
parser.add_argument('--skip_tasks', nargs='+', type=str, default=None)
args = parser.parse_args()

# %%
logger = logging.getLogger()
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
# %%
preprocessors = get_preprocessors('../bench')
api_key = args.api_key
base_url = args.base_url
model_name = args.model_name
streaming = args.streaming
enable_thinking = args.enable_thinking
llm = RemoteLLM(api_key, base_url, model_name, streaming, enable_thinking)
log_name = args.log_name if args.log_name else model_name.split('/')[-1]
skip_tasks = args.skip_tasks

# %%
for preprocessor in preprocessors:
    if skip_tasks and preprocessor.task in skip_tasks:
        continue
    preprocessor.preprocess()
    requests = preprocessor.get_all_requests()
    responses = llm.predict([request for request in requests])
    for i, request in enumerate(preprocessor.get_all_data()):
        request['json_response' if preprocessor.task in ['fs', 'mechsel', 'nepp', 'rcr', 'retro'] else 'json_results'] = responses[i]
        
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