import json
from eval.utils import tranform_str_to_json
from eval.eval_molund import check_string_type
from eval.eval_molund import eval_molund_from_list
import logging
import os

logger = logging.getLogger(__name__)

def evaluate_molund_score(model_name):
    task_dict = dict(
        fg_samples="fg_samples", murcko='murcko_scaffold', ring_count='ring_count',
        ring_system='ring_system_scaffold', equivalence = 'equivalence'
    )
    pred_key_dict = dict(
        fg_samples="count", murcko='Output Scaffold', ring_count='count',
        ring_system='output', equivalence = 'output'
    )
    gt_key_dict = dict(
        fg_samples="fg_num", murcko='largest_scaffold', ring_count='count',
        ring_system='', equivalence = 'gt'
    )
    result_dict = dict()
    
    for task in task_dict.keys():
        logger.info(f'evaluating {task} for model {model_name}')
        if 'llama' not in model_name:
            file_name = f"logs/{task_dict[task]}/{model_name}.json"
            
        pred_results = json.load(open(file_name, "r"))
        invalid_number = 0
        
        pred_list, gt_list = list(), list()
        for pred in pred_results:  
            if type(pred['json_results']) is str:
                pred_json = tranform_str_to_json(str_input=pred['json_results'])
                # if model_name == 'gemini': pred_json = pred_json[0]
                if pred_json == None:
                    invalid_number += 1
                    continue
                else:
                    if pred_key_dict[task] not in pred_json.keys():
                        invalid_number += 1; continue
                    if pred_json[pred_key_dict[task]] == "": 
                        invalid_number += 1; continue
                    if task in ["ring_count", "fg_samples"]:
                        if check_string_type(pred_json[pred_key_dict[task]]) == "string":
                            invalid_number += 1; continue
                    pred_list.append(pred_json[pred_key_dict[task]])
                    if gt_key_dict[task] != "":
                        gt_list.append(pred[gt_key_dict[task]])
            else:
                if pred_key_dict[task] not in pred['json_results'].keys():
                    invalid_number += 1; continue
                if pred['json_results'][pred_key_dict[task]] == "": 
                    invalid_number += 1; continue
                if task in ["ring_count", "fg_samples"]:
                    if check_string_type(pred['json_results'][pred_key_dict[task]]) == "string":
                            invalid_number += 1; continue
                pred_list.append(pred['json_results'][pred_key_dict[task]])
                if gt_key_dict[task] != "":
                    gt_list.append(pred[gt_key_dict[task]])
        
        assert len(pred_results) == invalid_number+len(pred_list)
        result_dict[task] = eval_molund_from_list(gt_list=gt_list, pred_list=pred_list, total_number=len(pred_results), task=task)
        logger.debug(model_name, task, result_dict[task])
    
    logger.info(f"eval_score_{model_name}_molund:\n\r{result_dict}")
    os.makedirs("results/molund", exist_ok=True)
    json.dump(result_dict, open(f"results/molund/eval_score_{model_name}.json", "w"), indent=4)
    
    return result_dict