""" styledstring.py
Provides a Styledstring class that holds a string, along with color and style attributes
Currently relies on ANSI escape sequences
Tested on Windows PowerShell, Unix/Linux
"""
from typing import overload, Optional


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


class Styledstring(str):
    """ Behaves like a normal str, with added styling

    fg / bg colors: black, red, green, yellow, blue, magenta, cyan, white, default
    
    attrs: bold, faint, italic, underline, blink, strike

    Usage: to get the styled version of the string, Styledstring.styled
    EX: to print the styled version, do print(Styledstring.styled)
    
    NOTE: for compatibility, simply passing Styledstring will pass the unstyled string.
    EX: if text = Styledstr("sampletext", fg='red'), print(text) will output: sampletext
    (This is an intermediary fix until all str methods are implemented)
    """    
    def __new__(cls, string, *args, **kwargs):
        """ Return a string instance """
        return str.__new__(cls, string)

    def __init__(self, string, fg=None, bg=None, attrs: Optional[list]=None):
        self._fg = fg
        self._bg = bg
        self._st = attrs

        self.styled = None
        self._update_styled()

    def _update_styled(self):
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
                
        self.styled = _sgr_seq(*styles) + self.__str__() + _RESET_SEQ

    def foreground(self, color=None):
        if color is not None:
            self._fg = color
            self._update_styled()
        return self._fg

    def background(self, color=None):
        if color is not None:
            self._bg = color
            self._update_styled()
        return self._bg

    def style(string, style=None) -> str:
        if not isinstance(string, Styledstring):
            string = Styledstring(string, style=style)
        string._st = style
        string._update_styled()
        return string.styled

    def color(string, foreground=None, background=None) -> str:
        if not isinstance(string, Styledstring):
            string = Styledstring(string, fg=foreground, bg=background)
        string.foreground(foreground)
        string.background(background)
        return string.styled

    @staticmethod
    def help():
        pass


if __name__ == "__main__":
    red_ul_bold_faint = Styledstring('Red, underlined, bold, faint', fg='red', attrs=['underline', 'bold', 'faint'])
    print(red_ul_bold_faint.styled)
    blue_italic_blink = Styledstring('FORMATTED', fg='blue', attrs=['italic', 'blink'])
    print(blue_italic_blink.styled)
