#!/bin/env python

from io import FileIO


# _FILENAME = '../gpcaxis/data/010_kats_tau_101.px'
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

        match (
            c,
            self._niq(),
            self._po <= self._pc,
            self._sbo <= self._sbc,
            self._semicolons == self._equals,
        ):

            case ('"', _, _, _, _):
                self._quotes += 1

            case ('\n' | '\r', False, _, _, _):
                raise ParseException("There can't be newlines inside quoted strings.")

            case ('\n' | '\r', True, _, _, _):
                return False

            case ('(', True, False, _, _):
                raise ParseException("There can't be nested parentheses, only one can be open.")

            case ('(', True, True, _, _):
                self._po += 1

            case (')', True, True, _, _):
                raise ParseException("There can't be a close parentheses if none is open.")

            case (')', True, False, _, _):
                self._pc += 1

            case ('[', True, _, False, _):
                raise ParseException("There can't be nested square brackets, only one can be open.")

            case ('[', True, _, True, _):
                self._sbo += 1

            case (']', True, _, True, _):
                raise ParseException("There can't be a close square brackets if none is open.")

            case (']', True, _, False, _):
                self._sbc += 1

            case ('=', True, _, _, False):
                raise ParseException("Found a second equals sign without a matching semicolon. Unexpected keyword terminator.")

            case ('=', True, _, _, True):
                # end of key
                if self.s == 'DATA':
                    return True
                self._equals += 1
                self.current_key = self.s
                self.s = ''
                return False

            case (';', True, _, _, True):
                raise ParseException("Found a semicolon without a matching equals sign. Value terminator without keyword terminator.")

            case (';', True, _, _, False):
                # end of value
                self._semicolons += 1
                self.headers[self.current_key] = self.s
                self.s = ''
                return False

        self.s += c
        return False

    def _niq(self) -> bool:
        """The character pointer/cursor is currently not in a
        location in the PX file that's inside a quoted string."""
        return self._quotes % 2 == 0

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
