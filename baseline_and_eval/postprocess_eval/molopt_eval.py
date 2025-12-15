import json
from eval.eval_molopt import eval_molopt_from_list
from eval.utils import tranform_str_to_json
import logging
import os

logger = logging.getLogger(__name__)

def evaluate_molopt_score(model_name=None):
    ## 在get_molopt_cot中得到test结果, 我们评测这些test结果
    prop_dict = dict(logp='logp', solubility='solubility', qed="qed",  drd='drd2', jnk='jnk3', gsk='gsk3b')
    # prop_dict = dict(logp='logp', solubility='solubility', qed="qed",  drd='drd2', gsk='gsk3b')
    
    result_final = dict()
    
    for prop in prop_dict.keys():
        logger.info(f'evaluating {prop} for model {model_name}')
        file_name = f"logs/{prop}/{model_name}.json"
        pred_results = json.load(open(file_name, "r"))
        
        tgt_smiles_list, src_smiles_list = list(), list()
        
        invalid_number = 0
        final_target_key = 'Final Target Molecule'
        
        if model_name not in ['biomedgpt', 'biomistral']:
            src_smiles_key =  'src_smiles'
        else: src_smiles_key = "src"
        
        for pred in pred_results:
            ## 提取 predicted-smiles, 如果生成的是json格式那不需要额外操作, 如果不是, 需要转换成json形式
            if type(pred['json_results']) is str:
                pred_json = tranform_str_to_json(str_input=pred['json_results'])
                # if model_name == 'gemini': pred_json = pred_json[0]
                if pred_json == None or type(pred_json) is str:
                    logger.debug(pred['json_results'])
                    invalid_number += 1
                    continue
                else:
                    if final_target_key in pred_json.keys():
                        tgt_smiles_list.append(pred_json[final_target_key])
                        src_smiles_list.append(pred[src_smiles_key])
                    else: 
                        logger.debug(pred['json_results'])
                        invalid_number += 1
                        continue
            else:
                if final_target_key in pred['json_results'].keys():
                    tgt_smiles_list.append(pred['json_results'][final_target_key])
                    src_smiles_list.append(pred[src_smiles_key])
        
        logger.debug(len(pred_results), invalid_number, len(src_smiles_list))
        assert len(src_smiles_list) == len(tgt_smiles_list)
        assert len(pred_results) == invalid_number + len(src_smiles_list)
        
        result_dict = eval_molopt_from_list(optimized_prop=prop, gt_list=src_smiles_list, pred_list=tgt_smiles_list, total_number=len(pred_results))
        result_final[prop] = result_dict
    
    logger.info(f"eval_score_{model_name}_molopt:\n\r{result_final}")
    os.makedirs("results/molopt", exist_ok=True)
    json.dump(result_final, open(f"results/molopt/eval_score_{model_name}.json", "w"), indent=4)
    
    return result_final