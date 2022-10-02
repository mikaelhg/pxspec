#!/bin/env python

import io


_FILENAME = '../gpcaxis/data/statfin_vtp_pxt_124l.px'

class ParseException(Exception):
    """PX parse failed"""


class CounterParser(object):
    """A POC for doing preliminary non-validating parsing for the
    header section of a PX file with counters and one _accumulator
    only, rather than a more complex state machine.
    """

    chunk_size = 4096

    # How many of these characters we've seen in this parse
    _quotes: int = 0
    _semicolons: int = 0
    _equals: int = 0
    _accumulator: str = ''

    count: int = 0
    keys: list = list()
    values: list = list()


    def parse_file(self, f: io.FileIO):
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

        elif c == '=' and self._niq():
            if self._semicolons != self._equals:
                raise ParseException("Found a second equals sign without a matching semicolon. Unexpected keyword terminator.")

            # end of key
            if self._accumulator == 'DATA':
                return True
            self._equals += 1
            self.keys.append(self._accumulator)
            self._accumulator = ''
            return False

        elif c == ';' and self._niq():
            if self._semicolons >= self._equals:
                raise ParseException("Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")

            # end of value
            self._semicolons += 1
            self.values.append(self._accumulator)
            self._accumulator = ''
            return False

        self._accumulator += c
        return False

    def _niq(self) -> bool:
        """The character pointer/cursor is currently not in a
        location in the PX file that's inside a quoted string."""
        return self._quotes % 2 == 0

    def __str__(self) -> str:
        return 'count: {}, quotes: {}, semis: {}, equals: {}'.format(
            self.count, self._quotes, self._semicolons, self._equals
        )


def main():
    px_parser = CounterParser()
    with io.open(_FILENAME, 'r', encoding='ISO-8859-15') as f:
        px_parser.parse_file(f)
    print(px_parser)
    # print(dict(zip(px_parser.keys, px_parser.values)))


if __name__ == '__main__':
    main()
