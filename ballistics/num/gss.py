from __future__ import annotations

import math
from typing import Callable, Tuple

_invphi = (math.sqrt(5) - 1) / 2  # 1 / phi
_invphi2 = (3 - math.sqrt(5)) / 2  # 1 / phi^2

FIND_MIN = "min"
FIND_MAX = "max"


def gss(
    f: Callable[[float], float],
    x_0: float,
    x_1: float,
    tol: float,
    find: str = FIND_MIN,
    max_it: int = 33,
) -> Tuple[float, float]:
    """Golden-section search, for the solution of local extremum of a univariate
    function within a specified interval. Successively divides the interval by (sqrt(5)-1)/2.
    Returns a sub-interval that contains the found extremum, with at most the width
    of the specified tolerance or when exhausting maximum iteration.

    Parameters
    ----------
    f : callable[[float],float]
        univariate objective function, valid on [min(`x_0`, `x_1`), max(`x_0`, `x_1`)].
    x_0, x_1 : float
        bounds of the extremum. Values can be provided in any order.
    find : str
        string flag, either `FIND_MIN` or `FIND_MAX`. Determines whether the search
        will be for a local minima or maxima, respectively.
    tol : float
        convergence criteria, maximum allowed width of the resulting interval.
    max_it: int
        terminating condition, maximum numbers of iterations allowed.

    Returns
    -------
    low_bound, high_bound : float
        subset interval [`low_bound`, `high_bound`] in which the extremum lies.

    Notes
    -----
    Algorithm will terminate and return when either the convergence criteria or the
    terminating condition is met, without raising an error. The user is responsible
    for providing a reasonable initial interval and tolerance.

    """

    if find == FIND_MIN:
        find_min = True
    elif find == FIND_MAX:
        find_min = False
    else:
        raise ValueError(f"{find} should be either '{FIND_MIN}' or '{FIND_MAX}'")

    tol = abs(tol)

    a, b = min(x_0, x_1), max(x_0, x_1)
    h = b - a

    # Required steps to achieve tolerance
    n = max(min(math.ceil(math.log(tol / h, _invphi)), max_it), 0)

    c, d = a + _invphi2 * h, a + _invphi * h
    yc, yd = f(c), f(d)

    for k in range(n):
        h *= _invphi
        if (yc < yd and find_min) or (yc > yd and not find_min):
            # a---c---d  b
            b, (d, yd) = d, (c, yc)
            c = a + _invphi2 * h
            yc = f(c)

        else:  # a   c---d---b
            a, (c, yc) = c, (d, yd)
            d = a + _invphi * h
            yd = f(d)

    if (yc < yd and find_min) or (yc > yd and not find_min):
        return a, d
    else:
        return c, b


if __name__ == "__main__":

    def f(x):
        return (x - 1) ** 2

    print(gss(f, 0, 2, find="min", tol=1e-4))
