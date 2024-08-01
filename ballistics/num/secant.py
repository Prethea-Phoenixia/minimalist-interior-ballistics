from typing import Callable, Tuple
from math import inf


def secant(
    f: Callable[[float], float],
    x_0: float,
    x_1: float,
    x_min: float = -inf,
    x_max: float = inf,
    tol: float = 1e-16,
    max_it: int = 100,
) -> Tuple[float, float]:
    tol = abs(tol)
    fx_0, fx_1 = f(x_0), f(x_1)

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
        raise ValueError(
            f"Secant method called from {x_min} to {x_max}\n"
            + f"Maximum iteration exceeded at it = {i}/{max_it}"
            + ",\n[0] f({})={}->\n[1] f({})={}->\n[2] f({})={}".format(
                x_0, fx_0, x_1, fx_1, x_2, fx_2
            )
        )
