#!/bin/env python

import argparse
import csv
from dataclasses import dataclass, field
import io
import itertools


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
    count: int = 0
    quotes: int = 0
    semicolons: int = 0
    equals: int = 0
    squarebracket_open: int = 0
    squarebracket_close: int = 0
    parenthesis_open: int = 0
    parenthesis_close: int = 0


@dataclass
class DataParseState:
    count: int = 0


class CounterParser:
    """A POC for doing preliminary non-validating parsing for the
    header section of a PX file with counters and one _accumulator
    only, rather than a more complex state machine.
    """

    headers = dict()
    row = RowAccumulator()
    hs = HeaderParseState()
    dps = DataParseState()

    def parse_data_dense(self, input: io.TextIOWrapper, output: csv.DictWriter):
        stub = self.header('STUB')
        stub_values = [self.header('VALUES', None, [k]) for k in stub]
        stub_flattened = itertools.product(*stub_values)

        heading = self.header('HEADING')
        heading_values = [self.header('VALUES', None, [k]) for k in heading]
        heading_flattened = list(itertools.product(*heading_values))
        heading_width = len(heading_flattened)
        heading_csv = [' '.join(x) for x in heading_flattened]

        output.writerow(stub + heading_csv)

        dps_count = 0
        values = list()
        value = ''
        value_len = 0
        while d := input.read(1024):
            for c in d:
                dps_count += 1
                if c == ' ' or c == "\n" or c == "\r":
                    if value_len > 0:
                        values.append(value)
                        value = ''
                        value_len = 0
                    if len(values) == heading_width:
                        output.writerow(list(next(stub_flattened)) + values)
                        values = list()
                else:
                    value += c
                    value_len += 1

        self.dps.count = dps_count

    def parse_header(self, br: io.TextIOWrapper):
        while c := br.read(1):
            if self.parse_header_character(c):
                return

    def parse_header_character(self, c: str) -> bool:
        in_quotes = self.hs.quotes % 2 == 1
        in_parenthesis = self.hs.parenthesis_open > self.hs.parenthesis_close
        in_key = self.hs.semicolons == self.hs.equals
        in_language = in_key and self.hs.squarebracket_open > self.hs.squarebracket_close
        in_subkey = in_key and in_parenthesis

        self.hs.count += 1

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

        elif c == ';' and in_key and not in_quotes:
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

    def header(self, keyword: str, language: str = None, subkeys: list[str] = None):
        return self.headers[PxHeaderKeyword(keyword, language, subkeys)].values

    def __str__(self) -> str:
        return f"{self.hs=}\n{self.dps=}"


def _parse_args():
    parser = argparse.ArgumentParser(description='Parse PX file.')
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--encoding', type=str, default='ISO-8859-15')
    parser.add_argument('--trace', action='store_true', default=False,
        help='Trace memory allocations, slows down the process.')
    return parser.parse_args()


def main(args):
    if args.trace:
        import tracemalloc
        tracemalloc.start()
    px_parser = CounterParser()
    with (
        open(args.input, 'r', encoding=args.encoding, buffering=4096) as inf,
        open(args.output, 'w', newline='', buffering=4096) as outf,
    ):
        csv_writer = csv.writer(outf, quoting=csv.QUOTE_NONNUMERIC)
        px_parser.parse_header(inf)
        px_parser.parse_data_dense(inf, csv_writer)
    print(px_parser)
    if args.trace:
        print(tracemalloc.get_traced_memory())
        tracemalloc.stop()


if __name__ == '__main__':
    main(_parse_args())
