from .preprocessor import Preprocessor
import regex as re
import json

from .mol_und_subtasks.equivalence import EquivalencePreProcessor
from .mol_und_subtasks.fg_count import FGCountPreprocessor
from .mol_und_subtasks.Murcko_scaffold import MurckoScaffoldProcessor
from .mol_und_subtasks.ring_count import RingCountPreprocessor
from .mol_und_subtasks.ring_system_scaffold import RingSystemScaffoldPreprocessor

def get_preprocessors(base_path):
    return [
        EquivalencePreProcessor(base_path),
        FGCountPreprocessor(base_path),
        MurckoScaffoldProcessor(base_path),
        RingCountPreprocessor(base_path),
        RingSystemScaffoldPreprocessor(base_path)
    ]