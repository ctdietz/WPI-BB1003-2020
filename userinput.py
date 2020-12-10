from typing import Any, List, Callable, Union, Optional
from abc import ABC, abstractmethod
import sys
import msvcrt

class Command:
    __slots__ = ['name', 'actions']
    def __init__(self, name: str, actions: Union[Callable, List[Callable]]):
        self.name = name
        self.actions = list(actions)

    def __hash__(self):
        return hash(self.name)


class Parser:
    def __init__(self, args: Optional[Union[Command, List[Command]]]=None):
        args = list(args)
        self.args = set(args)

    def addarg(self, arg: Command):
        self.args.add(arg)

    def parse(self, string) -> Any:
        pass


class Key:
    def __init__(self):
        """
        will eventually be a hashable representation of a keyboard key
        """
        pass


class InputHandler(ABC):
    def __init__(self, functions={}):
        super().__init__()
        self._buffer = ""
        self.functions = functions
        self.setup()

    def add_function(self, token: str, function: Union[Callable, List[Callable]]):
        """[summary]

        Args:
            token (str): [description]
            function (Union[Callable, List[Callable]]): a function or list of functions
                                                        to execute when the token is found
        """
        self.functions[token] = function

    def handle_arrowkeys(self, key):
        """
        Will eventually handle arrow keys. 
        for now just catches them
        """
        return key

    @abstractmethod
    def getinput(self):
        ...
    
    @abstractmethod
    def get_char(self) -> str:...

    @abstractmethod
    def get_char_echo(self) -> str:
        """
        get a char from input buffer,
        echo it back to output if it's printable
        """
        ...

    @abstractmethod
    def setup(self):
        """
        Perform any OS specific startup routines
        """
        ...

    @abstractmethod
    def shutdown(self):
        """
        Perform any OS specific shutdown routines
        """
        ...


class InputHandlerWin(InputHandler):
    arrowkey = {
        'P': 'key_DOWN',
        'H': 'key_UP',
        'K': 'key_LEFT',
        'M': 'key_RIGHT'
    }
    def __init__(self):
        super().__init__()

    def getinput(self, echo=True):
        if msvcrt.kbhit():
            if echo:
                char = self.get_char_echo()
            else:
                char = self.get_char()
            
            if char == chr(224):  # Arrow key leader. need to read again
                key = self.get_char()
                return self.handle_arrowkeys(InputHandlerWin.arrowkey[key])
            elif char == chr(13):  # Enter Key
                output = self._buffer
                self._buffer = ''
                return output
            elif char == chr(27):  # Escape
                return 'key_ESCAPE'
            elif char ==  chr(8):  # Backspace
                self._buffer = self._buffer[:-1]
                return 'key_BACKSPACE'  
            else:
                self._buffer += char
        

    def get_char(self):
        return msvcrt.getwch()

    def get_char_echo(self):
        return msvcrt.getwche()

    def setup(self):
        pass

    def shutdown(self):
        pass


class InputHandlerNix(InputHandler):
    def __init__(self):
        import tty
        super().__init__()

    def get_char(self) -> str:
        return ...
