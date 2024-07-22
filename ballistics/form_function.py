"""
Jinpeng Zhai 翟锦鹏
2024/07/14
914962409@qq.com
factory funcitons to initialize a form-function as used in interior ballistic
calculation. Note, the precise numerical values for shape function factory
functions doesn't matter -- they are always immediately factored into relative
measurements
"""

from __future__ import annotations
from typing import Dict
from dataclasses import dataclass
from math import pi

CYLINDER = "cylinder"
ROSETTE = "rosette"
HEXAGON = "hexagon"
ROUNDED_HEXAGON = "rounded hexagon"


@dataclass
class FormFunction:
    chi: float
    labda: float
    mu: float
    Z_k: float = 1.0
    # these values are only used when Z_k >1
    chi_s: float = 0
    labda_s: float = 0

    def __post_init__(self):
        if self.Z_k > 1:
            psi_s = self(1)
            self.chi_s = (1 - psi_s * self.Z_k**2) / (self.Z_k - self.Z_k**2)
            self.labda_s = psi_s / self.chi_s - 1

    def __call__(self, Z: float) -> float:
        if 0 <= Z <= 1:  # pre-fracture, pre "split"
            return self.chi * Z * (1 + self.labda * Z + self.mu * Z**2)
        elif 1 < Z <= self.Z_k:  # post fracture, after "split"
            return self.chi_s * Z * (1 + self.labda_s * Z)

        raise ValueError(f"psi(Z) is defined in [0, {self.Z_k}]")


def non_perf(length: float, width: float, height: float) -> FormFunction:
    # sort values in ascending order
    e_1, b, c = (0.5 * v for v in sorted([length, width, height]))
    alpha, beta = e_1 / b, e_1 / c

    return FormFunction(
        chi := 1 + alpha + beta,
        labda=-(alpha + beta + alpha * beta) / chi,
        mu=alpha * beta / chi,
    )


def single_perf(length: float, arch_width: float) -> FormFunction:
    # effectively the case for above where width = +inf
    e_1, c = (0.5 * v for v in (arch_width, length))
    beta = e_1 / c
    return FormFunction(chi=1 + beta, labda=-beta / (1 + beta), mu=0)


def multi_perf(
    length: float,
    arch_width: float,
    perforation_diameter: float,
    n_perforation: int = 7,
    shape: str = CYLINDER,
) -> FormFunction:

    d_0 = perforation_diameter
    e_1, c = 0.5 * arch_width, 0.5 * length
    beta = e_1 / c
    n = n_perforation
    rho_base = e_1 + 0.5 * d_0

    # fmt: off
    perf_dicts: Dict[int, Dict[str, tuple]] = {
        7: {
            CYLINDER: (1, 7, 0, 3 * d_0 + 8 * e_1, 0, 0.2956),
            ROSETTE: (2, 8, 12 * 3**0.5 / pi, d_0 + 4 * e_1, d_0 + 2 * e_1, 0.1547),
        },
        14: {ROSETTE: (8 / 3, 47 / 3, 26 * 3**0.5 / pi, d_0 + 4 * e_1, d_0 + 2 * e_1, 0.1547)},
        19: {
            ROSETTE: (3, 21, 36 * 3**0.5 / pi, d_0 + 4 * e_1, d_0 + 2 * e_1, 0.1547),
            CYLINDER: (1, 19, 0, 5 * d_0 + 12 * e_1, 0, 0.3559),
            HEXAGON: (18 / pi, 19, 18 * (3 * 3**0.5 - 1) / pi, d_0 + 2 * e_1, d_0 + 2 * e_1, 0.1864),
            ROUNDED_HEXAGON: (3**0.5 + 12 / pi, 19, 3 - 3**0.5 + 12 * (4 * 3**0.5 - 1) / pi, d_0 + 2 * e_1, d_0 + 2 * e_1, 0.1977)
        },
    }
    # fmt: on

    try:
        A, B, C, b, a, rho_ratio = perf_dicts[n_perforation][shape]

    except IndexError:
        raise ValueError("Supplied perforation and shape information not found.")

    rho = rho_ratio * rho_base
    Pi = (A * b + B * d_0) / (2 * c)
    Q = (C * a**2 + A * b**2 - B * d_0**2) / (2 * c) ** 2

    labda = beta * (n - 1 - 2 * Pi) / (Q + 2 * Pi)
    if labda < 0:
        raise ValueError(
            "Short multi-perforated grains will combust regressively, this case is not well modeled.",
        )

    return FormFunction(
        chi=beta * (Q + 2 * Pi) / Q,
        labda=labda,
        mu=beta**2 * (1 - n) / (Q + 2 * Pi),
        Z_k=(e_1 + rho) / e_1,
    )


if __name__ == "__main__":
    # print(non_perf(1, 1, 1)(1))
    f = multi_perf(5.5 * 2, 2, 1)
    print(f)
    print(1, f(1))
    print(f.Z_k, f(f.Z_k))

    for i in range(200):
        Z = f.Z_k * i / 199
        print(Z, f(Z))
