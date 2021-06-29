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

WorkflowSources: Type = Union[denovo.structures.DirectedGraph, 
                              denovo.structures.Adjacency, 
                              denovo.structures.Edges, 
                              denovo.structures.Matrix, 
                              denovo.structures.Nodes]
 
 

@dataclasses.dataclass
class Outline(denovo.configuration.Settings):
    """Loads and stores configuration settings for a fiat Project.

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
    
    @property
    def bases(self) -> Dict[str, str]:
        return self._get_bases()
    
    @property
    def connections(self) -> Dict[str, List[str]]:
        return self._get_connections()

    @property
    def designs(self) -> Dict[str, str]:
        return self._get_designs()
    
    @property
    def managers(self) -> Dict[str, str]:
        return self._get_managers()
     
    @property
    def nodes(self) -> List[str]:
        key_nodes = list(self.connections.keys())
        value_nodes = list(
            itertools.chain.from_iterable(self.connections.values()))
        return denovo.tools.deduplicate(iterable = key_nodes + value_nodes) 
        
    """ Private Methods """

    def _get_bases(self) -> Dict[str, str]:  
        suffixes = self.project.library.subclasses.suffixes 
        managers = self.managers
        bases = {}
        for name in self.nodes:
            section = managers[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                bases[name] = settings_to_base(
                    name = name,
                    section = managers[name])
                for key in component_keys:
                    prefix, suffix = denovo.tools.divide_string(key)
                    values = denovo.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    bases.update(dict.fromkeys(values, design))
        return bases
      
    def _get_connections(self) -> Dict[str, List[str]]:
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
        suffixes = self.project.library.subclasses.suffixes 
        managers = self.managers
        designs = {}
        for name in self.nodes:
            section = managers[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                designs[name] = settings_to_base(
                    name = name,
                    section = managers[name])
                for key in component_keys:
                    prefix, suffix = denovo.tools.divide_string(key)
                    values = denovo.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    designs.update(dict.fromkeys(values, design))
        return designs
    
    def _get_managers(self) -> Dict[str, str]:
        suffixes = self.project.library.subclasses.suffixes 
        managers = {}
        for name, section in self.items():
            component_keys = [k for k in section.keys() if k.endswith(suffixes)]
            if component_keys:
                managers[name] = name
                for key in component_keys:
                    values = denovo.tools.listify(section[key])
                    managers.update(dict.fromkeys(values, name))
        return managers

    
@dataclasses.dataclass
class Workflow(denovo.structures.DirectedGraph):
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
    def adjacency(self) -> denovo.structures.Adjacency:
        """Returns the stored graph as an adjacency list."""
        return self.contents

    @property
    def cookbook(self) -> fiat.base.Cookbook:
        """Returns the stored workflow as a Cookbook of Recipes."""
        return workflow_to_cookbook(source = self)
    
    @property
    def edges(self) -> denovo.structures.Edges:
        """Returns the stored graph as an edge list."""
        return denovo.structures.adjacency_to_edges(source = self.contents)

    @property
    def endpoints(self) -> Set[Hashable]:
        """Returns endpoint nodes in the stored graph in a list."""
        return {k for k in self.contents.keys() if not self.contents[k]}

    @property
    def matrix(self) -> denovo.structures.Matrix:
        """Returns the stored graph as an adjacency matrix."""
        return denovo.structures.adjacency_to_matrix(source = self.contents)
                      
    @property
    def nodes(self) -> Set[Hashable]:
        """Returns all stored nodes in a list."""
        return set(self.contents.keys())

    @property
    def paths(self) -> denovo.structures.Pipelines:
        """Returns all paths through the stored graph as Pipeline."""
        return self._find_all_paths(starts = self.roots, stops = self.endpoints)
       
    @property
    def roots(self) -> Set[Hashable]:
        """Returns root nodes in the stored graph in a list."""
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        return {k for k in self.contents.keys() if k not in stops}
    
    """ Class Methods """
 
    @classmethod
    def from_adjacency(cls, adjacency: denovo.structures.Adjacency) -> Workflow:
        """Creates a Workflow instance from an adjacency list."""
        return cls(contents = adjacency)
    
    @classmethod
    def from_edges(cls, edges: denovo.structures.Edges) -> Workflow:
        """Creates a Workflow instance from an edge list."""
        return cls(contents = denovo.structures.edges_to_adjacency(
            source = edges))
    
    @classmethod
    def from_matrix(cls, matrix: denovo.structures.Matrix) -> Workflow:
        """Creates a Workflow instance from an adjacency matrix."""
        return cls(contents = denovo.structures.matrix_to_adjacency(
            source = matrix))
    
    @classmethod
    def from_pipeline(cls, pipeline: denovo.structures.Pipeline) -> Workflow:
        """Creates a Workflow instance from a Pipeline."""
        return cls(contents = denovo.structures.pipeline_to_adjacency(
            source = pipeline))
       
    """ Public Methods """
    
    def add(self, 
            node: Hashable,
            ancestors: denovo.structures.Nodes = None,
            descendants: denovo.structures.Nodes = None) -> None:
        """Adds 'node' to the stored graph.
        
        Args:
            node (Hashable): a node to add to the stored graph.
            ancestors (Nodes): node(s) from which 'node' should be connected.
            descendants (Nodes): node(s) to which 'node' should be connected.

        Raises:
            KeyError: if some nodes in 'descendants' or 'ancestors' are not in 
                the stored graph.
                
        """
        if descendants is None:
            self.contents[node] = set()
        elif denovo.tools.is_property(item = descendants, instance = self):
            self.contents = set(getattr(self, descendants))
        else:
            descendants = denovo.tools.listify(descendants)
            descendants = [self._stringify(n) for n in descendants]
            missing = [n for n in descendants if n not in self.contents]
            if missing:
                raise KeyError(f'descendants {str(missing)} are not in the '
                               f'stored graph.')
            else:
                self.contents[node] = set(descendants)
        if ancestors is not None:  
            if denovo.tools.is_property(item = ancestors, instance = self):
                start = list(getattr(self, ancestors))
            else:
                ancestors = denovo.tools.listify(ancestors)
                missing = [n for n in ancestors if n not in self.contents]
                if missing:
                    raise KeyError(f'ancestors {str(missing)} are not in the '
                                   f'stored graph.')
                else:
                    start = ancestors
            for starting in start:
                if node not in self[starting]:
                    self.connect(start = starting, stop = node)                 
        return self 

    def append(self, item: WorkflowSources) -> None:
        """Appends 'item' to the endpoints of the stored graph.

        Appending creates an edge between every endpoint of this instance's
        stored graph and the every root of 'item'.

        Args:
            item (Union[Graph, Adjacency, Edges, Matrix, Nodes]): another Graph, 
                an adjacency list, an edge list, an adjacency matrix, or one or
                more nodes.
            
        Raises:
            TypeError: if 'source' is neither a Graph, Adjacency, Edges, Matrix,
                or Nodes type.
                
        """
        if isinstance(item, (denovo.structures.DirectedGraph, 
                             denovo.structures.Adjacency, 
                             denovo.structures.Edges, 
                             denovo.structures.Matrix, 
                             denovo.structures.Nodes)):
            current_endpoints = list(self.endpoints)
            new_graph = self.create(source = item)
            self.merge(item = new_graph)
            for endpoint in current_endpoints:
                for root in new_graph.roots:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError('item must be a DirectedGraph, Adjacency, Edges, '
                            'Matrix, Pipeline, or Hashable type')
        return self
  
    def connect(self, start: Hashable, stop: Hashable) -> None:
        """Adds an edge from 'start' to 'stop'.

        Args:
            start (Hashable): name of node for edge to start.
            stop (Hashable): name of node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError('The start of an edge cannot be the same as the '
                             'stop in a Workflow because it is acyclic')
        elif start not in self:
            self.add(node = start)
        elif stop not in self:
            self.add(node = stop)
        if stop not in self.contents[start]:
            self.contents[start].add(self._stringify(stop))
        return self

    def delete(self, node: Hashable) -> None:
        """Deletes node from graph.
        
        Args:
            node (Hashable): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'node' is not in 'contents'.
            
        """
        try:
            del self.contents[node]
        except KeyError:
            raise KeyError(f'{node} does not exist in the graph')
        self.contents = {k: v.discard(node) for k, v in self.contents.items()}
        return self

    def disconnect(self, start: Hashable, stop: Hashable) -> None:
        """Deletes edge from graph.

        Args:
            start (Hashable): starting node for the edge to delete.
            stop (Hashable): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' is not a node in the stored graph..

        """
        try:
            self.contents[start].discard(stop)
        except KeyError:
            raise KeyError(f'{start} does not exist in the graph')
        return self

    def merge(self, item: WorkflowSources) -> None:
        """Adds 'item' to this Graph.

        This method is roughly equivalent to a dict.update, just adding the
        new keys and values to the existing graph. It converts the WorkflowSources
        formats to an adjacency list that is then added to the existing 
        'contents'.
        
        Args:
            item (WorkflowSources): another Graph, an adjacency list, an edge list, an 
                adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a DirectedGraph, Adjacency, Edges, 
                Matrix, or Nodes type.
            
        """
        if isinstance(item, denovo.structures.DirectedGraph):
            adjacency = item.adjacency
        elif isinstance(item, denovo.structures.Adjacency):
            adjacency = item
        elif isinstance(item, denovo.structures.Edges):
            adjacency = denovo.structures.edges_to_adjacency(source = item)
        elif isinstance(item, denovo.structures.Matrix):
            adjacency = denovo.structures.matrix_to_adjacency(source = item)
        elif isinstance(item, (MutableSequence, Tuple, Set)):
            adjacency = denovo.structures.pipeline_to_adjacency(source = item)
        elif isinstance(item, Hashable):
            adjacency = {item: set()}
        else:
            raise TypeError('item must be a DirectedGraph, Adjacency, Edges, '
                            'Matrix, Pipeline, or Hashable type')
        self.contents.update(adjacency)
        return self

    def prepend(self, item: WorkflowSources) -> None:
        """Prepends 'item' to the roots of the stored graph.

        Prepending creates an edge between every endpoint of 'item' and every
        root of this instance;s stored graph.

        Args:
            item (WorkflowSources): another DirectedGraph, an adjacency list, an edge 
                list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'source' is neither a DirectedGraph, Adjacency, Edges, 
                Matrix, or Nodes type.
                
        """
        if isinstance(item, (denovo.structures.DirectedGraph, 
                             denovo.structures.Adjacency, 
                             denovo.structures.Edges, 
                             denovo.structures.Matrix, 
                             denovo.structures.Nodes)):
            current_roots = list(self.roots)
            new_graph = self.create(source = item)
            self.merge(item = new_graph)
            for root in current_roots:
                for endpoint in new_graph.endpoints:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError('item must be a DirectedGraph, Adjacency, Edges, '
                            'Matrix, Pipeline, or Hashable type')
        return self
      
    def subset(self, 
               include: Union[Any, Sequence[Any]] = None,
               exclude: Union[Any, Sequence[Any]] = None) -> Workflow:
        """Returns a new Workflow without a subset of 'contents'.
        
        All edges will be removed that include any nodes that are not part of
        the new subgraph.
        
        Any extra attributes that are part of a Workflow (or a subclass) will be
        maintained in the returned subgraph.

        Args:
            include (Union[Any, Sequence[Any]]): nodes which should be included
                with any applicable edges in the new subgraph.
            exclude (Union[Any, Sequence[Any]]): nodes which should not be 
                included with any applicable edges in the new subgraph.

        Returns:
           Workflow: with only key/value pairs with keys not in 'subset'.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        else:
            if include:
                excludables = [k for k in self.contents if k not in include]
            else:
                excludables = []
            excludables.extend([i for i in self.contents if i in exclude])
            new_graph = copy.deepcopy(self)
            for node in more_itertools.always_iterable(excludables):
                new_graph.delete(node = node)
        return new_graph
    
    def walk(self, 
             start: Hashable, 
             stop: Hashable, 
             path: denovo.structures.Pipeline = None) -> (
                 denovo.structures.Pipeline):
        """Returns all paths in graph from 'start' to 'stop'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (Hashable): node to start paths from.
            stop (Hashable): node to stop paths.
            path (Pipeline): a path from 'start' to 'stop'. Defaults to an 
                empty list. 

        Returns:
            Pipeline: a list of possible paths (each path is a list 
                nodes) from 'start' to 'stop'.
            
        """
        if path is None:
            path = []
        path = path + [start]
        if start == stop:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self.walk(
                    start = node, 
                    stop = stop, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    """ Private Methods """

    def _find_all_paths(self, 
                        starts: Union[Hashable, Sequence[Hashable]],
                        stops: Union[Hashable, Sequence[Hashable]]) -> (
                            denovo.structures.Pipeline):
        """Returns all paths between 'starts' and 'stops'.

        Args:
            start (Union[Hashable, Sequence[Hashable]]): starting points for 
                paths through the Workflow.
            ends (Union[Hashable, Sequence[Hashable]]): endpoints for paths 
                through the Workflow.

        Returns:
            Pipeline: list of all paths through the Workflow from all 'starts' 
                to all 'ends'.
            
        """
        all_paths = []
        for start in more_itertools.always_iterable(starts):
            for end in more_itertools.always_iterable(stops):
                paths = self.walk(start = start, stop = end)
                if paths:
                    if all(isinstance(path, Hashable) for path in paths):
                        all_paths.append(paths)
                    else:
                        all_paths.extend(paths)
        return all_paths
            
    """ Dunder Methods """

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Hashable): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: Hashable) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self

    def __str__(self) -> str:
        """Returns prettier summary of the stored graph.

        Returns:
            str: a formatted str of class information and the contained 
                adjacency list.
            
        """
        return denovo.tools.beautify(item = self, package = 'fiat')
