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
    _quotes: int = 0
    _semicolons: int = 0
    _equals: int = 0

    # sb = square brackets open close, p = parenthesis
    _sbo, _sbc, _po, _pc = 0, 0, 0, 0

    count, s = 0, ""

    current_key, headers = '', dict()

    def _niq(self) -> bool:
        """The character pointer/cursor is currently not in a
        location in the PX file that's inside a quoted string."""
        return self._quotes % 2 == 0


    def parse_file(self, f: FileIO):
        while data := f.read(self.chunk_size):
            for c in data:
                if self.parse_character(c):
                    return


    def parse_character(self, c: str) -> bool:
        """
        Returns a bool to signify whether we should stop parsing here.
        """

        self.count += 1

        if c == '"':
            self._quotes += 1

        elif c == '\n' or c == '\r':
            if not self._niq():
                raise ParseException("There can't be newlines inside quoted strings.")
            return False

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

        elif c == '=' and self._niq():
            if self._semicolons != self._equals:
                raise ParseException("Found a second equals sign without a matching semicolon. Unexpected keyword terminator.")

            # end of key
            if self.s == 'DATA':
                return True
            self._equals += 1
            self.current_key = self.s
            self.s = ''
            return False

        elif c == ';' and self._niq():
            if self._semicolons >= self._equals:
                raise ParseException("Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")

            # end of value
            self._semicolons += 1
            self.headers[self.current_key] = self.s
            self.s = ''
            return False

        self.s += c
        return False

    def __str__(self) -> str:
        return 'count: {}, sbo: {}, sbc: {}, po: {}, pc: {}, quotes: {}, semis: {}, equals: {}'.format(
            self.count, self._sbo, self._sbc, self._po, self._pc,
            self._quotes, self._semicolons, self._equals
        )


def main():
    import tracemalloc
    tracemalloc.start()
    px_parser = CounterParser()
    with open(_FILENAME, 'r', encoding='ISO-8859-15') as f:
        px_parser.parse_file(f)
    print(px_parser)
    # print(px_parser.headers)
    print(tracemalloc.get_traced_memory())
    tracemalloc.stop()


if __name__ == '__main__':
    main()
