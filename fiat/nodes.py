"""
nodes: project workflow nodes and related classes
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
import inspect
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo
import more_itertools




@dataclasses.dataclass
class Registry(amicus.base.Catalog):
    """A Catalog of Component subclasses or subclass instances."""

    """ Properties """
    
    @property
    def suffixes(self) -> tuple[str]:
        """Returns all stored names and naive plurals of those names.
        
        Returns:
            tuple[str]: all names with an 's' added in order to create simple 
                plurals combined with the stored keys.
                
        """
        plurals = [key + 's' for key in self.contents.keys()]
        return tuple(list(self.contents.keys()) + plurals)


@dataclasses.dataclass
class Library(object):
    
    subclasses: Registry = Registry()
    instances: Registry = Registry()

    """ Properties """
    
    @property
    def laborers(self) -> Tuple[str]:
        kind = configuration.bases.laborer
        instances = [
            k for k, v in self.instances.items() if isinstance(v, kind)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, kind)]
        return tuple(instances + subclasses)   
        
    @property
    def manager(self) -> Tuple[str]:
        kind = configuration.bases.manager
        instances = [
            k for k, v in self.instances.items() if isinstance(v, kind)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, kind)]
        return tuple(instances + subclasses)   
     
    @property
    def tasks(self) -> Tuple[str]:
        kind = configuration.bases.task
        instances = [
            k for k, v in self.instances.items() if isinstance(v, kind)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, kind)]
        return tuple(instances + subclasses)

    @property
    def workers(self) -> Tuple[str]:
        kind = configuration.bases.worker
        instances = [
            k for k, v in self.instances.items() if isinstance(v, kind)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, kind)]
        return tuple(instances + subclasses)

    """ Public Methods """
    
    def classify(self, component: str) -> str:
        """[summary]

        Args:
            component (str): [description]

        Returns:
            str: [description]
            
        """        
        if component in self.laborers:
            return 'laborer'
        elif component in self.managers:
            return 'manager'
        elif component in self.tasks:
            return 'task'
        elif component in self.workers:
            return 'worker'
        else:
            raise TypeError(f'{component} is not a recognized type')

    def instance(self, name: Union[str, Sequence[str]], **kwargs) -> Component:
        """Returns instance of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'instances' catalog over 'subclasses' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            Component: [description]
            
        """
        names = amicus.tools.listify(name)
        primary = names[0]
        item = None
        for key in names:
            for catalog in ['instances', 'subclasses']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {name} was found') 
        elif inspect.isclass(item):
            instance = item(name = primary, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)  
        return instance 

    def parameterify(self, name: Union[str, Sequence[str]]) -> List[str]:
        """[summary]

        Args:
            name (Union[str, Sequence[str]]): [description]

        Returns:
            List[str]: [description]
            
        """        
        component = self.select(name = name)
        return list(component.__annotations__.keys())
       
    def register(self, component: Union[Component, Type[Component]]) -> None:
        """[summary]

        Args:
            component (Union[Component, Type[Component]]): [description]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        if isinstance(component, Component):
            instances_key = self._get_instances_key(component = component)
            self.instances[instances_key] = component
            subclasses_key = self._get_subclasses_key(component = component)
            if subclasses_key not in self.subclasses:
                self.subclasses[subclasses_key] = component.__class__
        elif inspect.isclass(component) and issubclass(component, Component):
            subclasses_key = self._get_subclasses_key(component = component)
            self.subclasses[subclasses_key] = component
        else:
            raise TypeError(
                f'component must be a Component subclass or instance')
        return self
    
    def select(self, name: Union[str, Sequence[str]]) -> Component:
        """Returns subclass of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'subclasses' catalog over 'instances' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            Component: [description]
            
        """
        names = amicus.tools.listify(name)
        item = None
        for key in names:
            for catalog in ['subclasses', 'instances']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {name} was found') 
        elif inspect.isclass(item):
            component = item
        else:
            component = item.__class__  
        return component 
    
    """ Private Methods """
    
    def _get_instances_key(self, 
        component: Union[Component, Type[Component]]) -> str:
        """Returns a snakecase key of the class name.
        
        Returns:
            str: the snakecase name of the class.
            
        """
        try:
            key = component.name 
        except AttributeError:
            try:
                key = amicus.tools.snakify(component.__name__) 
            except AttributeError:
                key = amicus.tools.snakify(component.__class__.__name__)
        return key
    
    def _get_subclasses_key(self, 
        component: Union[Component, Type[Component]]) -> str:
        """Returns a snakecase key of the class name.
        
        Returns:
            str: the snakecase name of the class.
            
        """
        try:
            key = amicus.tools.snakify(component.__name__) 
        except AttributeError:
            key = amicus.tools.snakify(component.__class__.__name__)
        return key      

 

@dataclasses.dataclass
class Component(abc.ABC):
    """Base class for nodes in a project workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
            Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
  
    """
    name: str = None
    contents: Any = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    library: ClassVar[Library] = Library()

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library'."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library'.
        if not abc.ABC in cls.__bases__:
            cls.library.register(component = cls)
            
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Adds instance to 'library'.
        self.library.register(component = self)
  
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        pass

    """ Public Methods """
    
    def execute(self, 
        project: amicus.Project, 
        iterations: Union[int, str] = None, 
        **kwargs) -> amicus.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        if iterations is None:
            iterations = self.iterations
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if isinstance(self.parameters, Parameters):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if iterations in ['infinite']:
                while True:
                    project = self.implement(project = project, **parameters)
            else:
                for _ in range(iterations):
                    project = self.implement(project = project, **parameters)
        return project

    """ Dunder Methods """
    
    def __call__(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'execute' method if an instance is called.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        return self.execute(project = project, **kwargs)


@dataclasses.dataclass
class Task(denovo.structures.Node):
    """Node type for fiat Workflows.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout fiat. For example, if a fiat 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. 
            Defaults to None. 
        step (Union[str, Callable]):
        

    """
    name: str = None
    step: Union[str, Callable] = None
    technique: Callable = None
      
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass
  
    """ Public Methods """
    
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        project = self.contents.execute(project = project, **kwargs)
        return project    


@dataclasses.dataclass
class Step(amicus.base.Proxy, Task):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when creating branching, parallel workflows which test a variety of 
    strategies with similar or identical parameters and/or methods.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (Technique): stored Technique instance to be used by the 
            'implement' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                                                 
    """
    name: str = None
    contents: Technique = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
                    
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def organize(self, technique: Technique) -> Technique:
        """[summary]

        Args:
            technique (Technique): [description]

        Returns:
            Technique: [description]
            
        """
        if self.parameters:
            new_parameters = self.parameters
            new_parameters.update(technique.parameters)
            technique.parameters = new_parameters
        return technique
        
                                                  
@dataclasses.dataclass
class Technique(Task):
    """Keystone class for primitive objects in an amicus composite object.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (Callable): stored Callable algorithm to be used by the 
            'implement' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                                                 
    """
    name: str = None
    contents: Callable = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    step: str = None
        
    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self

    """ Public Methods """

    def execute(self, 
        project: amicus.Project, 
        iterations: Union[int, str] = None, 
        **kwargs) -> amicus.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        if self.step is not None:
            step = self.library.instance(name = self.step)
            self = step.organize(technique = self)
        return super().execute(
            project = project, 
            iterations = iterations, 
            **kwargs)

