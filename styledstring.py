""" A set of functions for pretty printing and displaying output
"""
from __future__ import annotations
from typing import overload, Type, List, Optional, Union
from abc import ABC, abstractmethod


def _esc_seq(seq: str) -> str:
    leader = "\u001b["
    seq = leader + seq
    return seq

def _sgr_seq(*params: str) -> str:
    # params = list(params)
    seq = _esc_seq(";".join(params) + "m")
    # print(seq)
    return seq

_COLORS = {
    "black": '0',
    "red": '1',
    "green": '2',
    "yellow": '3',
    "blue": '4',
    "magenta": '5',
    "cyan": '6',
    "white": '7',
    'default': '9'
}

_ATTRS = {
    "bold": '1',
    "faint": '2',
    "italic": '3',
    "underline": '4',
    "blink": '5',
    "strike": '9'
}

_RESET_SEQ = _sgr_seq("39", "49", "0")


# class _PostfixedABC(ABC):
#     @abstractmethod
#     def copy_onto(self, value: object) -> ...:
#         """
#         Must return 
#         """
#         return type(self)(value=value, prefix=self._prefix, suffix=self._suffix)
#         # return _Postfixed(body=value, prefix=self._prefix, suffix=self._suffix)


class _Postfixed(ABC):
    """ 
    "Postfix" is used to mean a 'fix' or 'fixes', as in the root of prefix and suffix,
    that i/are always applied after a opperation is performed on the object's value.
    The term 'fixative' from biology or various art disciplines could also be used. 
    """
    def __init__(self, value: object=""):
        #TODO: can this be made to work for any object type? 
        #      including for prefix and suffix?
        self._value = str(value)

    def __str__(self):
        return self._wrap(self._value)

    __repr__ = __str__

    def _wrap(self, body):
        return self.prefix + body + self.suffix

    @overload
    def __getitem__(self, i: int) -> _Postfixed: ...
    @overload
    def __getitem__(self, s: slice) -> _Postfixed: ...
    def __getitem__(self, value) -> _Postfixed:
        substring = self._value.__getitem__(value)
        return self.copy_onto(substring)

    def split(self, sep: Optional[str]=None, maxsplit: int=-1) -> List[_Postfixed]:
        #TODO: return instance of subclass
        splits = [self.copy_onto(s) for s in self._value.split(sep, maxsplit)]
        return splits

    def __len__(self):
        return len(self._value)

    @abstractmethod
    def copy_onto(self, value: object) -> _Postfixed:
        """
        Must return a new instance of the same class, accept only a new value,
        and provide all other necessary attributes from the instance.
        """
        return _Postfixed(value=value, prefix=self.prefix, suffix=self.suffix)

    @property
    @abstractmethod
    def prefix(self, prefix) -> None:
        """
        Must return the object to be applied 
        as the prefix through concatenation
        """
        return prefix

    @property
    @abstractmethod
    def suffix(self, suffix) -> None:
        """
        Must return the object to be applied 
        as the suffix through concatenation
        """
        return suffix


class Styledstring(_Postfixed):
    def __init__(self, string="", fg=None, bg=None, attrs: Union[list, tuple, None]=None, *args, **kwargs):
        self.attrs = attrs
        self._fg = fg
        self._bg = bg
        self._st = attrs
        super().__init__(string)

    def copy_onto(self, value):
        return Styledstring(value, self._fg, self._bg, self._st)

    @property
    def prefix(self):
        styles = []
        if self._fg is not None:
            styles.append('3' + _COLORS[self._fg])
        if self._bg is not None:
            styles.append('4' + _COLORS[self._bg])
        if self._st is not None:
            if isinstance(self._st, str):
                styles.append(_ATTRS[self._st])
            else:
                styles.extend([_ATTRS[s] for s in self._st])
                
        return _sgr_seq(*styles)

    @property
    def suffix(self):
        return _RESET_SEQ

    def foreground(self, color=None):
        if color is not None:
            self._fg = color

    def background(self, color=None):
        if color is not None:
            self._bg = color

    def style(string, attrs: Optional[list]=None) -> Styledstring:
        if not isinstance(string, Styledstring):
            string = Styledstring(string, attrs=attrs)
        string._st = style
        return string

    def color(string, fg=None, bg=None) -> Styledstring:
        if not isinstance(string, Styledstring):
            string = Styledstring(string, fg=foreground, bg=background)
        string.foreground(fg)
        string.background(bg)
        return string







