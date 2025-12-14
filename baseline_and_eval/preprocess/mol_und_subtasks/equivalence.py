from ..preprocessor import Preprocessor
import regex as re
import json

mol_pattern_A_B = re.compile(r'Molecule A:\s*(?P<smilesA>.+?)\s*,\s*Molecule B:(?P<smilesB>.+?)\s*\.$', re.S)

def extract_mols_A_B(query_str):
    match = mol_pattern_A_B.search(query_str)
    if match:
        A, B = match.group('smilesA').strip(), match.group('smilesB').strip()
        return A, B
    else:
        raise Exception('Query not match pattern')
    
class EquivalencePreProcessor(Preprocessor):
    def __init__(self, base_path):
        super().__init__(f'{base_path}/mol_und/equivalence.json', 'equivalence')
        
    def _extract(self, data):
        request_dict = super()._extract(data)
        try:
            molA, molB = extract_mols_A_B(data['query'])
            request_dict['src_smiles'] = molA
            request_dict['tgt_smiles'] = molB
        except:
            print(f"Failed to extract molecule from {data['query']}")
            return None
        
        request_dict['gt'] = data['gt']
        
        return request_dict