import numpy as np
from statistics import median, mean
from typing import Sequence


class RawDecoding:

    def __init__(self):
        pass

    @classmethod
    def perbeam_bs_from_snippets_using_median(cls, snippets: Sequence) -> float:
        if len(snippets) == 0:
            return float('nan')
        return median(snippets)

    @classmethod
    def perbeam_bs_from_snippits_using_mean(cls, snippets) -> float:
        if len(snippets) == 0:
            return float('nan')
        return mean(snippets)

    @classmethod
    def perbeam_bs_from_beam_average(cls, beam_averages) -> float:
        if len(beam_averages) == 0:
            return float('nan')

        return beam_averages
