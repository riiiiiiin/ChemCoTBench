import sys, re, os, json
from .rxnutils import read_json, is_valid_smiles
from eval.utils import tranform_str_to_json

from evaluator import MoleculeSMILESEvaluator
evaluator = MoleculeSMILESEvaluator()

subtask_to_result_key = {
    "RCR": "SMILES",
    "nepp": "pred_smi",
    "mechsel": "choice",
    "major_product": "Major Product",
    "byproduct": "Byproduct(s)",
    "retro": "Reactants"
}

def evaluate_mol(model_name: str, subtask: str, log_dir: str = None):
    print(f'{model_name} {subtask}')
    if log_dir is None:
        log_dir = f"logs/{subtask}"
    
    if not os.path.exists(log_dir):
        raise ValueError(f"logs_dir {log_dir} is not correct")
    samples = read_json(f"{log_dir}/{model_name}.json")
    preds = []
    gts = []
    for sample in samples:
        gt = sample['gt']
        if subtask in ['major_product', 'byproduct']:
            gt = json.loads(gt)
            gts.append(gt.get(subtask_to_result_key[subtask], ''))
        elif subtask == 'retro':
            if len(gt) == 0:
                continue
            gts.append('.'.join(gt))
        else:
            gts.append(gt)

        try:
            pred_smiles = tranform_str_to_json(sample['json_response'])
            pred = pred_smiles.get(subtask_to_result_key[subtask], '')
            if subtask == 'retro':
                pred = '.'.join(pred)
            preds.append(pred)
        except Exception as e:
            print(f'error parsing {sample['json_response']}: {e}')
            preds.append('')
        
    res = evaluator.evaluate(preds, gts)
    if subtask in ['RCR', 'major_product', 'byproduct', 'retro']:
        fts = (res['rdk_sims'] + res['maccs_sims'] + res['morgan_sims']) / 3
        res['fts'] = fts
        
    return res

def evaluate_MechSel(model_name: str, logs_dir: str = 'logs/mechsel'):
    """
    Evaluate the reaction mechanism selection prediction.

    Args:
        logs_dir (str): The directory where the logs are stored.
        model_name (str): The name of the model.

    Returns:
        None
    """
    if not os.path.exists(logs_dir):
        raise ValueError(f"logs_dir {logs_dir} is not correct")
    samples = read_json(f"{logs_dir}/{model_name}.json")

    preds = []
    gts = []
    for sample in samples:
        pred_smiles = tranform_str_to_json(sample['json_response'])
        pred_choice = pred_smiles[subtask_to_result_key['MechSel']]
        preds.append(pred_choice)
        if len(pred_choice) > 1:
            # if multiple chars, we take the first one
            pred_choice = pred_choice[0]
        # if pred_choice is not a valid choice, we treat it as empty
        if not pred_choice.lower().isalpha():
            pred_choice = ""

        pred_choice = pred_choice.lower()
        gt = sample['gt'].lower()
        preds.append(pred_choice)
        gts.append(gt)

    accuracy = sum(1 for pred, gt in zip(preds, gts) if pred == gt) / len(gts)
    return {"MCQ Accuracy (mean)": accuracy}

def evaluate_rxn_score(model_name: str, logs_dir: str = 'logs'):
    all_results = {}
    subtasks = subtask_to_result_key.keys()
    for subtask in subtasks:
        if subtask == 'MechSel':
            all_results[subtask] = evaluate_MechSel(model_name)
        elif subtask in ['major_product', 'byproduct']:
            all_results[subtask] = evaluate_mol(model_name, subtask, f"{logs_dir}/fs")
        else:
            all_results[subtask] = evaluate_mol(model_name, subtask)
    print(f"eval_score_{model_name}", all_results)


