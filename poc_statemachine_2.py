#!/bin/env python

import argparse
from dataclasses import dataclass, field
import io

from typing.io import TextIO


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

    def to_keyword(self) -> PxHeaderKeyword:
        return PxHeaderKeyword(
            self.keyword,
            self.language if self.language != '' else None,
            self.subkeys if len(self.subkeys) > 0 else None
        )

    def to_value(self) -> PxHeaderValue:
        return PxHeaderValue(self.values)

    def to_row(self) -> PxHeaderRow:
        return PxHeaderRow(self.to_keyword(), self.to_value())


@dataclass
class HeaderParseState:
    quotes: int = 0
    semicolons: int = 0
    equals: int = 0
    squarebracket_open: int = 0
    squarebracket_close: int = 0
    parenthesis_open: int = 0
    parenthesis_close: int = 0


class CounterParser(object):
    """A POC for doing preliminary non-validating parsing for the
    header section of a PX file with counters and one _accumulator
    only, rather than a more complex state machine.
    """

    chunk_size = 4096
    count: int = 0
    headers = dict()
    row = RowAccumulator()
    hs = HeaderParseState()

    def parse_file(self, f: TextIO):
        while data := f.read(self.chunk_size):
            for c in data:
                if self.parse_character(c):
                    return

    def parse_character(self, c: str) -> bool:
        """
        Returns a bool to signify whether we should stop parsing here.
        """

        in_quotes = self.hs.quotes % 2 == 1
        in_parenthesis = self.hs.parenthesis_open > self.hs.parenthesis_close
        in_key = self.hs.semicolons == self.hs.equals
        in_language = in_key and self.hs.squarebracket_open > self.hs.squarebracket_close
        in_subkey = in_key and in_parenthesis

        self.count += 1

        if c == '"':
            self.hs.quotes += 1

        elif (c == '\n' or c == '\r') and in_quotes:
            raise ParseException("There can't be newlines inside quoted strings.")

        elif (c == '\n' or c == '\r') and not in_quotes:
            return False

        elif c == '[' and in_key and not in_quotes:
            self.hs.squarebracket_open += 1

        elif c == ']' and in_key and not in_quotes:
            self.hs.squarebracket_close += 1

        elif c == '(' and in_key and not in_quotes:
            self.hs.parenthesis_open += 1

        # TLIST opening quote
        elif c == '(' and not in_key and not in_quotes:
            self.hs.parenthesis_open += 1
            self.row.value += c

        elif c == ')' and in_key and not in_quotes:
            self.hs.parenthesis_close += 1
            self.row.subkeys.append(self.row.subkey)
            self.row.subkey = ''

        # TLIST closing quote
        elif c == ')' and not in_key and not in_quotes:
            self.hs.parenthesis_close += 1
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
            self.hs.equals += 1
            return False

        elif c == ';' and not in_quotes and in_key:
            raise ParseException(
                "Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")

        elif c == ';' and not in_quotes and not in_key:
            if len(self.row.value) > 0:
                self.row.values.append(self.row.value)
            self.hs.semicolons += 1
            self.headers[self.row.to_keyword()] = self.row.to_value()
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

    def values(self, keyword: str, language: str = None, subkeys: list[str] = None):
        return self.headers[PxHeaderKeyword(keyword, language, subkeys)].values

    def __str__(self) -> str:
        return f'{self.hs=}'


def _parse_args():
    parser = argparse.ArgumentParser(description='Parse PX file.')
    parser.add_argument('file', type=str)
    parser.add_argument('--encoding', type=str, default='ISO-8859-15')
    return parser.parse_args()


def main(args):
    px_parser = CounterParser()
    with io.open(args.file, 'r', encoding=args.encoding) as f:
        px_parser.parse_file(f)
    stub = px_parser.values('STUB')
    heading = px_parser.values('HEADING')
    stubs = {k: px_parser.values('VALUES', None, [k]) for k in stub}
    headings = {k: px_parser.values('VALUES', None, [k]) for k in heading}
    # print(px_parser.headers)
    print(f'{stub=}, {stubs=}')
    print(f'{heading=} {headings=}')
    print(px_parser)


if __name__ == '__main__':
    main(_parse_args())
