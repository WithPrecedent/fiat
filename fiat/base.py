"""
base:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
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
class Director(collections.abc.Iterator):
    
    project: fiat.Project = None
    stages: Sequence[str] = dataclasses.field(default_factory = list)
    workshop: ModuleType = denovo.project.workshop

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets index for iteration.
        self.index = 0
        
    """ Properties """
    
    @property
    def current(self) -> str:
        return list(self.stages.keys())[self.index]
    
    @property
    def subsequent(self) -> str:
        try:
            return list(self.stages.keys())[self.index + 1]
        except IndexError:
            return None
       
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self
        
    # def functionify(self, source: str, product: str) -> str:
    #     """[summary]

    #     Args:
    #         source (str): [description]
    #         product (str): [description]

    #     Returns:
    #         str: [description]
            
    #     """        
    #     name = f'{source}_to_{product}'
    #     return getattr(self.workshop, name)

    # def kwargify(self, func: Callable) -> Dict[Hashable, Any]:
    #     """[summary]

    #     Args:
    #         func (Callable): [description]

    #     Returns:
    #         Dict[Hashable, Any]: [description]
            
    #     """        
    #     parameters = inspect.signature(func).parameters.keys()
    #     kwargs = {}
    #     for parameter in parameters:
    #         try:
    #             kwargs[parameter] = getattr(self.project, parameter)
    #         except AttributeError:
    #             pass
    #     return kwargs
    
    """ Dunder Methods """

    # def __getattr__(self, attribute: str) -> Any:
    #     """[summary]

    #     Args:
    #         attribute (str): [description]

    #     Raises:
    #         IndexError: [description]

    #     Returns:
    #         Any: [description]
            
    #     """
    #     if attribute in self.stages:
    #         if attribute == self.subsequent:
    #             self.__next__()
    #         else:
    #             raise IndexError(
    #                 f'You cannot call {attribute} because the current stage is '
    #                 f'{self.current} and the next callable stage is '
    #                 f'{self.subsequent}')  
    #     else:
    #         raise KeyError(f'{attribute} is not in {self.__class__.__name__}')             
            
    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.
        
        Returns:
            Iterable: of the Project instance.
            
        """
        return self
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index + 1 < len(self.stages):
            source = self.stages[self.current]
            product = self.stages[self.subsequent]
            # director = self.functionify(source = source, product = product)
            director = getattr(self.workshop, f'create_{product}')
            if hasattr(configuration, 'VERBOSE') and configuration.VERBOSE:
                print(f'Creating {product}')
            kwargs = {'project': self.project}
            setattr(self.project, product, director(**kwargs))
            self.index += 1
            if hasattr(configuration, 'VERBOSE') and configuration.VERBOSE:
                print(f'Completed {product}')
        else:
            raise StopIteration
        return self


@dataclasses.dataclass    
class Parameters(denovo.base.Lexicon):
    """Creates and stores parameters for a Component.
    
    The use of Parameters is entirely optional, but it provides a handy tool
    for aggregating data from an array of sources, including those which only 
    become apparent during execution of an fiat project, to create a unified 
    set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the 'contents' 
    attribute an ordinary set of kwargs. In this way, it can serve as a drop-in
    replacement for a dict that would ordinarily be used for accumulating 
    keyword arguments.
    
    If an fiat class uses a Parameters instance, the 'finalize' method should
    be called before that instance's 'implement' method in order for each of the
    parameter types to be incorporated.
    
    Args:
        contents (Mapping[str, Any]): keyword parameters for use by an fiat
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout fiat. To properly match parameters
            in an Outline instance, 'name' should be the prefix to "_parameters"
            as a section name in an Outline instance. Defaults to None. 
        default (Mapping[str, Any]): default parameters that will be used if 
            they are not overridden. Defaults to an empty dict.
        implementation (Mapping[str, str]): parameters with values that can only 
            be determined at runtime due to dynamic nature of fiat and its 
            workflows. The keys should be the names of the parameters and the 
            values should be attributes or items in 'contents' of 'project' 
            passed to the 'finalize' method. Defaults to an emtpy dict.
        selected (Sequence[str]): an exclusive list of parameters that are 
            allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in an Outline instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(
        default_factory = dict)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, project: fiat.Project, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            project (fiat.Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting base.
        parameters = self.default
        parameters.update(kwargs)
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(settings = project.settings))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(project = project))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Limits parameters to those in 'selected'.
        if self.selected:
            self.contents = {k: self.contents[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_settings(self, 
        settings: fiat.options.Outline) -> Dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (fiat.options.Outline): instance with possible 
                parameters.

        Returns:
            Dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        try:
            parameters = settings[f'{self.name}_parameters']
        except KeyError:
            suffix = self.name.split('_')[-1]
            prefix = self.name[:-len(suffix) - 1]
            try:
                parameters = settings[f'{prefix}_parameters']
            except KeyError:
                try:
                    parameters = settings[f'{suffix}_parameters']
                except KeyError:
                    parameters = {}
        return parameters
   
    def _at_runtime(self, project: fiat.Project) -> Dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            project (fiat.Project): instance from which implementation 
                parameters can be derived.

        Returns:
            Dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(project, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = project.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        return self




@dataclasses.dataclass
class Stage(denovo.containers.Lexicon, abc.ABC):
    
    pass
    
    

@dataclasses.dataclass
class Worker(denovo.quirks.Element, collections.abc.Iterable, abc.ABC):
    """Keystone class for parts of an fiat workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout fiat. For example, if a fiat 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                              
    """
    name: str = None
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1

    """ Public Methods """  

    def organize(self, subcomponents: Dict[str, List[str]]) -> None:
        """[summary]

        Args:
            subcomponents (Dict[str, List[str]]): [description]

        """
        subcomponents = self._serial_order(
            name = self.name, 
            subcomponents = subcomponents)
        nodes = list(more_itertools.collapse(subcomponents))
        if nodes:
            self.extend(nodes = nodes)
        return self       

    def implement(self, project: fiat.Project, **kwargs) -> fiat.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (fiat.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            fiat.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    

    """ Private Methods """

    def _implement_in_serial(self, 
                             project: fiat.Project,
                             **kwargs) -> fiat.Project:
        """Applies stored nodes to 'project' in order.

        Args:
            project (Project): fiat project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        for node in self.paths[0]:
            project = node.execute(project = project, **kwargs)
        return project
       
    def _serial_order(self, 
                      name: str,
                      subcomponents: Dict[str, List[str]]) -> List[Hashable]:
        """[summary]

        Args:
            name (str): [description]
            directive (Directive): [description]

        Returns:
            List[Hashable]: [description]
            
        """   
        organized = []
        components = subcomponents[name]
        for item in components:
            organized.append(item)
            if item in subcomponents:
                organized_subcomponents = []
                subcomponents = self._serial_order(
                    name = item, 
                    subcomponents = subcomponents)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized   
  
   