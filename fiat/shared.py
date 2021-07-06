"""
shared: resources and settings accessible across fiat
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo


""" Shared Annotation Types """

ClerkSources: Type = Union[denovo.filing.Clerk, 
                           Type[denovo.filing.Clerk], 
                           pathlib.Path, 
                           str]   
SettingsSources: Type = Union[denovo.configuration.Settings, 
                              Type[denovo.configuration.Settings], 
                              Mapping[str, Mapping[str, Any]],
                              pathlib.Path, 
                              str]

WorkflowSources: Type = Union[denovo.structures.System, 
                              denovo.structures.Adjacency, 
                              denovo.structures.Edges, 
                              denovo.structures.Matrix, 
                              denovo.structures.Nodes]

""" Shared Constants """

PARALLELIZE: bool = False
GPU: bool = False
VERBOSE: bool = False

""" Shared Mutable Objects """

library: denovo.containers.Library = denovo.containers.Library()


@dataclasses.dataclass
class Bases(denovo.quirks.Importer):
    
    clerk: Union[str, Type] = 'denovo.filing.Clerk'
    director: Union[str, Type] = 'fiat.base.Director'
    library: Union[str, Type] = 'denovo.containers.Library'
    outline: Union[str, Type] = 'fiat.stages.Outline'
    parameters: Union[str, Type] = 'fiat.stages.Parameters'
    report: Union[str, Type] = 'fiat.stages.Report'
    section: Union[str, Type] = 'fiat.stages.Section'
    settings: Union[str, Type] = 'denovo.filing.Settings'
    task: Union[str, Type] = 'fiat.base.Task'
    worker: Union[str, Type] = 'fiat.base.Worker'
    workflow: Union[str, Type] = 'fiat.stages.Workflow'
    
    
bases: Bases = Bases()