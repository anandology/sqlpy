"""Utilities.
(partof sqlpy)
"""

__all__ = [
    "IterBetter", "ResultSet", "Row", 
    "interpolate", "safestr"
]

class IterBetter:
    """
    Returns an object that can be used as an iterator 
    but can also be used via __getitem__ (although it 
    cannot go backwards -- that is, you cannot request 
    `iterbetter[0]` after requesting `iterbetter[1]`).
    
        >>> import itertools
        >>> c = iterbetter(itertools.count())
        >>> c[1]
        1
        >>> c[5]
        5
        >>> c[3]
        Traceback (most recent call last):
            ...
        IndexError: already passed 3

    For boolean test, IterBetter peeps at first value in the itertor without effecting the iteration.

        >>> c = iterbetter(iter(range(5)))
        >>> bool(c)
        True
        >>> list(c)
        [0, 1, 2, 3, 4]
        >>> c = iterbetter(iter([]))
        >>> bool(c)
        False
        >>> list(c)
        []

    (Taken from web.utils)
    """
    def __init__(self, iterator): 
        self.i, self.c = iterator, 0

    def __iter__(self): 
        if hasattr(self, "_head"):
            yield self._head

        while 1:    
            yield self.i.next()
            self.c += 1

    def __getitem__(self, i):
        #todo: slices
        if i < self.c: 
            raise IndexError, "already passed "+str(i)
        try:
            while i > self.c: 
                self.i.next()
                self.c += 1
            # now self.c == i
            self.c += 1
            return self.i.next()
        except StopIteration: 
            raise IndexError, str(i)
            
    def __nonzero__(self):
        if hasattr(self, "__len__"):
            return len(self) != 0
        elif hasattr(self, "_head"):
            return True
        else:
            try:
                self._head = self.i.next()
            except StopIteration:
                return False
            else:
                return True

class ResultSet(IterBetter):
    def __init__(self, cursor):
        self.cursor = cursor
        IterBetter.__init__(self, self.iterwrapper())

    def iterwrapper(self):
        names = [x[0] for x in self.cursor.description]        
        values = self.cursor.fetchone()
        while values:
            yield Row(dict(zip(names, values)))
            values = self.cursor.fetchone()

    def list(self):
        return list(self)

    def __len__(self):
        return self.cursor.rowcount

class Row(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttibuteError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __repr__(self):
        return "<Row %r>" % dict(self)

def interpolate(format):
    """
    Takes a format string and returns a list of 2-tuples of the form
    (boolean, string) where boolean says whether string should be evaled
    or not.

    from <http://lfw.org/python/Itpl.py> (public domain, Ka-Ping Yee)
    """
    from tokenize import tokenprog

    def matchorfail(text, pos):
        match = tokenprog.match(text, pos)
        if match is None:
            raise _ItplError(text, pos)
        return match, match.end()

    namechars = "abcdefghijklmnopqrstuvwxyz" \
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_";
    chunks = []
    pos = 0

    while 1:
        dollar = format.find("$", pos)
        if dollar < 0: 
            break
        nextchar = format[dollar + 1]

        if nextchar == "{":
            chunks.append((0, format[pos:dollar]))
            pos, level = dollar + 2, 1
            while level:
                match, pos = matchorfail(format, pos)
                tstart, tend = match.regs[3]
                token = format[tstart:tend]
                if token == "{": 
                    level = level + 1
                elif token == "}":  
                    level = level - 1
            chunks.append((1, format[dollar + 2:pos - 1]))

        elif nextchar in namechars:
            chunks.append((0, format[pos:dollar]))
            match, pos = matchorfail(format, dollar + 1)
            while pos < len(format):
                if format[pos] == "." and \
                    pos + 1 < len(format) and format[pos + 1] in namechars:
                    match, pos = matchorfail(format, pos + 1)
                elif format[pos] in "([":
                    pos, level = pos + 1, 1
                    while level:
                        match, pos = matchorfail(format, pos)
                        tstart, tend = match.regs[3]
                        token = format[tstart:tend]
                        if token[0] in "([": 
                            level = level + 1
                        elif token[0] in ")]":  
                            level = level - 1
                else: 
                    break
            chunks.append((1, format[dollar + 1:pos]))
        else:
            chunks.append((0, format[pos:dollar + 1]))
            pos = dollar + 1 + (nextchar == "$")

    if pos < len(format): 
        chunks.append((0, format[pos:]))
    return chunks

def safestr(s):
    if isinstance(s, str):
        return s
    elif isinstance(s, unicode):
        return s.encode('utf-8')
    else:
        return str(s)
