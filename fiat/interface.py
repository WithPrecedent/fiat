"""
interface: primary access point and interface for a fiat project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project

"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)
import warnings

import denovo

import fiat


@dataclasses.dataclass
class Project(denovo.quirks.Element, denovo.quirks.Factory):
    """Interface for a fiat project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout fiat. For example, if a fiat 
            instance needs outline from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        outline (OutlineSources): an Outline-compatible subclass or instance, 
            a str or pathlib.Path containing the file path where a file of a 
            supported file type with outline for an Outline instance is 
            located, or a 2-level mapping containing outline. Defaults to the 
            default Outline instance.
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
        library (ClassVar[nodes.Library]): a class attribute containing a 
            dot-accessible dictionary of base classes. Each base class has 
            'subclasses' and 'instances' class attributes which contain catalogs
            of subclasses and instances of those library classes. This 
            attribute is inherited from Keystone. Changing this attribute will 
            entirely replace the existing links between this instance and all 
            other base classes.
            
    """
    name: str = None
    settings: fiat.shared.bases.settings = None
    clerk: fiat.shared.bases.clerk = None
    director: fiat.shared.bases.director = None
    stages: Sequence[Union[str, fiat.shared.bases.stage]] = dataclasses.field(
        default_factory = lambda: ['settings', 'outline', 'workflow', 'report'])
    library: fiat.shared.bases.library = None
    data: object = None
    identification: str = None
    automatic: bool = True
    sources: ClassVar[Mapping[Type, str]] = {(fiat.shared.bases.settings,
                                              dict, 
                                              pathlib.Path, 
                                              str): 'settings'}
    validations: ClassVar[MutableSequence[str]] = ['outline'
                                                   'identification',
                                                   'clerk',
                                                   'stages',
                                                   'director',
                                                   'library',
                                                   'workflow']
    
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
            try:
                getattr(self, f'_validate{validation}')()
            except AttributeError:
                pass
        # Sets multiprocessing technique, if necessary.
        self._set_parallelization()
        # Calls 'complete' if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """

    @classmethod
    def from_settings(cls, 
                      settings: fiat.shared.SettingsSources, 
                      **kwargs) -> Project:
        """[summary]

        Args:
            settings (SettingsSources): [description]

        Returns:
            Project: [description]
            
        """        
        
        if isinstance(settings, fiat.shared.bases.settings):
            outline = fiat.shared.bases.outline.create(source = settings)
        elif (inspect.isclass(settings) 
              and issubclass(settings, fiat.shared.bases.settings)):
            outline = fiat.shared.bases.outline.create(source = settings())
        else:
            settings = fiat.shared.bases.settings.create(source = settings)
            outline = fiat.shared.bases.outline.create(source = settings)
        return cls(outline = outline, **kwargs)
        
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
    
    def _store_shared_settings(self) -> None:
        """[summary]

        Returns:
            [type]: [description]
            
        """
        attributes = dir(fiat.shared)
        constants = [a.is_upper() for a in attributes]
        relevant = ['general', 'denovo', 'fiat', self.name]
        sections = {k: v for k, v in self.settings.items() if k in relevant}
        constant_keys = [k for k in sections.keys() if k.upper() in constants]
        for key in constant_keys:
            setattr(fiat.shared, key.upper(), sections[key])
        return self
                  
    def _validate_outline(self) -> None:
        """Validates the 'outline' attribute.
        
        If 'outline' is None, the default 'outline' in 'configuration' is
        used.
        
        """
        if self.outline is None:
            self.outline = fiat.shared.bases.outline()
        elif isinstance(self.outline, (str, pathlib.Path, dict)):
            self.outline = fiat.create(source = self.outline)
        elif isinstance(self.outline, fiat.shared.bases.settings):
            if not isinstance(self.outline, fiat.shared.bases.outline):
                self.outline = fiat.shared.bases.outline.create(
                    source = self.outline.contents)
        else:
            raise TypeError('outline must be a Settings, str, pathlib.Path, '
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
        elif not isinstance(self.identification, str):
            raise TypeError('identification must be a str or None type')
        return self
    
    def _validate_clerk(self) -> None:
        """Creates or validates 'clerk'."""
        if isinstance(self.clerk, (str, pathlib.Path, type(None))):
            self.clerk = fiat.shared.bases.clerk(settings = self.outline)
        elif isinstance(self.clerk, fiat.shared.bases.clerk):
            self.clerk.settings = self.outline
            self.clerk._add_settings()
        else:
            raise TypeError('clerk must be a Clerk, str, pathlib.Path, or None '
                            'type')
        return self

    def _validate_director(self) -> None:
        """Creates or validates 'director'."""
        if self.director is None:
            self.director = fiat.shared.bases.director(project = self)
        elif not isinstance(self.director, fiat.shared.bases.director):
            raise TypeError('director must be a Director or None type')
        return self
    
    def _validate_workflow(self) -> None:
        """Creates or validates 'library'."""
        if self.workflow is None:
            self.workflow = fiat.shared.bases.workflow(project = self)
        elif not isinstance(self.workflow, fiat.shared.bases.workflow):
            raise TypeError('workflow must be a Workflow or None type')
        return self

    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'outline'."""
        if fiat.shared.PARALLELIZE and not globals()['multiprocessing']:
            import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return self
         
    """ Dunder Methods """
      
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
