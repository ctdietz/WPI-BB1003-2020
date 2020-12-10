import os, sys, platform
from typing import Optional, Union
from collections import namedtuple
from operator import add

from userinput import InputHandlerWin, InputHandlerNix


class Term:
    Size = namedtuple("Size", ["columns", "lines"])
    
    def __init__(self, size: Optional[tuple]=None, alt_buff=True, *args, **kwargs):
        """An interface for ANSI terminals. 
        
        In accordance with the ANSI standard,
        coordinates are of the form n, m (row, column)
        and indexing is 1 based. eg upper left coordinate is (1, 1)

        Args:
            size (Optional[tuple], optional): size of element (columns, rows). Defaults to None.
            alt_buff (bool, optional): Request the terminal to switch to the alternate buffer. Defaults to True.

        Raises:
            NotImplementedError: If the current platform is not supported.
        """
        self._platform = platform.system()

        # map the correct system dependent callable to send alias
        # NOTE: May not be necessary, but better now than later 
        if self._platform == 'Windows':
            self.send = self.send_win
        elif self._platform == 'Linux':   # TODO: add distinct OSX and Linux send methods
            self.send = self.send_nix
        elif self._platform == 'Darwin':  # aka MacOS
            self.send = self.send_nix
        else: 
            raise NotImplementedError(f"Platform '{self._platform}' is not yet supported")

        self._uses_alt_buff = alt_buff
        self.size = os.get_terminal_size() if size is None else Term.Size(columns=size[0], lines=size[1])

    def _make_esc(self, code: str) -> str:
        escape_sequence = "\u001b[" + code
        return escape_sequence

    def send_win(self, text: str) -> None:
        print(text, sep='', end='', flush=True)

    def send_nix(self, text: str) -> None:
        print(text, sep='', end='', flush=True)

    def startup(self):
        """ Sends the esc_seq to swap to the terminal alt buffer"""
        #TODO: this doesn't seem to work properly
        if self._uses_alt_buff:
            self.send(self._make_esc("?1049h"))

    def shutdown(self):
        """ Sends the esc_seq to swap to the terminal main buffer, and quits"""
        #TODO: this doesn't seem to work properly
        if self._uses_alt_buff:
            self.send(self._make_esc("?1049l"))
        quit()

    # def run(self):
    #     self.startup()
    #     while True:
    #         char = sys.stdin.read(1)
    #         if ord(char) == 3:  # CTRL-C
    #             break
    #         else:
    #             self.handle_input(char)
    #     self.shutdown()

    def handle_input(self, char):
        pass

    def cursor_abs(self, n: int, m: int) -> None:
        '''Absolute Cursor Position Control Sequence
        Moves the cursor to row n, column m
        Values are 1 based eg. first column is column 1
        '''
        self.send(self._make_esc(f"{n};{m}H"))

    def cursor_up(self, n: int=1) -> None:
        '''Move cursor up n lines
        '''
        self.send(self._make_esc(f"{n}A"))
    
    def cursor_down(self, n: int=1) -> None:
        '''Move cursor down n lines
        '''
        self.send(self._make_esc(f"{n}B"))
    
    def cursor_forward(self, n: int=1) -> None:
        '''Move cursor forward n lines
        '''
        self.send(self._make_esc(f"{n}C"))
    
    def cursor_back(self, n: int=1) -> None:
        '''Move cursor back n lines
        '''
        self.send(self._make_esc(f"{n}D"))


class Canvas(Term):
    Position = namedtuple("Position", ["column", "line"])
    def __init__(self, size: tuple, position: tuple, *args, **kwargs):
        """A drawable area on the screen.
        
        In accordance with the ANSI standard, 
        coordinates are of the form n, m (row, column)
        and indexing is 1 based. eg upper left coordinate is (1, 1)

        Args:
            size (tuple): size of canvas (row: int, column: int)
            position (tuple): relative position of the canvas (row: int, column: int). \
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
                cln = blankchars.join([cln[:start(0)], cln[start(1)+size[1]:]])
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

    def remove_child(self, child, ignoresubchilds=False) -> None:
        raise NotImplementedError
        if isinstance(child, Term):
            if child in self.children:
                pass
        else:
            raise TypeError("child must be of type Term or instance of subclass of Term")
    
    def redraw(self, position=None) -> None:
        position = (self.position.column, self.position.line) if position is None else position
        self.cursor_abs(position[1], position[0])
        for i, line in enumerate(self.content):
            self.cursor_abs(position[1] + i, position[0])
            self.send(line)
        for child in self.children:
            position = list(map(add, position, child.position))
            child.redraw(position)

    def print_at(self, text, position=None, checkbounds=True):
        #TODO: implement checkbounds to see if it overflows
        position = (self.position.column, self.position.line) if position is None else position
        self.cursor_abs(position[1], position[0])
        self.send(text)


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
            self.cursor_abs(self.position[1], self.position[0]+2)

    def redraw(self, to_start=True):
        super().redraw()
        if to_start:
            self.cursor_abs(self.position[1], self.position[0]+2)



class AppBase(Term):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        
        self._border_top = f'┌╴{self.name}╶' + '─'*(self.size.columns - len(name) - 4) + '┐'
        self._border_mid = '├' + '─'*(self.size.columns - 2) + '┤'
        self._border_bot = '└' + '─'*(self.size.columns - 2) + '┘'

        self.draw_border()
        
    def draw_border(self):
        #TODO: change print calls to send()
        self.cursor_abs(1, 1)
        print(self._border_top, end='', flush=True)
        for r in range(2, self.size.lines - 2):
            self.cursor_abs(r, 1)
            print('│', end='', flush=True)
            self.cursor_abs(r, self.size.columns)
            print('│', end='', flush=True)
        self.cursor_abs(self.size.lines - 2, 1)
        print(self._border_mid, end='', flush=True)
        self.cursor_abs(self.size.lines - 1, 1)
        print('│', end='', flush=True)
        self.cursor_abs(self.size.lines - 1, self.size.columns)
        print('│', end='', flush=True)
        self.cursor_abs(self.size.lines, 1)
        print(self._border_bot, end='', flush=True)


class App(AppBase):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        self.content = Canvas(size=(self.size.columns-2, self.size.lines-4), position=(2, 2))
        self.cmdline = CommandPrompt(size=(self.size.columns - 2, 1), position=(2, self.size.lines - 1))

        # use correct input handler
        # TODO: this should probably go up in Term
        if self._platform == 'Windows':
            self._inputhandler = InputHandlerWin()
        elif self._platform == 'Linux':   # TODO: add distinct OSX and Linux send methods
            self._inputhandler = InputHandlerNix()
        elif self._platform == 'Darwin':  # aka MacOS
            self._inputhandler = InputHandlerNix()
        else: 
            raise NotImplementedError(f"Platform '{self._platform}' is not yet supported")

    def run(self):
        self.startup()
        self.content.clear()
        self.cmdline.clear()
        while True:
            rawinput = self._inputhandler.getinput(echo=True)
            if rawinput == 'key_ESCAPE':
                self.shutdown()
            elif rawinput == 'key_BACKSPACE':
                self.send(' ')
                self.cursor_back()
            elif rawinput is not None:
                self.content.clear()
                self.content.print_at(rawinput)
                self.cmdline.clear()
        

terminal = App(name="App Test", alt_buff=False)
terminal.run()