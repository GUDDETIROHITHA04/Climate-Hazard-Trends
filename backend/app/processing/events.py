"""Shared helper: find runs of consecutive True values."""
import numpy as np


def find_runs(flag, min_len: int):
    """Return [(start, end_exclusive)] of runs of True with length >= min_len."""
    padded = np.concatenate([[0], np.asarray(flag, dtype=int), [0]])
    d = np.diff(padded)
    return [(int(s), int(e)) for s, e in zip(np.where(d == 1)[0], np.where(d == -1)[0]) if e - s >= min_len]
