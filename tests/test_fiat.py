"""
test_fiat: executes all fiat tests
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


ToDo:

    
"""
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, MutableMapping, MutableSequence, Optional, 
                    Sequence, Set, Tuple, Type, Union)

import denovo

import fiat


""" Testing Functions """

def test_version() -> None:
    assert fiat.__version__ == '0.1.0'
    return

if __name__ == '__main__':
    test_version()
    folder = pathlib.Path('.')
    testimony = denovo.testing.Testimony(package = fiat, folder = folder)
    testimony.testify()
