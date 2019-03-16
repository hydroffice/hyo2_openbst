from statistics import median
from typing import Sequence


class RawDecoding:

    @classmethod
    def perbeam_bs_from_snippets_using_median(cls, snippets: Sequence) -> float:

        if len(snippets) == 0:
            return float('nan')

        return median(snippets)

