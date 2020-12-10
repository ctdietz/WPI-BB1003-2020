import os, sys, platform
from typing import Optional, Union
from collections import namedtuple
import operator as opr
from functools import lru_cache
import textwrap

from userinput import InputHandlerWin, InputHandlerNix


PLATFORM = platform.system()

class Term:

    size = os.get_terminal_size()
   
    # different OS's require different low level terminal interfaces
    # NOTE: no low level stuff is happening yet. but it could
    if PLATFORM == 'Windows':
        def print(text: str) -> None:
            print(text, sep='', end='', flush=True)
    elif PLATFORM == 'Linux':
        def print(text: str) -> None:
            print(text, sep='', end='', flush=True)
    elif PLATFORM == 'Darwin':
        def print(text: str) -> None:
            print(text, sep='', end='', flush=True)
    else: 
        raise NotImplementedError(f"Platform '{self._platform}' is not yet supported")

    def precsi(seq: str) -> str:
        """ Prepend the ANSI Control Sequence Indicator
        """
        escape_sequence = "\u001b[" + seq
        return escape_sequence

    def printcsi(seq: str) -> None:
        Term.print(Term.precsi(seq))

    def cursor_abs(n: int, m: int) -> None:
        '''Absolute Cursor Position Control Sequence
        Moves the cursor to row n, column m
        Values are 1 based eg. first column is column 1
        '''
        Term.printcsi(f"{n};{m}H")

    def cursor_up(n: int=1) -> None:
        '''Move cursor up n lines
        '''
        Term.printcsi(f"{n}A")
    
    def cursor_down(n: int=1) -> None:
        '''Move cursor down n lines
        '''
        Term.printcsi(f"{n}B")
    
    def cursor_forward(n: int=1) -> None:
        '''Move cursor forward (right) n lines
        '''
        Term.printcsi(f"{n}C")
    
    def cursor_back(n: int=1) -> None:
        '''Move cursor back (left) n lines
        '''
        Term.printcsi(f"{n}D")

    # @property
    # def size():
    #     return os.get_terminal_size()


class Screen:
    Size = namedtuple("Size", ["columns", "lines"])
    
    def __init__(self, size: Optional[tuple]=None, alt_buff=True, *args, **kwargs):
        """An interface for ANSI terminals. 

        NOTE: This has been changed. 
        coordinates are of the form n, m (row, column)
        and indexing is 1 based. eg upper left coordinate is (1, 1)

        Args:
            size (Optional[tuple], optional): size of element (columns, rows). Defaults to None.
            alt_buff (bool, optional): Request the terminal to switch to the alternate buffer. Defaults to True.

        Raises:
            NotImplementedError: If the current platform is not supported.
        """

        self._uses_alt_buff = alt_buff
        self.size = Term.size if size is None else Screen.Size(columns=size[0], lines=size[1])

    def startup(self):
        """ Sends the esc_seq to swap to the terminal alt buffer"""
        #TODO: this doesn't seem to work properly
        if self._uses_alt_buff:
            Term.printcsi("?1049h")

    def shutdown(self):
        """ Sends the esc_seq to swap to the terminal main buffer, and quits"""
        #TODO: this doesn't seem to work properly
        if self._uses_alt_buff:
            Term.printcsi("?1049l")
        quit()
    
    def handle_input(self, char):
        pass


