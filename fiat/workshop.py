"""
workshop: functions for converting fiat objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import itertools
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import denovo
import more_itertools

import fiat


""" Configuration Parsing Functions """

def settings_to_outline(settings: fiat.shared.bases.settings, 
                        **kwargs) -> fiat.Outline:
    """[summary]

    Args:
        settings (fiat.shared.bases.settings): [description]

    Returns:
        Outline: derived from 'settings'.
        
    """
    suffixes = denovo.shared.library.subclasses.suffixes
    outline = fiat.Outline(**kwargs)
    section_base = fiat.stages.Section
    for name, section in settings.items():
        if any(k.endswith(suffixes) for k in section.keys()):
            outline[name] = section_base.from_settings(settings = settings,
                                                       name = name)
    return outline
    
def create_workflow(project: fiat.Project, **kwargs) -> fiat.Workflow:
    """[summary]

    Args:
        project (fiat.Project): [description]

    Returns:
        fiat.Workflow: [description]
        
    """
    workflow = outline_to_workflow(outline = project.outline,
                                   library = project.library,
                                   **kwargs)
    return workflow

def outline_to_workflow(outline: fiat.Outline, **kwargs) -> fiat.Workflow:
    """[summary]

    Args:
        outline (fiat.Outline): [description]
        library (denovo.containers.Library): [description]

    Returns:
        fiat.Workflow: [description]
        
    """
    for name in outline.nodes:
        outline_to_component(name = name, outline = outline)
    workflow = fiat.shared.bases.workflow
    workflow = outline_to_system(outline = outline, **kwargs)
    return workflow 
 
def outline_to_system(outline: fiat.Outline) -> fiat.Workflow:
    """[summary]

    Args:
        outline (fiat.Outline): [description]
        library (nodes.Library, optional): [description]. Defaults to None.
        connections (Dict[str, List[str]], optional): [description]. Defaults 
            to None.

    Returns:
        fiat.structures.Graph: [description]
        
    """    
    connections = connections or outline_to_connections(
        outline = outline, 
        library = library)
    graph = fiat.structures.Graph()
    for node in connections.keys():
        kind = library.classify(component = node)
        method = locals()[f'finalize_{kind}']
        graph = method(
            node = node, 
            connections = connections,
            library = library, 
            graph = graph)     
    return graph

def outline_to_component(name: str, 
                         outline: fiat.Outline, 
                         **kwargs) -> fiat.base.Component:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        outline (fiat.Outline): [description]
        library (nodes.Library, optional): [description]. Defaults to None.
        connections (Dict[str, List[str]], optional): [description]. Defaults 
            to None.
        design (str, optional): [description]. Defaults to None.
        recursive (bool, optional): [description]. Defaults to True.
        overwrite (bool, optional): [description]. Defaults to False.

    Returns:
        nodes.Component: [description]
    
    """
    design = outline.designs[name] or None
    base = outline.bases[name]
    initialization = outline_to_initialization(
        name = name, 
        design = design,
        section = section, 
        outline = outline,
        library = library)
    initialization.update(kwargs)
    if 'parameters' not in initialization:
        initialization['parameters'] = outline_to_implementation(
            name = name, 
            design = design,
            outline = outline)
    component = library.instance(name = [name, design], **initialization)
    return component

def outline_to_initialization(
    name: str, 
    section: str,
    design: str,
    outline: fiat.Outline,
    library: nodes.Library) -> Dict[Hashable, Any]:
    """Gets parameters for a specific Component from 'outline'.

    Args:
        name (str): [description]
        section (str): [description]
        design (str): [description]
        outline (fiat.Outline): [description]
        library (nodes.Library): [description]

    Returns:
        Dict[Hashable, Any]: [description]
        
    """
    suboutline = outline[section]
    parameters = library.parameterify(name = [name, design])
    possible = tuple(i for i in parameters if i not in ['name', 'contents'])
    parameter_keys = [k for k in suboutline.keys() if k.endswith(possible)]
    kwargs = {}
    for key in parameter_keys:
        prefix, suffix = fiat.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            kwargs[suffix] = suboutline[key]
    return kwargs  
        
def outline_to_implementation(
    name: str, 
    design: str,
    outline: fiat.Outline) -> Dict[Hashable, Any]:
    """[summary]

    Args:
        name (str): [description]
        design (str): [description]
        outline (fiat.Outline): [description]

    Returns:
        Dict[Hashable, Any]: [description]
        
    """
    try:
        parameters = outline[f'{name}_parameters']
    except KeyError:
        try:
            parameters = outline[f'{design}_parameters']
        except KeyError:
            parameters = {}
    return parameters

def finalize_serial(
    node: str,
    connections: Dict[str, List[str]],
    library: nodes.Library,
    graph: fiat.structures.Graph) -> fiat.structures.Graph:
    """[summary]

    Args:
        node (str): [description]
        connections (Dict[str, List[str]]): [description]
        library (nodes.Library): [description]
        graph (fiat.structures.Graph): [description]

    Returns:
        fiat.structures.Graph: [description]
        
    """    
    connections = _serial_order(
        name = node, 
        connections = connections)
    nodes = list(more_itertools.collapse(connections))
    if nodes:
        graph.extend(nodes = nodes)
    return graph      

def _serial_order(
    name: str,
    connections: Dict[str, List[str]]) -> List[Hashable]:
    """[summary]

    Args:
        name (str): [description]
        directive (core.Directive): [description]

    Returns:
        List[Hashable]: [description]
        
    """   
    organized = []
    components = connections[name]
    for item in components:
        organized.append(item)
        if item in connections:
            organized_connections = []
            connections = _serial_order(
                name = item, 
                connections = connections)
            organized_connections.append(connections)
            if len(organized_connections) == 1:
                organized.append(organized_connections[0])
            else:
                organized.append(organized_connections)
    return organized   


""" Workflow Executing Functions """

def workflow_to_summary(project: fiat.Project, **kwargs) -> fiat.Project:
    """[summary]

    Args:
        project (fiat.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    # summary = None
    # print('test workflow', project.workflow)
    # print('test paths', project.workflow.paths)
    # print('test parser contents', library.instances['parser'].contents)
    # print('test parser paths', library.instances['parser'].paths)
    summary = configuration.SUMMARY()
    print('test project paths', project.workflow.paths)
    # for path in enumerate(project.workflow.paths):
    #     name = f'{summary.prefix}_{i + 1}'
    #     summary.add({name: workflow_to_result(
    #         path = path,
    #         project = project,
    #         data = project.data)})
    return summary
        
def workflow_to_result(
    path: Sequence[str],
    project: fiat.Project,
    data: Any = None,
    library: nodes.Library = None,
    result: core.Result = None,
    **kwargs) -> object:
    """[summary]

    Args:
        name (str): [description]
        path (Sequence[str]): [description]
        project (fiat.Project): [description]
        data (Any, optional): [description]. Defaults to None.
        library (nodes.Library, optional): [description]. Defaults to None.
        result (core.Result, optional): [description]. Defaults to None.

    Returns:
        object: [description]
        
    """    
    library = library or configuration.LIBRARY
    result = result or configuration.RESULT
    data = data or project.data
    result = result()
    for node in path:
        print('test node in path', node)
        try:
            component = library.instance(name = node)
            result.add(component.execute(project = project, **kwargs))
        except (KeyError, AttributeError):
            pass
    return result
