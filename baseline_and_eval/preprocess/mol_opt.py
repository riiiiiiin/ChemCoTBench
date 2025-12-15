from .preprocessor import Preprocessor
import regex as re
import json
import logging

logger = logging.getLogger(__name__)

mol_pattern = re.compile(r'Source Molecule:\s*(?P<smiles>.+?)\.$', re.S)

def extract_mol(query_str):
    # src mol lies 
    m = mol_pattern.search(query_str)
    if m:
        smiles = m.group('smiles').strip()
        # print(smiles)
        return smiles
    else:
        raise Exception('No molecule found in the query')
    
class MolOptPreprocessor(Preprocessor):
    def __init__(self, raw_data_path, task):
        super().__init__(raw_data_path, task, 'prop')
        
    def _extract(self, data):
        request_dict = super()._extract(data)
        
        try:
            mol = extract_mol(data['query'])
        except:
            logger.debug(f"Failed to extract molecule from {data['query']}")
            return None
        
        request_dict['src_smiles'] = mol
        
        return request_dict

def get_preprocessors(base_path):
    def get_preprocessor(task):
        return MolOptPreprocessor(f'{base_path}/mol_opt/{task}.json', task)
    return [
        get_preprocessor(task) for task in ['drd', 'gsk', 'jnk', 'logp', 'qed', 'solubility']
    ]