styled = Styledstring("Styledstring", fg='red')
print(styled[3:6])


# styled = Styledstring("styled test")

'''
# Stylish, Styledstringing
class Styledstring(str):
    """ Behaves like a normal str, with added styling
    """    
    def __new__(cls, string, *args, **kwargs):
        """ Return a string instance """
        return str.__new__(cls, string)

    def __init__(self, string, fg_color=None, bg_color=None, attrs: Optional[list]=None):
        self._fg = fg_color
        self._bg = bg_color
        self._st = attrs

        self.styled = None
        self._update_Postfixed()

    def _update_Postfixed(self):
        styles = []
        if self._fg is not None:
            styles.append('3' + _COLORS[self._fg])
        if self._bg is not None:
            styles.append('4' + _COLORS[self._bg])
        if self._st is not None:
            if isinstance(self._st, str):
                styles.append(_prefixfix[self._st])
            else:
                styles.extend([_prefixfix[s] for s in self._st])
                
        self.styled = _sgr_seq(*styles) + self.__str__() + _RESET_SEQ

    def foreground(self, color=None):
        if color is not None:
            self._fg = color
            self._update_Postfixed()
        return self._fg

    def background(self, color=None):
        if color is not None:
            self._bg = color
            self._update_Postfixed()
        return self._bg

    def style(string, style=None) -> str:
        if not isinstance(string, Styledstring):
            string = Styledstring(string, style=style)
        string._st = style
        string._update_Postfixed()
        return string.styled

    def color(string, foreground=None, background=None) -> str:
        if not isinstance(string, Styledstring):
            string = Styledstring(string, fg_color=foreground, bg_color=background)
        string.foreground(foreground)
        string.background(background)
        return string.styled

    @staticmethod
    def help():
        pass


fancy = Motif(fg='red', bg='white', styles=[])
fancy.bold(on: bool=True)
fancy.unbold()
fancy.italic(bool)
fancy.unitalic(bool)
fancy.underline()
fancy.deunderline()
fancy.blink()
fancy.noblink()
fancy.faint()
fancy.notfaint()

class Motif(str):
    #TODO: relieve dependency on str inheritence
    #      Motif should eventually implement all string methods
    def __init__(self, text=None, fg=None, bg=None, styles=[]):
        self._fg = fg
        self._bg = bg
        self._st = styles

        #TODO: Implement these as dict. 
        # All of these can be applied at once, including Faint and Bold
        # Mixing some effects may vary by terminal
        self._bld = False  # Bold
        self._lgt = False  # Faint / Light
        self._itc = False  # Italic
        self._udl = False  # Underline
        self._bln = False  # Blink (Currently only ANSI "slow blink")
        self._xot = False  # Strike aka Crossed Out, Strikethrough

    def __new__(cls, text=None, *args, **kwargs):
        """ Return a string instance """
        return str.__new__(cls, text)

    def bold(self, on: bool=True) -> Motif:
        return self

    def italic(self, on: bool=True) -> Motif:
        return self

    def underline(self, on: bool=True) -> Motif:
        return self

    def bold(self, on: bool=True) -> Motif:
        return self

fancy = Motif()
fancy.bold()

test_Postfixedstring = Styledstring('FORMATTED', fg_color='red', style=['underline', 'bold', 'faint'])
test_Postfixedstring.color('blue')
print(test_Postfixedstring.styled)
test_Postfixedstring = Styledstring('FORMATTED', fg_color='red', style=['underline', 'faint'])
test_Postfixedstring.color('blue')
print(test_Postfixedstring.styled)
test_Postfixedstring2 = Styledstring('FORMATTED', fg_color='red', style='bold')
print(test_Postfixedstring2.styled)
print(Styledstring.color('temp Styledstring', 'red'))
'''

