#!/bin/env python

import io


_FILENAME = '../gpcaxis/data/statfin_vtp_pxt_124l.px'

class ParseException(Exception):
    """PX parse failed"""


class Accumulators:
    keyword = ''
    language = ''
    subkey = ''
    subkeys = list()
    value = ''
    values = list()

    def reset(self):
        self.keyword = ''
        self.language = ''
        self.subkey = ''
        self.value = ''
        self.subkeys = list()
        self.values = list()


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
    _squarebracket_open: int = 0
    _squarebracket_close: int = 0
    _parenthesis_open: int = 0
    _parenthesis_close: int = 0

    count: int = 0
    headers = dict()
    acc = Accumulators()

    def parse_file(self, f: io.FileIO):
        while data := f.read(self.chunk_size):
            for c in data:
                if self.parse_character(c):
                    return


    def parse_character(self, c: str) -> bool:
        """
        Returns a bool to signify whether we should stop parsing here.
        """

        in_quotes = self._quotes % 2 == 1
        in_key = self._semicolons == self._equals
        in_language = in_key and self._squarebracket_open > self._squarebracket_close
        in_subkey = in_key and self._parenthesis_open > self._parenthesis_close

        self.count += 1

        if c == '"':
            self._quotes += 1

        elif c == '\n' or c == '\r':
            if in_quotes:
                raise ParseException("There can't be newlines inside quoted strings.")
            return False

        elif c == '[' and in_key and not in_quotes:
            self._squarebracket_open += 1

        elif c == ']' and in_key and not in_quotes:
            self._squarebracket_close += 1

        elif c == '(' and in_key and not in_quotes:
            self._parenthesis_open += 1

        elif c == ')' and in_key and not in_quotes:
            self._parenthesis_close += 1
            self.acc.subkeys.append(self.acc.subkey)
            self.acc.subkey = ''

        elif c == ',' and in_subkey and not in_quotes:
            self.acc.subkeys.append(self.acc.subkey)
            self.acc.subkey = ''

        elif c == ',' and not in_subkey and not in_quotes:
            self.acc.values.append(self.acc.value)
            self.acc.value = ''

        elif c == '=' and not in_quotes:
            if not in_key:
                raise ParseException(
                    "Found a second equals sign without a matching semicolon. Unexpected keyword terminator.")

            if self.acc.keyword == 'DATA':
                return True
            self._equals += 1
            return False

        elif c == ';' and not in_quotes:
            if in_key:
                raise ParseException(
                    "Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")
            if len(self.acc.value) > 0:
                self.acc.values.append(self.acc.value)
            self._semicolons += 1
            self.headers[(self.acc.keyword, self.acc.language, tuple(self.acc.subkeys))] = \
                self.acc.values
            self.acc.reset()
            return False

        elif in_subkey:
            self.acc.subkey += c
        elif in_language:
            self.acc.language += c
        elif in_key:
            self.acc.keyword += c
        else:
            self.acc.value += c

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
    # print(dict(zip(px_parser.keys, px_parser.values)))
    print(px_parser.headers)
    print(px_parser)


if __name__ == '__main__':
    main()
