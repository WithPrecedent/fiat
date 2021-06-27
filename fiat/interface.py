"""
interface: primary access point and interface for a fiat project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Parameters
    Directive
    Outline
    Component
    Result
    Summary

"""
from __future__ import annotations
import collections.abc
import dataclasses
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)
import warnings

import denovo

import fiat

    
ClerkSources: Type = Union[denovo.filing.Clerk, 
                           Type[denovo.filing.Clerk], 
                           pathlib.Path, 
                           str]   
SettingsSources: Type = Union[denovo.configuration.Settings, 
                              Type[denovo.configuration.Settings], 
                              Mapping[str, Mapping[str, Any]],
                              pathlib.Path, 
                              str]




""" Iterator for Constructing Project Stages """
 
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


""" Primary Interface and Access Point """

@dataclasses.dataclass
class Project(denovo.quirks.Element, denovo.quirks.Flexible):
    """Interface for a fiat project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout fiat. For example, if a fiat 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        settings (SettingsSources): a Settings-compatible subclass or instance, 
            a str or pathlib.Path containing the file path where a file of a 
            supported file type with settings for a Settings instance is 
            located, or a 2-level mapping containing settings. Defaults to the 
            default Settings instance.
        clerk (ClerkSources): a Clerk-compatible class or a str or pathlib.Path 
            containing the full path of where the root folder should be located 
            for file input and output. A 'clerk' must contain all file path and 
            import/export methods for use throughout fiat. Defaults to the 
            default Clerk instance. 
            
        stages (ClassVar[Sequence[Union[str, core.Stage]]]): a list of Stages or 
            strings corresponding to keys in 'core.library'. Defaults to a list 
            of strings listed in the dataclass field.
        data (object): any data object for the project to be applied. If it is 
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.
        identification (str): a unique identification name for a fiat Project. 
            The name is used for creating file folders related to the project. 
            If it is None, a str will be created from 'name' and the date and 
            time. Defaults to None.   
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
    
    Attributes:
        library (ClassVar[nodes.Library]): a class attribute containing a 
            dot-accessible dictionary of base classes. Each base class has 
            'subclasses' and 'instances' class attributes which contain catalogs
            of subclasses and instances of those library classes. This 
            attribute is inherited from Keystone. Changing this attribute will 
            entirely replace the existing links between this instance and all 
            other base classes.
        workflow (core.Stage): a workflow of a project derived from 'outline'. 
            Defaults to None.
        summary (core.Stage): a summary of a project execution derived from 
            'workflow'. Defaults to None.
            
    """
    name: str = None
    settings: SettingsSources = None
    clerk: ClerkSources = None
    director: fiat.Director = None
    workflow: fiat.Workflow = None
    data: object = None
    identification: str = None
    automatic: bool = True
    _validations: MutableSequence[str] = dataclasses.field(
        default_factory = lambda: ['settings'
                                   'identification',
                                   'clerk',
                                   'director',
                                   'workflow',
                                   'data'])
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls validation methods.
        for validation in self._validations:
            getattr(self, f'_validate{validation}')()
        # Sets multiprocessing technique, if necessary.
        self._set_parallelization()
        # Calls 'execute' if 'automatic' is True.
        if self.automatic:
            self.execute()

    """ Public Methods """

    @classmethod
    def create(cls, settings: denovo.configuration.Settings) -> Project:
        """[summary]

        Args:
            settings (denovo.configuration.Settings): [description]

        Returns:
            Project: [description]
            
        """        
        return cls.from_settings(settings = settings, **kwargs)

    @classmethod
    def from_settings(cls, settings: denovo.configuration.Settings) -> Project:
        """[summary]

        Args:
            settings (denovo.configuration.Settings): [description]

        Returns:
            Project: [description]
            
        """        
        return cls(settings = settings)
        
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def execute(self) -> None:
        """Iterates through all stages."""
        for stage in self.director.stages:
            self.advance()
        return self
                     
    """ Private Methods """
    
    def _validate_settings(self) -> None:
        """Validates the 'settings' attribute.
        
        If 'settings' is None, the default 'settings' in 'configuration' is
        used.
        
        """
        if self.settings is None:
            self.settings = denovo.configuration.settings
        elif isinstance(self.settings, (str, pathlib.Path)):
            self.settings = denovo.configuration.bases.settings.create(
                file_path = self.settings)
        elif isinstance(self.settings, dict):
            self.settings = denovo.configuration.bases.settings.create(
                dictionary = self.settings)
        elif not isinstance(self.settings, denovo.configuration.bases.settings):
            raise TypeError('settings must be a Settings, str, pathlib.Path, '
                            'dict, or None type')
        return self      
    
    def _validate_identification(self) -> None:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        """
        if self.identification is None:
            self.identification = (
                denovo.tools.datetime_string(prefix = self.name))
        return self
    
    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'settings'."""
        if (self.settings['fiat']['parallelize'] 
                and not globals()['multiprocessing']):
            import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return self
         
    """ Dunder Methods """

    # def __getattr__(self, attribute: str) -> Any:
    #     """[summary]

    #     Args:
    #         attribute (str): [description]

    #     Raises:
    #         KeyError: [description]

    #     Returns:
    #         Any: [description]
            
    #     """
    #     if attribute in self.director.stages:
    #         getattr(self.director, attribute)
    #     else:
    #         raise KeyError(f'{attribute} is not in {self.name}') 
            
    def __iter__(self) -> Iterable:
        """Returns iterable of a Project's Director instance.
        
        Returns:
            Iterable: of a Project's Director instance.
            
        """
        return iter(self.director)
 
    def __next__(self) -> None:
        """Completes a stage in 'director'."""
        try:
            next(self.director)
        except StopIteration:
            pass
        return self
