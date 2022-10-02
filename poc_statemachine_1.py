#!/bin/env python

from io import FileIO


# _FILENAME = '../gpcaxis/data/010_kats_tau_101.px'
# _FILENAME = '../gpcaxis/data/example4.px'
_FILENAME = '../gpcaxis/data/statfin_vtp_pxt_124l.px'


class ParseException(Exception):
    """PX parse failed"""


class HeaderParser(object):
    """A POC for doing preliminary non-validating parsing for the
    header section of a PX file with counters and one accumulator
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

    character_count, accumulator = 0, ""

    current_key, headers = '', dict()

    def parse_file(self, f: FileIO):
        while data := f.read(self.chunk_size):
            for c in data:
                if self.parse_character(c):
                    return

    def parse_character(self, character: int) -> bool:
        """
        Returns a bool to signify whether we should stop parsing here.
        """

        self.character_count += 1

        match (
            character,
            self._quotes % 2 == 1,
            self._parenthesis_open <= self._parenthesis_close,
            self._squarebracket_open <= self._squarebracket_close,
            self._semicolons == self._equals,
        ):

            case ('"', _, _, _, _):
                self._quotes += 1

            case ('\n' | '\r', True, _, _, _):
                raise ParseException("There can't be newlines inside quoted strings.")

            case ('\n' | '\r', False, _, _, _):
                return False

            case ('(', False, False, _, _):
                raise ParseException("There can't be nested parentheses, only one can be open.")

            case ('(', False, True, _, _):
                self._parenthesis_open += 1

            case (')', False, True, _, _):
                raise ParseException("There can't be a close parentheses if none is open.")

            case (')', False, False, _, _):
                self._parenthesis_close += 1

            case ('[', False, _, False, _):
                raise ParseException("There can't be nested square brackets, only one can be open.")

            case ('[', False, _, True, _):
                self._squarebracket_open += 1

            case (']', False, _, True, _):
                raise ParseException("There can't be a close square brackets if none is open.")

            case (']', False, _, False, _):
                self._squarebracket_close += 1

            case ('=', False, _, _, False):
                raise ParseException(
                    "Found a second equals sign without a matching semicolon. Unexpected keyword terminator.")

            case ('=', False, _, _, True):
                if self.accumulator == 'DATA':
                    return True
                self._equals += 1
                self.current_key = self.accumulator
                self.accumulator = ''
                return False

            case (';', False, _, _, True):
                raise ParseException(
                    "Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")

            case (';', False, _, _, False):
                self._semicolons += 1
                self.headers[self.current_key] = self.accumulator
                self.accumulator = ''
                return False

        self.accumulator += character
        return False

    def __str__(self) -> str:
        return f"{self.character_count=} {self._quotes=} {self._semicolons=} {self._equals=}\n" \
               f"{self._squarebracket_open=} {self._squarebracket_close=}\n" \
               f"{self._parenthesis_open=} {self._parenthesis_close=}"


def main():
    import tracemalloc
    tracemalloc.start()
    px_parser = HeaderParser()
    with open(_FILENAME, 'r', encoding='ISO-8859-15') as f:
        px_parser.parse_file(f)
    print(px_parser)
    # print(px_parser.headers)
    print(tracemalloc.get_traced_memory())
    tracemalloc.stop()


if __name__ == '__main__':
    main()
