#!/bin/env python

from io import FileIO


_FILENAME = '../gpcaxis/data/010_kats_tau_101.px'
# _FILENAME = '../gpcaxis/data/example4.px'
_FILENAME = '../gpcaxis/data/statfin_vtp_pxt_124l.px'

class ParseException(Exception):
    """PX parse failed"""


class CounterParser(object):
    """A POC for doing preliminary non-validating parsing for the
    header section of a PX file with counters and one accumulator
    only, rather than a more complex state machine.
    """

    chunk_size = 4096

    # How many of these characters we've seen in this parse
    _quotes, _semicolons, _equals, _commas = 0, 0, 0, 0

    # sb = square brackets open close, p = parenthesis
    _sbo, _sbc, _po, _pc = 0, 0, 0, 0

    count, s, keys, values = 0, "", list(), list()

    def _niq(self) -> bool:
        """The character pointer/cursor is currently not in a
        location in the PX file that's inside a quoted string."""
        return self._quotes % 2 == 0


    def parse_file(self, f: FileIO) -> bool:
        while data := f.read(self.chunk_size):
            for c in data:
                if not self.parse_character(c):
                    return True
        return True


    def parse_character(self, c: str) -> bool:
        self.count += 1

        if c == '"':
            self._quotes += 1

        elif c == '\n' or c == '\r':
            if not self._niq():
                raise ParseException("There can't be newlines inside quoted strings.")
            return True

        elif c == '(' and self._niq():
            if self._po > self._pc:
                raise ParseException("There can't be nested parentheses, only one can be open.")
            self._po += 1

        elif c == ')' and self._niq():
            if self._po <= self._pc:
                raise ParseException("There can't be a close parentheses if none is open.")
            self._pc += 1

        elif c == '[' and self._niq():
            if self._sbo > self._sbc:
                raise ParseException("There can't be nested square brackets, only one can be open.")
            self._sbo += 1

        elif c == ']' and self._niq():
            if self._sbo <= self._sbc:
                raise ParseException("There can't be a close square brackets if none is open.")
            self._sbc += 1

        elif c == '=' and self._niq() and self._semicolons == self._equals:
            # end of key
            if self.s == 'DATA':
                return False
            self._equals += 1
            self.keys.append(self.s)
            self.s = ''
            return True

        elif c == ';' and self._niq() and self._semicolons < self._equals:
            # end of value
            self._semicolons += 1
            self.values.append(self.s)
            self.s = ''
            return True

        self.s += c
        return True

    def __str__(self) -> str:
        return 'sbo: {}, sbc: {}, po: {}, pc: {}, quotes: {}, semis: {}, equals: {}'.format(
            self._sbo, self._sbc, self._po, self._pc,
            self._quotes, self._semicolons, self._equals
        )


def main():
    px_parser = CounterParser()
    with open(_FILENAME, 'r', encoding='ISO-8859-15') as f:
        px_parser.parse_file(f)
    print(px_parser)


if __name__ == '__main__':
    main()
