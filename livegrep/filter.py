import itertools
import re
from typing import List
from typing import Pattern, Match, Optional


class FilterRegex:
    def __init__(self, patt: Pattern, negative: bool):
        self._patt = patt
        self._is_negative = negative

    @property
    def patt(self) -> Pattern:
        return self._patt

    @property
    def is_negative(self) -> bool:
        return self._is_negative

    def match(self, s: str, return_all_matches: bool) -> Optional[List[Match]]:
        if return_all_matches:
            m = list(self._patt.finditer(s))
            return m or None
        else:
            m = self._patt.search(s)
            return None if m is None else [m]

    def keep_line(self,
                  s: str,
                  return_all_matches: bool) -> (bool, Optional[List[Match]]):
        m = self.match(s, return_all_matches)
        return (m is None) if self._is_negative else (m is not None), m

    def __str__(self) -> str:
        return "%s(%s %s)" % (self.__class__.__name__,
                              '-' if self._is_negative else '+',
                              self._patt)

    @classmethod
    def neg(cls, patt: Pattern) -> 'FilterRegex':
        return cls(patt, negative=True)

    @classmethod
    def pos(cls, patt: Pattern) -> 'FilterRegex':
        return cls(patt, negative=False)


# class NegativeFilterRegex(FilterRegex):
#     def keep_line(self, s: str) -> (bool, Optional[List[Match]]):
#         m = self.match(s)
#         return m is None, m
#
#
# class PositiveFilterRegex(FilterRegex):
#     def keep_line(self, s: str) -> (bool, Optional[List[Match]]):
#         m = self.match(s)
#         return m is not None, m


class MultiFilterRegex(FilterRegex):
    def __init__(self, *patt: Pattern):
        super().__init__(patt[0], negative=False)
        self._patt = patt

    def match(self, s: str, return_all_matches: bool) -> Optional[List[Match]]:
        m = []
        if return_all_matches:
            for p in self._patt:
                m.append([x for x in p.finditer(s) if x is not None])
            flattened_m = list(itertools.chain(m))
            return flattened_m or None
        else:
            for p in self._patt:
                m.append(p.search(s))
            return m or None


def read_patterns() -> List[FilterRegex]:
    filters = []
    with open('patterns.txt') as f:
        for line in f.readlines():
            if not line.startswith(('+', '-')):
                continue
            sign, regex = line.rstrip('\n').split(' ', 1)
            regex = re.compile(regex)
            if sign == '-':
                filters.append(FilterRegex.neg(regex))
            elif sign == '++':
                filters.append(FilterRegex.pos(regex))
            else:  # sign == '+'
                if filters:
                    # if isinstance(filters[-1], NegativeFilterRegex):
                    if filters[-1].is_negative:
                        filters.append(FilterRegex.pos(regex))
                    else:
                        if isinstance(filters[-1], MultiFilterRegex):
                            rxs = *filters[-1].patt, regex
                        else:  # PositiveFilterRegex
                            rxs = filters[-1].patt, regex
                        filters[-1] = MultiFilterRegex(*rxs)
                else:
                    filters.append(FilterRegex.pos(regex))
    return filters


re_filts = read_patterns()


def filter_lines(ll):
    for i in range(len(ll)):
        l = ll[i]
        skip = False
        for re_filt in re_filts:
            # TODO funktionsaufruf keep_line() ist langsamer als variante mit isinstance!?
            keep_line, _ = re_filt.keep_line(l, False)
            if not keep_line:
                skip = True
                break
            # if re_filt.is_negative:
            # #if isinstance(re_filt, NegativeFilterRegex):
            #     if re_filt.match(l) is not None:
            #         skip = True
            #         break
            # else:  # positive
            #     if re_filt.match(l) is None:
            #         skip = True
            #         break
        if skip:
            ll[i] = None
