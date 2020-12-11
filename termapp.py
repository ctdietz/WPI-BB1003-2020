from abc import ABC, abstractmethod
import os, sys, platform
from typing import Optional, Union
from collections import namedtuple
import operator as opr
from functools import reduce
import textwrap
from userinput import InputHandlerWin, InputHandlerNix
from styledstring import Styledstring



class Rect:
    def __init__(self, origin: tuple, size: tuple):
        self.origin = origin
        self.size = size

    @property
    def topleft(self) -> tuple:
        return self.origin
    
    @property
    def topright(self) -> tuple:
        return (self.size[0], self.origin[1])

    @property
    def bottomleft(self) -> tuple:
        return (self.origin[0], self.size[1])
    
    @property
    def bottomright(self) -> tuple:
        return self.size

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def offset_origin(self, offset: tuple) -> tuple:
        return (self.origin[0] + offset[0], self.origin[1] + offset[1])


PLATFORM = platform.system()

class Term:
    size = os.get_terminal_size()
    rect = Rect((1, 1), (size.columns, size.lines))
   
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

    def cursor_abs(m: int, n: int) -> None:
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
    
    def __init__(self, rect: Optional[Rect]=None, alt_buff=False, *args, **kwargs):
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
        self.rect = Term.rect if rect is None else rect

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


class CanvasABC(ABC):
    def __init__(self):
        super().__init__()


class Canvas(CanvasABC):
    def __init__(self, rect: Rect, *args, **kwargs):
        """A drawable area on the screen.
        
        In accordance with the ANSI standard, 
        coordinates are of the form n, m (row, column)
        and indexing is 1 based. eg upper left coordinate is (1, 1)
        Args:
            size (tuple): size of element (columns, rows). Defaults to None.
            position (tuple): relative position of the canvas (column int, row: int). \
                              Indexing is 1 based. 
        """

        self.rect = rect
        
        self.elements = []

        self._empty_content = [' '*self.rect.width for _ in range(self.rect.height)]

    def add_element(self, element):
        element.rect = self.rect
        self.elements.append(element)

    def add_elements(self, *elements: list):
        for elem in elements:
            self.add_element(elem)

    def clear(self):
        self._empty_content = [' '*self.rect.width for _ in range(self.rect.height)]

    def refresh(self):
        Term.cursor_abs(*self.rect.origin)
        for i, line in enumerate(self._empty_content):
            Term.cursor_abs(*self.rect.offset_origin((0, i)))
            Term.print(line)
        for elem in self.elements:
            elem.draw()

    def print_at(self, text, position=None, wrap=False):
        #TODO: implement checkbounds to see if it overflows
        position = self.rect.origin if position is None else position
        if wrap:
            text = textwrap.wrap(text, self.rect.width - position[0] + 2)
            for i, line in enumerate(text, start=position[1]+1):
                Term.cursor_abs(position[0], i)
                Term.print(line)
        else:
            Term.cursor_abs(position[0], position[1])
            Term.print(text)

    def make_copy(self):
        newcopy = Canvas(rect=self.rect)
        return newcopy


