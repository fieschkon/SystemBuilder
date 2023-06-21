import inspect
from typing import Any, Callable, List, Tuple, Type
import logging

class Delegate:
    def __init__(self, *types: Type) -> None:
        self.__types: Tuple[Type, ...] = types
        self.__updateSignature__()
        self.subscribers: List[Callable[..., None]] = []

    def connect(self, function: Callable[..., None]) -> None:
        """
        Connect function handle to delegate.

        Args:
            function (Callable[..., None]): The handle for the method to be executed. Must handle *args.
        """
        self.subscribers.append(function)

    def disconnect(self, function: Callable[..., None]) -> None:
        """
        Disconnects function handle from delegate.

        Args:
            function (Callable[..., None]): The handle to be disconnected from the delegate.
        """
        if function in self.subscribers:
            self.subscribers.remove(function)

    def emit(self, *args) -> None:
        for function in self.subscribers:
            function(*args)
    
    def emitFirst(self, *args):
        self.subscribers[0](*args)

    def __updateSignature__(self):
        arg = "function"
        types = self.__types + tuple([None])
        params = [
            inspect.Parameter(
                arg, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=types
            )
        ]
        sig = inspect.Signature(params)
        inspect.signature(self.connect).replace(parameters=params)
        self.connect.__annotations__[arg] = types
        inspect.signature(self.disconnect).replace(parameters=params)
        self.disconnect.__annotations__[arg] = types
