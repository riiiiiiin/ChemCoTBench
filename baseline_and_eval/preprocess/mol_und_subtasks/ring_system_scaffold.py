from ..preprocessor import Preprocessor
import regex as re
import json
import logging

logger = logging.getLogger(__name__)

mol_pattern_mol_ring_system = re.compile(r'Input Molecule:\s*(?P<smiles>.+?)\s*,\s*Ring System Structure:(?P<ring>.+?)\s*$', re.S)

def extract_mol_ring_system(query_str):
    match = mol_pattern_mol_ring_system.search(query_str)
    if match:
        mol, ring = match.group('smiles').strip(), match.group('ring').strip()
        return mol, ring
    else:
        raise Exception('Query not match pattern')
    
class RingSystemScaffoldPreprocessor(Preprocessor):
    def __init__(self, base_data_path):
        super().__init__(f'{base_data_path}/mol_und/ring_system_scaffold.json', 'ring_system_scaffold')
        
    def _extract(self, data):
        request_dict = super()._extract(data)
        
        try:
            mol, ring = extract_mol_ring_system(data['query'])
            request_dict['smiles'] = mol
            request_dict['ring_system_scaffold'] = ring
        except:
            logger.debug(f"Failed to extract molecule from {data['query']}")
            
        return request_dict