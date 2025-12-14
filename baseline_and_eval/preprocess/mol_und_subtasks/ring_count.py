from ..preprocessor import Preprocessor
import regex as re
import json

mol_pattern_mol_ring = re.compile(r'Input Molecule:\s*(?P<smiles>.+?)\s*,\s*Ring Structure:(?P<ring>.+?)\s*\.$', re.S)

def extract_mol_ring(query_str):
    match = mol_pattern_mol_ring.search(query_str)
    if match:
        mol, ring = match.group('smiles').strip(), match.group('ring').strip()
        return mol, ring
    else:
        raise Exception('Query not match pattern')
    
class RingCountPreprocessor(Preprocessor):
    def __init__(self, base_data_path):
        super().__init__(f'{base_data_path}/mol_und/ring_count.json', 'ring_count')
        
    def _extract(self, data):
        request_dict = super()._extract(data)
        try:
            mol, ring = extract_mol_ring(data['query'])
            request_dict['smiles'] = mol
            request_dict['ring'] = ring
        except:
            print(f"Failed to extract molecule from {data['query']}")
            return None
        
        request_dict['count'] = data['gt']
        
        return request_dict