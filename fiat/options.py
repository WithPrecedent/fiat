"""
options: classes and functions for storing fiat project settings
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Outline (Lexicon): stores configuration settings after either loading 
        them from disk or by the passed arguments.    
         
"""
from __future__ import annotations
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo
import more_itertools

import fiat