class Canvas(Screen):
    Position = namedtuple("Position", ["column", "line"])
    def __init__(self, size: tuple, position: tuple, *args, **kwargs):
        """A drawable area on the screen.
        
        In accordance with the ANSI standard, 
        coordinates are of the form n, m (row, column)
        and indexing is 1 based. eg upper left coordinate is (1, 1)

        Args:
            size (tuple): size of element (columns, rows). Defaults to None.
            position (tuple): relative position of the canvas (column int, row: int). \
                              Indexing is 1 based. 
        """
        super().__init__(size=size, *args, **kwargs)
        
        self.position = Canvas.Position(column=position[0], line=position[1])
        self.children = []

        self.content = [' '*self.size.columns for _ in range(self.size.lines)]

    def clear(self, start: Optional[tuple]=None, size: Optional[tuple]=None, redraw=True) -> None:
        if start is not None:
            if size is None:
                size = (self.size.columns - start[0], self.size.lines - start[1])
            
            blankchars = ' '*(size[0])
            for line in range(size[1]):
                cln = self.content[line]
                cln = blankchars.join([cln[:start[0]], cln[start[1]+size[1]:]])
                self.content[line] = cln
        else:
            self.content = [' '*self.size.columns for _ in range(self.size.lines)]
        if redraw:
            self.redraw()

    def add_child(self, child) -> None:
        if isinstance(child, Term):
            #TODO: check if child is already in children
            #       and if child is alrady in children of children
            self.children.append()
        else:
            raise TypeError("child must be of type Term or instance of subclass of Term")

    def rm_child(self, child, ignoresubchilds=False) -> None:
        raise NotImplementedError
        if isinstance(child, Screen):
            if child in self.children:
                pass
        else:
            raise TypeError("child must be of type Term or instance of subclass of Term")
    
    def redraw(self, position=None) -> None:
        position = (self.position.column, self.position.line) if position is None else position
        Term.cursor_abs(position[1], position[0])
        for i, line in enumerate(self.content):
            Term.cursor_abs(position[1] + i, position[0])
            Term.print(line)
        for child in self.children:
            position = list(map(opr.add, position, child.position))
            child.redraw(position)

    def print_at(self, text, position=None, wrap=True):
        #TODO: implement checkbounds to see if it overflows
        position = (self.position.column, self.position.line) if position is None else position
        if wrap:
            text = textwrap.wrap(text, self.size.columns - position[0] + 2)
            for i, line in enumerate(text, start=position[1]):
                Term.cursor_abs(i, position[0])
                Term.print(line)
        else:
            Term.cursor_abs(position[1], position[0])
            Term.print(text)


class CommandPrompt(Canvas):
    def __init__(self, size: tuple, position: tuple, leader: str='>', *args, **kwargs):
        
        # size = (size, 1) if isinstance(size, int) else size
        super().__init__(size, position, *args, **kwargs)
        
        self.content = ['>' + ' '*(self.size.columns-1)]
        self.leader = leader
        self.minlen = len(leader) + 1
        self.maxlen = self.size.columns - 3

    def clear(self, redraw=True, resetcursor=True) -> None:
        self.content = ['>' + ' '*(self.size.columns-1)]
        if redraw:
            self.redraw()
        if resetcursor:
            Term.cursor_abs(self.position[1], self.position[0]+2)

    def redraw(self, to_start=True):
        super().redraw()
        if to_start:
            Term.cursor_abs(self.position[1], self.position[0]+2)



class AppBase(Screen):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        
        self._border_top = f'┌╴{self.name}╶' + '─'*(self.size.columns - len(name) - 4) + '┐'
        self._border_mid = '├' + '─'*(self.size.columns - 2) + '┤'
        self._border_bot = '└' + '─'*(self.size.columns - 2) + '┘'

        self.draw_border()
        
    def draw_border(self):
        Term.cursor_abs(1, 1)
        Term.print(self._border_top)

        Term.cursor_abs(self.size.lines - 2, 1)
        Term.print(self._border_mid)

        Term.cursor_abs(self.size.lines, 1)
        Term.print(self._border_bot)

        Term.cursor_abs(self.size.lines - 1, 1)
        for r in range(2, self.size.lines - 2):
            Term.cursor_abs(r, 1)
            Term.print('│')
            Term.cursor_abs(r, self.size.columns)
            Term.print('│')

        Term.cursor_abs(self.size.lines - 1, 1)
        Term.print('│')
        Term.cursor_abs(self.size.lines - 1, self.size.columns)
        Term.print('│')


class Layout(Canvas):
    def __init__(self, size: tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)


class App(AppBase):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        self.content = Canvas(size=(self.size.columns-2, self.size.lines-4), position=(2, 2))
        self.cmdline = CommandPrompt(size=(self.size.columns - 2, 1), position=(2, self.size.lines - 1))

        # use correct input handler
        # TODO: this should probably go up in Term
        if PLATFORM == 'Windows':
            self._inputhandler = InputHandlerWin()
        elif PLATFORM == 'Linux':   # TODO: add distinct OSX and Linux send methods
            self._inputhandler = InputHandlerNix()
        elif PLATFORM == 'Darwin':  # aka MacOS
            self._inputhandler = InputHandlerNix()
        else: 
            raise NotImplementedError(f"Platform '{PLATFORM}' is not yet supported")

    def run(self):
        self.startup()
        self.content.clear()
        self.cmdline.clear()
        while True:
            rawinput = self._inputhandler.getinput(echo=True)
            if rawinput == 'key_ESCAPE':
                self.shutdown()
            elif rawinput == 'key_BACKSPACE':
                Term.print(' ')
                Term.cursor_back()
            elif rawinput is not None:
                self.content.clear()
                self.content.print_at(rawinput)
                self.cmdline.clear()
        

terminal = App(name="App Test", alt_buff=False)
terminal.run()