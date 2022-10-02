#!/bin/env python

import argparse
from dataclasses import dataclass, field
import io


_FILENAME = '../gpcaxis/data/statfin_vtp_pxt_124l.px'


class ParseException(Exception):
    """PX parse failed"""


@dataclass
class PxHeaderKeyword:
    keyword: str = ''
    language: str = ''
    subkeys: list[str] = field(default_factory=list)
    def __hash__(self) -> int:
        if self.subkeys:
            return hash((self.keyword, self.language, *self.subkeys))
        else:
            return hash((self.keyword, self.language))


@dataclass
class PxHeaderValue:
    values: list[str] = field(default_factory=list)
    def __hash__(self) -> int:
        return hash(tuple(self.values))


@dataclass
class PxHeaderRow:
    keyword: PxHeaderKeyword = None
    value: PxHeaderValue = None


@dataclass
class RowAccumulator:
    keyword: str = ''
    language: str = ''
    subkey: str = ''
    subkeys: list[str] = field(default_factory=list)
    value: str = ''
    values: list[str] = field(default_factory=list)

    def get_keyword(self) -> PxHeaderKeyword:
        return PxHeaderKeyword(
            self.keyword,
            self.language if self.language != '' else None,
            self.subkeys if len(self.subkeys) > 0 else None
        )


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
    row = RowAccumulator()


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
        in_parenthesis = self._parenthesis_open > self._parenthesis_close
        in_key = self._semicolons == self._equals
        in_language = in_key and self._squarebracket_open > self._squarebracket_close
        in_subkey = in_key and in_parenthesis

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

        elif c == '(' and not in_key and not in_quotes:
            # TLIST(
            self._parenthesis_open += 1
            self.row.value += c

        elif c == ')' and in_key and not in_quotes:
            self._parenthesis_close += 1
            self.row.subkeys.append(self.row.subkey)
            self.row.subkey = ''

        elif c == ')' and not in_key and not in_quotes:
            # TLIST()
            self._parenthesis_close += 1
            self.row.value += c

        elif c == ',' and in_subkey and not in_quotes:
            self.row.subkeys.append(self.row.subkey)
            self.row.subkey = ''

        elif c == ',' and not in_key and not in_quotes and not in_parenthesis:
            self.row.values.append(self.row.value)
            self.row.value = ''

        elif c == '=' and not in_key and not in_quotes:
            raise ParseException(
                "Found a second equals sign without a matching semicolon. Unexpected keyword terminator.")

        elif c == '=' and in_key and not in_quotes:
            if self.row.keyword == 'DATA':
                return True
            self._equals += 1
            return False

        elif c == ';' and not in_quotes:
            if in_key:
                raise ParseException(
                    "Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")
            if len(self.row.value) > 0:
                self.row.values.append(self.row.value)
            self._semicolons += 1
            self.headers[self.row.get_keyword()] = self.row.values
            self.row = RowAccumulator()
            return False

        elif in_subkey:
            self.row.subkey += c

        elif in_language:
            self.row.language += c

        elif in_key:
            self.row.keyword += c

        else:
            self.row.value += c

        return False

    def __str__(self) -> str:
        return 'count: {}, quotes: {}, semis: {}, equals: {}'.format(
            self.count, self._quotes, self._semicolons, self._equals
        )


def _parse_args():
    parser = argparse.ArgumentParser(description='Parse PX file.')
    parser.add_argument('file', type=str, default=_FILENAME)
    return parser.parse_args()


def main(args):
    px_parser = CounterParser()
    with io.open(args.file, 'r', encoding='ISO-8859-15') as f:
        px_parser.parse_file(f)
    # print(dict(zip(px_parser.keys, px_parser.values)))
    print(px_parser.headers)
    print(px_parser)


if __name__ == '__main__':
    main(_parse_args())