class ElementABC(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    @abstractmethod
    def draw(self):...



class Text(ElementABC):
    def __init__(self, value, alignment='left', vposition: int=1, *args, **kwargs):
        super().__init__(rect=Term.rect, *args, **kwargs)
        self.value = list(value)
        self.alignment = alignment
        self.vposition = vposition

    def draw(self):
        if self.alignment == 'left':
            self.draw_left(self.value, self.vposition)
        elif self.alignment == 'center':
            self.draw_centered(self.value, self.vposition)

    def draw_left(self, value, vposition):
        hstart = 0
        for val in value:
            self.print_at(val, (self.rect.origin[0]+hstart, vposition))
            hstart += val.__len__()

    def draw_centered(self, value, vposition):
        total_len = reduce(opr.add, map(len, value))

        hstart = self.rect.width//2 - total_len//2
        for val in value:
            self.print_at(val, (hstart, vposition))
            hstart += val.__len__()

    def update_value(self, value):
        self.value = list(value)
        self.draw()


class MultilineText(Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def draw(self):
        for i in range(len(self.value)):
            vpos = self.vposition + i
            if self.alignment == 'left':
                self.draw_left(self.value[i], vpos)
            elif self.alignment == 'center':
                self.draw_centered(self.value[i], vpos)


class CommandPrompt(Canvas):
    def __init__(self, rect: Rect, leader: str='>', *args, **kwargs):
        
        # size = (size, 1) if isinstance(size, int) else size
        super().__init__(rect, *args, **kwargs)
        
        self._empty_content = ['>' + ' '*(self.rect.width-1)]
        self.leader = leader
        self.minlen = len(leader) + 1
        self.maxlen = self.rect.width - 3

    def clear(self) -> None:
        self._empty_content = ['>' + ' '*(self.rect.width-1)]

    def refresh(self, capture_cursor=True):
        super().refresh()
        if capture_cursor:
            Term.cursor_abs(*self.rect.offset_origin((2, 0)))


class _TermAppBase(Canvas):
    def __init__(self, name, alt_buff=False, *args, **kwargs):
        super().__init__(rect=Term.rect, *args, **kwargs)
        self.name = name
        self._uses_alt_buff = alt_buff

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
        
        self._border_top = f'┌╴{self.name}╶' + '─'*(self.rect.width - len(name) - 4) + '┐'
        self._border_mid = '├' + '─'*(self.rect.width - 2) + '┤'
        self._border_bot = '└' + '─'*(self.rect.width - 2) + '┘'

        self.draw_border()
        
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
    
    def draw_border(self):
        Term.cursor_abs(1, 1)
        Term.print(self._border_top)

        Term.cursor_abs(1, self.rect.height - 2)
        Term.print(self._border_mid)

        Term.cursor_abs(1, self.rect.height)
        Term.print(self._border_bot)

        for r in range(2, self.rect.height - 2):
            Term.cursor_abs(1, r)
            Term.print('│')
            Term.cursor_abs(self.rect.width, r)
            Term.print('│')

        Term.cursor_abs(1, self.rect.height - 1)
        Term.print('│')
        Term.cursor_abs(self.rect.width, self.rect.height - 1)
        Term.print('│')


class TermApp(_TermAppBase):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

        self.views = {}

        _temp_rect = Rect((2, 2), (self.rect.width-2, self.rect.height-4))
        _template = Canvas(_temp_rect)
        self.views['_template'] = _template
        self.views['default'] = _template.make_copy()

        _cmdline_rect = Rect((2, self.rect.height-1), ((self.rect.width - 2, 1)))
        self.cmdline = CommandPrompt(_cmdline_rect)

        self.content = self.views['default']

    def new_view(self, name: str, makedefault=False):
        self.views[name] = self.views['_template'].make_copy()
        if makedefault:
            self.views['default'] = self.views[name]
            self.change_view('default')
        return self.views[name]

    def change_view(self, name: str):
        if name in self.views:
            self.content = self.views[name]

    def run(self, **inputfuncs):
        self.startup()
        self.content.refresh()
        self.cmdline.refresh()
        while True:
            rawinput = self._inputhandler.getinput(echo=True)
            if rawinput == 'key_ESCAPE':
                self.shutdown()
            elif rawinput == 'key_BACKSPACE':
                Term.print(' ')
                Term.cursor_back()
            elif rawinput is not None:
                if rawinput in inputfuncs.keys():  
                    inputfuncs[rawinput]()  # out of all the spaghet... it'll be fine
                else:
                    try:
                        inputfuncs['default'](rawinput)  # see...
                    except KeyError:
                        pass
                    self.content.refresh()
                    self.content.print_at(rawinput)
                self.cmdline.refresh()
        

if __name__ == "__main__":
    from styledstring import Styledstring
    testapp = TermApp(name="App Test", alt_buff=False)
    startscreen = testapp.new_view(name="startscreen", makedefault=True)
    title_text = Styledstring('TITLE TEXT', fg='red', attrs=['bold', 'underline'])
    title = Text(title_text, alignment='center', vposition=5)
    startscreen.add_element(title)
    testapp.run()