"""
fiat: a simple, lightweight, flexible project system
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'fiat'. This 
        dict is needed for the 'importify' function which is called by this 
        modules '__getattr__' function.

"""
__version__ = '0.1.0'

__package__ = 'fiat'

__author__ = 'Corey Rayburn Yung'


from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


importables: Dict[str, str] = {'Director': 'base.Director',
                               'Parameters': 'base.Parameters',
                               'Project': 'interface.Project',
                               'Task': 'base.Task',
                               'Workflow': 'base.Workflow'}

def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them as package attributes.
    
    Args:
        name (str): name of fiat module or item being sought.

    Returns:
        Any: a module or item stored within a module.
        
    """
    package = __package__ or __name__
    return denovo.lazy.importify(name = name, 
                                 package = package, 
                                 importables = importables)
