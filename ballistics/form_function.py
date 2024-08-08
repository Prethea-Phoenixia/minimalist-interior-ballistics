from __future__ import annotations
from typing import Dict
from dataclasses import dataclass
from math import pi
from functools import cached_property

CYLINDER = "cylinder"
ROSETTE = "rosette"
HEXAGON = "hexagon"
ROUNDED_HEXAGON = "rounded hexagon"


@dataclass(frozen=True)
class FormFunction:
    """form function relates the volumetric burnup-ratio to the linear (depth-wise)
    burnup ratio, usually denoted psi and Z, respectively.

    Parameters
    ----------
    chi, labda, mu : float
        coefficient of the shpe function before propellant fracture, in the form of
        a 3rd-order polynomial:
        ```
        psi(Z) = chi * Z * (1 + labda * Z + mu * Z**2), Z in [0, 1]
        ```
        This is exact for all shapes supported in this module, pre-burnout.

    Z_k : float
        denotes the end of combustion point as expressed in linear (depth-wise) burnup
        ratio. This is always 1.0 except for multiple-perforated grains, where small
        "slivers" of grain continue to combust after the propellant has "fractured",
        or the web has been totally consumed. In that case, the slivers' combustion
        behavior is approximated with simple shapes of equivalent volume, and Z_k is
        extended accordingly to greater than unity.

    Attributes
    ----------
    psi_s: float
        the volumetric burnup at the time of propellant fracture.
    chi_s, labda_s : float
        coefficient of the shape function after propellant fracture, in the form of
        a 2nd-order polynomial:
        ```
        psi(Z) = chi_s * Z * (1 + labda * Z), Z in [1, Z_k],
        s.t. psi(1) = psi_s and psi(Z_k) = 1
        ```
        This is an approximate fit to result in the correct volume burnup at fracture
        and burnout points.

    Notes
    -----
    Subscripts are kept in-line with those used by M.E.Serebryakov and in common
    circulation within Soviet-sphere ballistic community, which was the convention
    in effect for interior balistics works of the 1980s in China. `k` (likely comes from
    *komplett*, "complete, with everything included" in German) is used to indicate
    the point of complete combustion, whereas `s` (for various Germanic word meaning
    "sliver" or "splinter", *schiefer* or *splitter*) denotes values at fracture point.

    References
    ----------
    - **[English]** Mekrassoff, V.A., An Abridged Translation of
    M.E.Serebryakov's "Interior Ballistics", originally published in Moscow, 1949,
    *Defense Technical Information Center*, AD0059622,
    [available online](https://apps.dtic.mil/sti/tr/pdf/AD0059622.pdf).
    - **[中文]** 张小兵，金志明（2014）枪炮内弹道学，北京理工大学出版社，第一章1.3小节
    """

    chi: float
    labda: float
    mu: float
    Z_k: float = 1.0

    @cached_property
    def psi_s(self):
        return self(1)

    @cached_property
    def chi_s(self) -> float:
        if self.Z_k > 1:
            return (1 - self.psi_s * self.Z_k**2) / (self.Z_k - self.Z_k**2)
        else:
            return 0

    @cached_property
    def labda_s(self) -> float:
        if self.Z_k > 1:
            return self.psi_s / self.chi_s - 1
        else:
            return 0

    def __call__(self, Z: float) -> float:
        if 0 <= Z <= 1:  # pre-fracture
            return self.chi * Z * (1 + self.labda * Z + self.mu * Z**2)
        elif 1 < Z <= self.Z_k:  # post fracture
            return self.chi_s * Z * (1 + self.labda_s * Z)

        raise ValueError(f"psi(Z) is defined in [0, {self.Z_k}]")

    def sigma(self, Z: float) -> float:
        if 0 <= Z <= 1:  # pre-fracture
            return self(Z) / self.chi
        elif 1 < Z <= self.Z_k:  # post fracture
            return self(Z) / self.chi_s

        raise ValueError(f"sigma(Z) is defined in [0, {self.Z_k}]")


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
