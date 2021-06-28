"""
core:
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

import more_itertools

import denovo
from . import configuration
from . import workshop

 
@dataclasses.dataclass
class Director(collections.abc.Iterator):
    
    project: Project = None
    stages: Sequence[str] = dataclasses.field(default_factory = dict)
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


basic_director = Director(stages = {
    'initialize': 'settings', 
    'draft': 'workflow', 
    'execute': 'summary'})
