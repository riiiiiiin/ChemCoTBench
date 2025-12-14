from .preprocessor import Preprocessor
import regex as re
import json

mol_pattern = re.compile(r'Input Molecule:\s*(?P<smiles>.+?)\s*,\s*Functional Group', re.S)

def extract_mol(query_str):
    # src mol lies 
    m = mol_pattern.search(query_str)
    if m:
        smiles = m.group('smiles').strip()
        return smiles
    else:
        raise Exception('No molecule found in the query')

class MolEditPreprocessor(Preprocessor):
    def __init__(self, raw_data_path, task):
        super().__init__(raw_data_path, task)
    def _extract(self, data):
        request_dict = super()._extract(data)
        request_dict['task'] = data['subtask']
        
        try:
            mol = extract_mol(request_dict['query'])
        except:
            print(f"Failed to extract molecule from {data['query']}")
            return None
        
        request_dict['molecule'] = mol
        meta_dict = json.loads(data['meta'])
        request_dict['reference'] = meta_dict['reference']
        if 'added_group' in meta_dict:
            request_dict['added_group'] = meta_dict['added_group']
        if 'removed_group' in meta_dict:
            request_dict['removed_group'] = meta_dict['removed_group']
            
        return request_dict

def get_preprocessors(base_path):
    def get_preprocessor(task):
        return MolEditPreprocessor(f'{base_path}/mol_edit/{task}.json', task)
    return [
        get_preprocessor(task) for task in ['add', 'delete', 'sub']
    ]
 
if __name__ == '__main__':
    mol_edit = MolEditPreprocessor('/home/myc/ChemCoTTest/bench/mol_edit/sub.json', 'sub')
    mol_edit.preprocess()
    print(mol_edit.data[0])