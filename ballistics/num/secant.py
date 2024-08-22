from math import inf
from typing import Callable, Tuple


def secant(
    f: Callable[[float], float],
    x_0: float,
    x_1: float,
    tol: float,
    x_min: float = -inf,
    x_max: float = inf,
    max_it: int = 100,
) -> Tuple[float, float]:
    """
    use secant method to solve the zero of a univariate function.

    Parameters
    ----------
    f: Callable[[float], float]
        univariate function defined on (at least) [x_min, x_max].
    x_0, x_1: float
        two initial guesses to seed the secant algorithm.
    x_min, x_max: float
        bounds on which the root is to be found. Default values
        [-inf, +inf].
    tol: float
        convergence criteria. The algorithm will terminate when the solution for the
        root does not vary more than abs(`tol`) in any single iteration.
    max_it: int
        terminating condition, maximum number of iterations before the calculation
        is aborted.


    Raises
    ------
    ValuError
        if the maximum number of iteration is exceeded.

    Returns
    -------
    x_2, x_1: float
        solution of successive iteration that satisifies |`x_2` - `x_1`| < abs(`tol`).

    Notes
    -----
    The secant method allows faster convergence on well behaved functions,
    but does not guarantee convergence to a root. it is incumbent upon
    the user to check that the algorithm did not converge to one of the bounds
    (`x_min`, `x_max`) even when the algorithm terminates without error.

    When an error is raised, there are a few possibilities:
    - the function does not have a root on [x_min, x_max], in which case the solution
    will "jump" around a stationary point without converging.
    - the function may not be well behaved in proximity to the root.

    """
    tol = abs(tol)
    fx_0, fx_1 = f(x_0), f(x_1)
    x_min, x_max = min(x_min, x_max), max(x_min, x_max)

    if x_0 == x_1 or fx_0 == fx_1:
        raise ValueError(
            "Impossible to calculate initial slope for secant method."
            + f"\nf({x_0})={fx_0}\nf({x_1})={fx_1}"
        )

    for i in range(max_it):
        x_2 = x_1 - fx_1 * (x_1 - x_0) / (fx_1 - fx_0)
        if x_2 < x_min:
            x_2 = 0.9 * x_min + 0.1 * x_1
        elif x_2 > x_max:
            x_2 = 0.9 * x_max + 0.1 * x_1

        fx_2 = f(x_2)

        if abs(x_2 - x_1) < tol:
            return x_2, x_1

        x_0, x_1, fx_0, fx_1 = x_1, x_2, fx_1, fx_2

    else:
        raise ValueError("Maximum iteration exceeded")
