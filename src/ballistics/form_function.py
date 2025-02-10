from __future__ import annotations

from enum import Enum
from functools import cached_property
from math import pi
from typing import Tuple

from attrs import field, frozen


class MultiPerfShape(Enum):
    # fmt: off
    SEVEN_PERF_CYLINDER = ("cylinder", 7, 1, 7, 0, (3, 8), (0, 0), 0.2956)
    SEVEN_PERF_ROSETTE = ("rosette", 7, 2, 8, 12 * 3**0.5 / pi, (1, 4), (1, 2), 0.1547)
    FOURTEEN_PERF_ROSETTE = ("rosette", 14, 8 / 3, 47 / 3, 26 * 3**0.5 / pi, (1, 4), (1, 2), 0.1547)
    NINETEEN_PERF_ROSETTE = ("rosette", 19, 3, 21, 36 * 3**0.5 / pi, (1, 4), (1, 2), 0.1547)
    NINETEEN_PERF_CYLINDER = ("cylinder", 19, 1, 19, 0, (5, 12), (0, 0), 0.3559)
    NINETEEN_PERF_HEXAGON = (
        "hexagon", 19, 18 / pi, 19, 18 * (3 * 3**0.5 - 1) / pi, (1, 2), (1, 2), 0.1864,
    )
    NINETEEN_PERF_ROUNDED_HEXAGON = (
        "rounded hexagon", 19, 3**0.5 + 12 / pi, 19, 3 - 3**0.5 + 12 * (4 * 3**0.5 - 1) / pi,
        (1, 2), (1, 2), 0.1977
    )
    # fmt: on

    def describe(self) -> str:
        desc, n, *_ = self.value
        return f"{n}-perforated {desc}"

    def __call__(self, d_0: float, e_1: float) -> Tuple[str, int, float, float, float, float, float, float]:
        desc, n, A, B, C, b_factors, a_factors, rho_ratio = self.value

        return (
            desc,
            n,
            A,
            B,
            C,
            sum(v * f for v, f in zip((d_0, e_1), b_factors)),
            sum(v * f for v, f in zip((d_0, e_1), a_factors)),
            rho_ratio,
        )


