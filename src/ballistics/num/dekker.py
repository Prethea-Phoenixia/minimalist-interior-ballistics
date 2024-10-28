from __future__ import annotations

from typing import Callable, Tuple


def dekker(
    f: Callable[[float], float], x_0: float, x_1: float, tol: float, max_it: int = 33
) -> Tuple[float, float]:
    """
    Dekker algorithm for finding the root of a univariate function on a bracketing
    interval. Returns the best estimate and its counterpoint.

    Parameters
    ----------
    f : Callable[[float], float]
        univariate function defined on [min(`x_0`, `x_1`), max(`x_0`, `x_1`)].
    x_0, x_1 : float
        interval of the root. must *strictly* brackets the root.
    tol:
        convergence criteria, maximum accepted difference between estimate and its
        counterpoint.
    max_it:
        terminating condition, maximum number of iterations before calculation is aborted.

    Returns
    -------
    x_best, x_bracketing : float
        the current best estimate and its counterpoint.

    Raises
    ------
    ValueError
        if the supplied interval does not bracket the root.
    ValueError
        if the maximum iteration has been exceeded.

    Notes
    -----
    This is a hybrid root finding algorithm that combines the bisection and secant method.
    On every iteration, both methods are called to generate the next estimate of the
    root, accepting the secant estimate when it is strictly between current best estimate
    and mid-point estimate. If this results in a sign change, the contrapoint is updated
    with the previous best estimate.

    This allows faster convergence when functions are well behaved, but if successive
    secant branches are taken, the convergence can be poorer than simple bisection.

    References
    ----------
    - **[1]** Dekker, T. J. (1969), "Finding a zero by means of successive linear
    interpolation", in Dejon, B.; Henrici, P. (eds.), Constructive Aspects of the
    Fundamental Theorem of Algebra, London: Wiley-Interscience, ISBN 978-0-471-20300-1

    """
    tol = abs(tol)  # ensure non-negative
    fx_0, fx_1 = f(x_0), f(x_1)

    if fx_0 * fx_1 >= 0:
        raise ValueError(
            "Dekker method must be initiated by bracketing points:\n"
            + "f({})={}, f({})={}".format(x_0, fx_0, x_1, fx_1)
        )

    (b_j, fb_j) = (x_0, fx_0) if abs(fx_0) < abs(fx_1) else (x_1, fx_1)
    (b_i, fb_i) = (a_j, fa_j) = (x_1, fx_1) if abs(fx_0) < abs(fx_1) else (x_0, fx_0)

    i = 0
    for i in range(max_it):
        m = 0.5 * (a_j + b_j)
        if fb_i != fb_j:
            s = b_j - fb_j * (b_j - b_i) / (fb_j - fb_i)  # secant estimate
        else:
            s = m

        if min(b_j, m) < s < max(b_j, m):
            # if secant estimate strictly between current estimate and bisection estimate
            b_k = s  # assign the secant estimation to be the next estimate
        else:
            b_k = m

        fb_k = f(b_k)  # calculate new value of estimate

        if fa_j * fb_k < 0:
            # if the contrapoint is of different sign than current estimate
            (a_k, fa_k) = (a_j, fa_j)  # new contrapoint is still the same
        else:  # otherwise, new contrapoint should use the current est.
            (a_k, fa_k) = (b_j, fb_j)

        if abs(fa_k) < abs(fb_k):  # ensure b is still the best guess
            (a_k, fa_k), (b_k, fb_k) = (b_k, fb_k), (a_k, fa_k)

        if abs(b_k - a_k) < tol:
            return b_k, a_k  # return the best, and the bracketing solution

        (a_j, fa_j), (b_i, fb_i), (b_j, fb_j) = (a_k, fa_k), (b_j, fb_j), (b_k, fb_k)

    else:
        # the entire loop has been ran without break or return.
        raise ValueError("Maximum iteration exceeded.")


if __name__ == "__main__":

    def f(x: float) -> float:

        return x**2 - 1

    print(dekker(f, 0.5, 1.5, tol=1e-4))
