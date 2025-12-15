from ..preprocessor import Preprocessor
import regex as re
import json
import logging

logger = logging.getLogger(__name__)

mol_pattern_mol = re.compile(r'Input Molecule:\s*(?P<smiles>.+?)\.$', re.S)

def extract_mol(query_str):
    match = mol_pattern_mol.search(query_str)
    if match:
        mol = match.group('smiles').strip()
        return mol
    else:
        raise Exception('Query not match pattern')
    
class MurckoScaffoldProcessor(Preprocessor):
    def __init__(self, base_path):
        super().__init__(f'{base_path}/mol_und/Murcko_scaffold.json', 'Murcko_scaffold')
        
    def _extract(self, data):
        request_dict = super()._extract(data)
        try:
            mol = extract_mol(data['query'])
            request_dict['smiles'] = mol
        except:
            logger.debug(f"Failed to extract molecule from {data['query']}")
            return None
        
        request_dict['largest_scaffold'] = data['gt']
        
        return request_dict