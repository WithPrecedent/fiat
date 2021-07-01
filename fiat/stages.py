"""
base:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import collections.abc
import copy
import dataclasses
import itertools
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo
import more_itertools

import fiat

WorkflowSources: Type = Union[denovo.structures.System, 
                              denovo.structures.Adjacency, 
                              denovo.structures.Edges, 
                              denovo.structures.Matrix, 
                              denovo.structures.Nodes]
 
 

@dataclasses.dataclass
class Outline(denovo.configuration.Settings):
    """fiat project settings with convenient accessors.

    Args:
        contents (denovo.configuration.TwoLevel): a two-level nested dict for 
            storing configuration options. Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.

    """
    contents: denovo.configuration.TwoLevel = dataclasses.field(
        default_factory = dict)
    default_factory: Any = dataclasses.field(default_factory = dict)
    default: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    project: fiat.Project = None
    sources: ClassVar[Mapping[Type, str]] = denovo.configuration._sources

    """ Properties """
    
    # @property
    # def bases(self) -> Dict[str, str]:
    #     return self._get_bases()
    
    @property
    def connections(self) -> Dict[str, List[str]]:
        return self._get_connections()

    @property
    def designs(self) -> Dict[str, str]:
        return self._get_designs()

    @property
    def nodes(self) -> List[str]:
        key_nodes = list(self.connections.keys())
        value_nodes = list(
            itertools.chain.from_iterable(self.connections.values()))
        return denovo.tools.deduplicate(iterable = key_nodes + value_nodes) 
    
    @property
    def parents(self) -> Dict[str, str]:
        return self._get_parents()
            
    """ Private Methods """

    # def _get_bases(self) -> Dict[str, str]:  
    #     suffixes = self.project.library.subclasses.suffixes 
    #     parents = self.parents
    #     bases = {}
    #     for name in self.nodes:
    #         section = parents[name]
    #         component_keys = [
    #             k for k in self[section].keys() if k.endswith(suffixes)]
    #         if component_keys:
    #             bases[name] = settings_to_base(
    #                 name = name,
    #                 section = parents[name])
    #             for key in component_keys:
    #                 prefix, suffix = denovo.tools.divide_string(key)
    #                 values = denovo.tools.listify(self[section][key])
    #                 if suffix.endswith('s'):
    #                     design = suffix[:-1]
    #                 else:
    #                     design = suffix            
    #                 bases.update(dict.fromkeys(values, design))
    #     return bases
      
    def _get_connections(self) -> Dict[str, List[str]]:
        """[summary]

        Returns:
            Dict[str, List[str]]: [description]
            
        """
        suffixes = self.project.library.subclasses.suffixes 
        connections = {}
        for name, section in self.items():
            component_keys = [k for k in section.keys() if k.endswith(suffixes)]
            for key in component_keys:
                prefix, suffix = denovo.tools.divide_string(key)
                values = denovo.tools.listify(section[key])
                if prefix == suffix:
                    if name in connections:
                        connections[name].extend(values)
                    else:
                        connections[name] = values
                else:
                    if prefix in connections:
                        connections[prefix].extend(values)
                    else:
                        connections[prefix] = values
        return connections
    
    def _get_designs(self) -> Dict[str, str]:  
        """[summary]

        Returns:
            Dict[str, str]: [description]
            
        """
        suffixes = self.project.library.subclasses.suffixes 
        parents = self.parents
        designs = {}
        for name in self.nodes:
            section = parents[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                designs[name] = settings_to_base(
                    name = name,
                    section = parents[name])
                for key in component_keys:
                    prefix, suffix = denovo.tools.divide_string(key)
                    values = denovo.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    designs.update(dict.fromkeys(values, design))
        return designs
    
    def _get_parents(self) -> Dict[str, str]:
        suffixes = self.project.library.subclasses.suffixes 
        parents = {}
        for name, section in self.items():
            component_keys = [k for k in section.keys() if k.endswith(suffixes)]
            if component_keys:
                parents[name] = name
                for key in component_keys:
                    values = denovo.tools.listify(section[key])
                    parents.update(dict.fromkeys(values, name))
        return parents

    
@dataclasses.dataclass
class Workflow(denovo.structures.System):
    """Project workflow implementation as a directed acyclic graph (DAG).
    
    Workflow stores its graph as an adjacency list. Despite being called an 
    "adjacency list," the typical and most efficient way to create one in python
    is using a dict. The keys of the dict are the nodes and the values are sets
    of the hashable summarys of other nodes.

    Workflow internally supports autovivification where a set is created as a 
    value for a missing key. 
    
    Args:
        contents (Adjacency): an adjacency list where the keys are nodes and the 
            values are sets of hash keys of the nodes which the keys are 
            connected to. Defaults to an empty a defaultdict described in 
            '_DefaultAdjacency'.
                  
    """  
    contents: denovo.structures.Adjacency = dataclasses.field(
        default_factory = lambda: collections.defaultdict(set))
    
    """ Properties """
    
    @property
    def cookbook(self) -> fiat.base.Cookbook:
        """Returns the stored workflow as a Cookbook of Recipes."""
        return workflow_to_cookbook(source = self)
            
    """ Dunder Methods """

    def __str__(self) -> str:
        """Returns prettier summary of the stored graph.

        Returns:
            str: a formatted str of class information and the contained 
                adjacency list.
            
        """
        return denovo.tools.beautify(item = self, package = 'fiat')
