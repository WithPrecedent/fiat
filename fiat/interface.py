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
import dataclasses
import inspect
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


_sources: Mapping[Type, str] = {(denovo.configuration.Settings,
                                 dict, 
                                 pathlib.Path, 
                                 str): 'settings'}
_validations: MutableSequence[str] = ['settings'
                                      'identification',
                                      'clerk', 
                                      'director',
                                      'workflow',
                                      'data',
                                      'library']


@dataclasses.dataclass
class Project(denovo.quirks.Element, denovo.quirks.Factory):
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
    library: denovo.containers.Library = None
    data: object = None
    identification: str = None
    automatic: bool = True
    sources: ClassVar[Mapping[Type, str]] = _sources
    validations: ClassVar[MutableSequence[str]] = _validations
    
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
        # Calls 'complete' if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """

    @classmethod
    def from_settings(cls, settings: denovo.configuration.Settings) -> Project:
        """[summary]

        Args:
            settings (denovo.configuration.Settings): [description]

        Returns:
            Project: [description]
            
        """
        if isinstance(settings, denovo.configuration.Settings):
            return cls(settings = settings)
        elif (inspect.isclass(settings) 
              and issubclass(settings, denovo.configuration.Settings)):
            return cls(settings = settings())
        else:
            settings = denovo.configuration.Settings.create(source = settings)
            return cls(settings = settings)
        
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
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
                source = self.settings)
        elif isinstance(self.settings, dict):
            self.settings = denovo.configuration.bases.settings.create(
                source = self.settings)
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