@frozen(kw_only=True)
class FormFunction:
    """form function relates the volumetric burnup-ratio to the linear (depth-wise)
    burnup ratio, usually denoted psi and Z, respectively.

    Parameters
    ----------
    chi, labda, mu : float
        coefficient of the shape function before propellant fracture, in the form of
        a 3rd-order polynomial:
        ```
        psi(Z) = chi * Z * (1 + labda * Z + mu * Z**2), Z in [0, 1]
        ```
        these are considered exact under ideal parallel combustion assumptions.
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
        this is an approximate fit to result in the correct volume burnup at fracture
        and burnout points.


    Methods
    -------
    non_perf(length, width, height)
        classmethod that generates a form function for non-perforated propellant shapes.
    single_perf(arch_width, height)
        classmethod that generates a form function for single-perforated propellant shapes.
    multi_perf(arch_width, perforation_diameter, height, n_perforations, shape)
        classmethod that generates a form function for multiple-perforated propellant shapes.

    Notes
    -----
    Form funciton applies not only to propellant geometry described by parameters but
    also all shapes that are similar. The required parameters are best thought of as
    characteristic ratios.

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

    name: str = field(default="")
    description: str = field(default="")
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

        raise ValueError(f"psi(Z) is defined in [0, {self.Z_k}], but called with Z = {Z}")

    def sigma(self, Z: float) -> float:
        if 0 <= Z <= 1:  # pre-fracture
            return self(Z) / self.chi
        elif 1 < Z <= self.Z_k:  # post fracture
            return self(Z) / self.chi_s

        raise ValueError(f"sigma(Z) is defined in [0, {self.Z_k}]")

    def pretty_print(self) -> str:
        return "\n".join(
            (
                f"{self.name}",
                f"{self.description}",
                f"    chi {self.chi:.4f}",
                f"  labda {self.labda:.4f}",
                f"     mu {self.mu:.4f}",
                f"  chi_s {self.chi_s:.4f}",
                f"labda_s {self.labda_s:.4f}",
            )
        )

    @classmethod
    def non_perf(cls, length: float, width: float, height: float) -> FormFunction:
        """
        form function that describes:
        - **right square-prism**, commonly described as stick, tape or flake.
        - **right cylinder**, including those that are elliptic.
        - **sphere**, including those that are oblonged.
        shaped propellants.

        Parameters
        ----------
        length, width, height: float
            parameters that describes the supplied shape. For each shape, the supplied
            parameters are interpreted as specifying the below. no particular order is
            required.


            | shapes                    | parameters interpretation     |
            | --------------------------| ------------------------------|
            | right square prism        | length, width & height        |
            | right (elliptic) cylinder | two axes of the ends & height |
            | (oblonged) sphere         | three axes of an ellipsoid    |

        Notes
        -----
        The only real requirement on the shape being described is that it combusts
        in a self-similar fashion, with the center-of-volume staying constant.
        The listed shapes *should* cover most shapes that saw adoption as service
        propellants in the smokeless era.

        """
        # sort values in ascending order
        e_1, b, c = (0.5 * v for v in sorted([length, width, height]))
        alpha, beta = e_1 / b, e_1 / c
        chi = 1 + alpha + beta
        return cls(
            name="grain",
            description=f"{e_1*2:.1f} x {b*2:.1f} x {c*2:.1f} mm",
            chi=chi,
            labda=-(alpha + beta + alpha * beta) / chi,
            mu=alpha * beta / chi,
        )

    @classmethod
    def single_perf(cls, arch_width: float, height: float) -> FormFunction:
        """
        form function that describes **right hollow cylinder** shaped propellants,
        colloquially referred to as tubular grains.

        Parameters
        ----------
        arch_width: float
            the width of the arch, or the distance between the inner and outer
            surface of the cylinder, also the difference between the radius
            of the inner and outer surface.
        height: float
            the length of the propellant, or the distance between the two ends
        """
        # effectively the case for above where width = +inf
        e_1, c = (0.5 * v for v in (arch_width, height))
        beta = e_1 / c
        return cls(
            name="tube",
            description=f"{e_1*2:.1f} / 1 - {c*2:.1f} mm",
            chi=1 + beta,
            labda=-beta / (1 + beta),
            mu=0,
        )

    @classmethod
    def multi_perf(
        cls,
        arch_width: float,
        perforation_diameter: float,
        height: float,
        shape: MultiPerfShape,
    ) -> FormFunction:
        """
        form function that describes multiple perforated propellants of specified shape.

        Parameters
        ----------
        arch_width: float
            the width of the arch, or the distance between the centers of two adjacent
            perforations, substracting the perforation diameter.
        height: float
            the length of the propellant, or the distance between the two ends.
        n_perforations: int
            the number of perforations.
        shape: `MultiPerfShape`
            the shape of the multi-perforated propellant.

        """

        d_0 = perforation_diameter
        e_1, c = 0.5 * arch_width, 0.5 * height
        beta = e_1 / c
        # n = n_perforations
        rho_base = e_1 + 0.5 * d_0

        desc, n, A, B, C, b, a, rho_ratio = shape(d_0=d_0, e_1=e_1)
        rho = rho_ratio * rho_base
        Pi = (A * b + B * d_0) / (2 * c)
        Q = (C * a**2 + A * b**2 - B * d_0**2) / (2 * c) ** 2

        labda = beta * (n - 1 - 2 * Pi) / (Q + 2 * Pi)
        if labda < 0:
            raise ValueError(
                "Short multi-perforated grains will combust regressively, this case is not well\
 modeled.",
            )

        return cls(
            name=f"{n} perf {desc}",
            description=f"{e_1*2:.1f} / {n} (d = {d_0:.1f}) - {c*2:.1f} mm",
            chi=beta * (Q + 2 * Pi) / Q,
            labda=labda,
            mu=beta**2 * (1 - n) / (Q + 2 * Pi),
            Z_k=(e_1 + rho) / e_1,
        )


if __name__ == "__main__":
    f = FormFunction.multi_perf(5.5 * 2, 2, 1, shape=MultiPerfShape.SEVEN_PERF_CYLINDER)
    print(f)
    print(1, f(1))
    print(f.Z_k, f(f.Z_k))

    for i in range(200):
        Z = f.Z_k * i / 199
        print(Z, f(Z))
