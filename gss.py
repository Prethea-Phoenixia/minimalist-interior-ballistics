"""
Jinpeng Zhai 翟锦鹏
2023/11/16
914962409@qq.com
"""

import math
from typing import Callable, Tuple

invphi = (math.sqrt(5) - 1) / 2  # 1 / phi
invphi2 = (3 - math.sqrt(5)) / 2  # 1 / phi^2


def gss_interval(
    f: Callable,
    x_0: float,
    x_1: float,
    find: str,
    tol: float = 1e-4,
    max_it: int = 100,
) -> Tuple[float, float]:
    """Golden-section search. improved from the example
    given on wikipedia. Reuse half the evaluations.

    Given a function f with a single local extremum in
    the interval [a,b], gss returns a subset interval
    [c,d] that contains the extremum with d-c <= tol.

    a-c-d-b

    ____Parameters______________________________________________________________________
        f:
            functions
        x_0:
            one argument
        x_1:
            another argument
        y:
            reference value, used as a target for zero finding, equivalent to
            lambda x: f(x) - y, y_abs_tol = y * y_rel_tol

        ____Tolerance_Specification____________________________________________________
        tol:
            the change in x value that is considered acceptable
        max_it:
            salvage mechanism, limit the maximum amount of iterations that will
            be accepted to prevent infinite runoff

    ____Return_Signature________________________________________________________________
        x_0, x_1:
            two current best guesses that brackets the real optimum, guaranteed to
            preserve order.
    """

    if find == "min":
        find_min = True
    elif find == "max":
        find_min = False
    else:
        raise ValueError(f"{find} should be either 'min' or 'max'")

    a, b = min(x_0, x_1), max(x_0, x_1)
    h = b - a

    # Required steps to achieve tolerance
    n = max(min(math.ceil(math.log(tol / h, invphi)), max_it), 0)

    c, d = a + invphi2 * h, a + invphi * h
    yc, yd = f(c), f(d)

    for k in range(n):

        if (yc < yd and find_min) or (yc > yd and not find_min):
            # a---c---d  b
            b, d = d, c
            yd = yc
            h *= invphi
            c = a + invphi2 * h
            yc = f(c)

        else:
            # a   c---d---b
            a, c = c, d
            yc = yd
            h *= invphi
            d = a + invphi * h
            yd = f(d)

    if (yc < yd and find_min) or (yc > yd and not find_min):
        return a, d
    else:
        return c, b


if __name__ == "__main__":

    def f(x):
        return (x - 1) ** 2

    print(gss_interval(f, 0, 2, find="min"))
