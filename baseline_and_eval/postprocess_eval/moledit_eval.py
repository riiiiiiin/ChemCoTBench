import json
from eval.eval_moledit import eval_moledit_from_list
from eval.utils import tranform_str_to_json

def evaluate_moledit_score(model_name): 
    result_dict = dict()
    
    for task in ['add', 'delete', 'sub']:
        print(model_name, task)
        file_name = f"logs/{task}/{model_name}.json" 
        pred_results = json.load(open(file_name, "r"))
        
        invalid_number = 0
        pred_list, src_list = list(), list()
        group_a, group_b = list(), list()
        
        for pred in pred_results:
            ## extract predicted-smiles, if prediction is not json format, need to change 
            if type(pred['json_results']) is str:
                pred_json = tranform_str_to_json(str_input=pred['json_results'])
                # if model_name == 'gemini': pred_json = pred_json[0]
                if pred_json == None:
                    invalid_number += 1
                    continue
                else:
                    if 'output' not in pred_json.keys():
                        invalid_number += 1; continue
                    pred_list.append(pred_json['output'])
                    src_list.append(pred['molecule'])
                    if task == 'add': group_a.append(pred['added_group'])
                    elif task == 'delete': group_a.append(pred['removed_group'])
                    elif task == 'sub':
                        group_a.append(pred['added_group']); group_b.append(pred['removed_group'])
            else:
                pred_list.append(pred['json_results']['output'])
                src_list.append(pred['molecule'])
                if task == 'add': group_a.append(pred['added_group'])
                elif task == 'delete': group_a.append(pred['removed_group'])
                elif task == 'sub':
                    group_a.append(pred['added_group']); group_b.append(pred['removed_group'])
        
        assert len(src_list) == len(pred_list)
        assert len(src_list) == len(group_a)
        
        result_dict[task] = eval_moledit_from_list(src_list=src_list, pred_list=pred_list, group_a=group_a, group_b=group_b, task=task, total_number=len(pred_list)) 
    
    print(f"eval_score_{model_name}", result_dict)
    # json.dump(result_dict, open(f"logs/eval_score_{model_name}.json", "w"), indent=4)
