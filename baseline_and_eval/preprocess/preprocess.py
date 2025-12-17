from . import mol_edit
from . import mol_opt
from . import mol_und
from . import rxn

def get_preprocessors(path):
    preprocessors = []
    preprocessors += mol_edit.get_preprocessors(path)
    preprocessors += mol_opt.get_preprocessors(path)
    preprocessors += mol_und.get_preprocessors(path)
    preprocessors += rxn.get_preprocessors(path)
    return preprocessors