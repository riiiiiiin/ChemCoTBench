from ..preprocessor import Preprocessor
import regex as re
import json
import logging

logger = logging.getLogger(__name__)

mol_pattern_mol_frag = re.compile(r'Input Molecule:\s*(?P<smiles>.+?)\s*,\s*Fragment Name:(?P<frag>.+?)\s*\.$', re.S)

def extract_mol_frag(query_str):
    match = mol_pattern_mol_frag.search(query_str)
    if match:
        mol, frag = match.group('smiles').strip(), match.group('frag').strip()
        return mol, frag
    else:
        raise Exception('Query not match pattern')
    
class FGCountPreprocessor(Preprocessor):
    def __init__(self, base_path):
        super().__init__(f'{base_path}/mol_und/fg_count.json', 'fg_samples')
        
    def _extract(self, data):
        request_dict = super()._extract(data)
        try:
            mol, frag = extract_mol_frag(data['query'])
            request_dict['smiles'] = mol
            request_dict['fg_name'] = frag
        except:
            logger.debug(f"Failed to extract molecule from {data['query']}")
            return None

        meta_dict = json.loads(data['meta'])
        request_dict['fg_smarts'] = meta_dict['fg_smarts']
        request_dict['fg_label'] = meta_dict['fg_label']
    
        request_dict['fg_num'] = data['gt']
        
        return request_dict
    