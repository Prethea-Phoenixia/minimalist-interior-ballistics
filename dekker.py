"""
Jinpeng Zhai 翟锦鹏
2023/11/16
914962409@qq.com
"""

from typing import Callable, Tuple


def dekker_interval(
    f: Callable, x_0: float, x_1: float, tol: float = 1e-4, max_it: int = 100
) -> Tuple[float, float]:
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
        raise ValueError(
            "Dekker method called from {} to {}\n".format(x_0, x_1)
            + "Maximum iteration exceeded at {}/{} iterations,\n".format(i, max_it)
            + "f({})={}->\nf({})={}".format(b_i, fb_i, b_j, fb_j)
        )


def dekker_scalar(
    f: Callable, x_0: float, x_1: float, tol: float = 1e-4, max_it: int = 100
) -> float:
    return dekker_interval(f=f, x_0=x_0, x_1=x_1, tol=tol, max_it=max_it)[0]


if __name__ == "__main__":

    def f(x: float) -> float:

        return x**2 - 1

    print(dekker_scalar(f, 0.5, 1.5))
