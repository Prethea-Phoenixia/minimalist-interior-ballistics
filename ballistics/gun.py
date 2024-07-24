from __future__ import annotations
from dataclasses import dataclass
from typing import List, Callable, Any, Optional, Dict, Union
from math import pi
from bisect import insort
from functools import wraps, cached_property

from . import START, PEAK_PRESSURE, BURNOUT, MUZZLE, INTERMEDIATE, STEP
from . import MAX_DT

from .dekker import dekker
from .gss import gss, FIND_MAX
from .state import State
from .delta import Delta
from .charge import Charge

from tabulate import tabulate


def mark_max_pressure(state_generating_func: Callable) -> Callable:
    """
    decorator that finds the maximum pressure point and insert it into the list of
    `ballistics.state.State` sorted by time, given a list-of-`ballistics.state.State`
    generating function.

    Notes
    -----
    Implementation wise, conducts a gold-section search using `ballistics.gss.gss`
    in the interval bracketed by the step before and after the step where maximum
    pressure is recorded. By intercepting the accuracy specification passed to the
    generating functions, the peak-pressure point is determined to (at worst) step size
    times `acc`.
    """

    @wraps(state_generating_func)
    def wrapper(self, *args, acc, **kwargs):
        states = state_generating_func(self, *args, acc=acc, **kwargs)

        pressures = [s.average_pressure for s in states]
        j = pressures.index(max(pressures))
        s_pmax = states[j]

        i, k = max(j - 1, 0), min(j + 1, len(states) - 1)
        time_min, time_max = states[i].time, states[k].time

        def time_pressure(time: float) -> float:
            return self.propagate_rk4(
                state=s_pmax, dt=time - s_pmax.time
            ).average_pressure

        time_pmax = gss(
            f=time_pressure,
            x_0=time_min,
            x_1=time_max,
            find=FIND_MAX,
            tol=acc * (time_max - time_min) / (k - i),
        )

        s_pmax = self.propagate_rk4(
            state=s_pmax, dt=time_pmax - s_pmax.time, marker=PEAK_PRESSURE
        )
        insort(states, s_pmax)

        return states

    return wrapper


@dataclass
class Gun:
    """class that tracks physical properties of the bore (i.e. that are charge-invariant)
    and manages propellant charge."""

    caliber: float
    shot_mass: float
    chamber_volume: float
    loss_fraction: float = 0.05
    start_pressure: float = 30e6

    def __post_init__(self):
        self.charges = []

    @cached_property
    def S(self):
        return 0.25 * self.caliber**2 * pi

    @cached_property
    def l_0(self):
        return self.chamber_volume / self.S

    def add_charge(self, *args, **kwargs):
        self.charges.append(Charge(gun=self, *args, **kwargs))
        self.total_charge_mass = sum(c.charge_mass for c in self.charges)

        # calculate the average adiabatic index
        molar_sum = sum(c.charge_mass / c.gas_molar_mass for c in self.charges)
        average_Cp = 0
        average_Cv = 0
        for c in self.charges:
            adiabatic_index = c.adiabatic_index
            molar_fraction = (c.charge_mass / c.gas_molar_mass) / molar_sum
            average_Cp += molar_fraction * (adiabatic_index) / (adiabatic_index - 1)
            average_Cv += molar_fraction / (adiabatic_index - 1)

        self.average_adiabatic_index = average_Cp / average_Cv

        # calculation variables
        self.phi = (
            1 + self.loss_fraction + self.total_charge_mass / (3 * self.shot_mass)
        )

    # @mark_max_pressure
    def to_burnout(self, n_intg: int, acc: float) -> List[State]:
        """integrates projectile motion up to the propellant burnout point and returns
        a List of State.

        Parameters
        ----------
        n_intg: int
            number of integration steps that is to be taken from shot start to charge
            burnout.

        acc: float
            relative accuracy characteristic points (burnout and peak) will be
            determined to in relation to actual step size.

        Returns
        -------
        list of `ballistics.state.State`

        Notes
        -----
        Implementation wise, the adaptive stepsize is first seeded with a
        value from module wide constant `ballistics.MAX_DT`, integrated until burnout,
        the total time of which is used as a better approximate to time-to-burnout,
        divided by `n_intg` as the step size for the next run. This is repeated
        until at least `n_intg` steps were taken. This ensures the final two steps
        brackets the actual burnout point, from which `ballistics.dekker.dekker`
        is called to numerically find the burnout point to an accuracy of stepsize times
        `acc`.
        """
        Z_c0 = tuple(c.solve_bomb() for c in self.charges)

        def burnout(state: State) -> float:
            if sum(Z - c.Z_k for Z, c in zip(state.burnup_fractions, self.charges)) < 0:
                return -1
            else:
                return 1

        states: List[State] = []
        delta_t = MAX_DT
        rough_ttb = 0.0
        while len(states) < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg
            states = []
            s_next = State(
                gun=self,
                time=0.0,
                travel=0.0,
                velocity=0.0,
                burnup_fractions=Z_c0,
                marker=START,
            )
            while burnout(s_next) < 0:
                s_now = s_next
                states.append(s_now)
                s_next = self.propagate_rk4(state=s_now, dt=delta_t)

            rough_ttb = s_next.time

        tol_t = delta_t * acc

        def time_burnout(time: float) -> float:
            return burnout(self.propagate_rk4(state=s_now, dt=time - s_now.time))

        burnout_time = dekker(
            f=time_burnout, x_0=s_now.time, x_1=s_next.time, tol=tol_t
        )[0]
        s_burnout = self.propagate_rk4(
            state=s_now, dt=burnout_time - s_now.time, marker=BURNOUT
        )
        states.append(s_burnout)
        return states

    def to_travel(self, travel: float, n_intg: int, acc: float) -> List[State]:
        """conducts integration up to the desired shot-travel using length-wise ODE
        from burnout point to muzzle exit. Calls `.to_burnout` for integration up
        to the burnout point.
        Parameters
        ----------
        travel: float
            the projectile travel to which the integration is done to. Does not accept
            a value that results in muzzle exit before burnout.
        n_intg: int
            determines the number of steps taken in the length-wise integration,
            in addition to being passed through to `to_burnout`.
        acc: float
            see documentation for `to_burnout`.

        Returns
        -------
        list of `ballistics.state.State`

        """
        states = self.to_burnout(n_intg=n_intg, acc=acc)
        s_burnout = states[-1]

        d_travel = (travel - s_burnout.travel) / n_intg

        if d_travel < 0:
            raise ValueError("travel is breech-ward of burnout point.")

        state = s_burnout
        for _ in range(n_intg - 1):
            states.append(state := self.propagate_rk4(state=state, dl=d_travel))

        states.append(
            state := self.propagate_rk4(state=state, dl=d_travel, marker=MUZZLE)
        )

        return states

    def to_velocity(self, velocity: float, n_intg: int, acc: float) -> List[State]:
        """conducts integration up to the desired velocity using velocity-wise ODE
        from burnout point to muzzle exit. Calls `.to_burnout` for integration up
        to the burnout point.
        Parameters
        ----------
        velocity: float
            the projectile velocity to which the integration is done to. Does not accept
            a value that results in muzzle exit before burnout.
        n_intg: int
            determines the number of steps taken in the length-wise integration,
            in addition to being passed through to `to_burnout`.
        acc: float
            see documentation for `to_burnout`.

        Returns
        -------
        list of `ballistics.state.State`

        """

        states = self.to_burnout(n_intg=n_intg, acc=acc)
        s_burnout = states[-1]

        d_velocity = (velocity - s_burnout.velocity) / n_intg

        if d_velocity < 0:
            raise ValueError("velocity is lower than at burnout point.")

        state = s_burnout
        for _ in range(n_intg - 1):
            states.append(state := self.propagate_rk4(state=state, dv=d_velocity))

        states.append(
            state := self.propagate_rk4(state=state, dv=d_velocity, marker=MUZZLE)
        )

        return states

    @staticmethod
    def prettyprint(states: List[State]) -> str:
        """
        generates a plain, tabulated view of data for a list of
        `ballistics.state.State` objects.

        Parameters
        ----------
        states: list of `ballistics.state.State`

        Returns
        -------
        str
            generated using `tabulate.tabulate()`
        """
        return tabulate(
            [
                (
                    state.marker,
                    state.time * 1e3,
                    state.travel,
                    state.velocity,
                    state.breech_pressure * 1e-6,
                    state.average_pressure * 1e-6,
                    state.shot_pressure * 1e-6,
                    state.volume_burnup_fractions,
                )
                for state in states
            ],
            headers=(
                "significance",
                "time\nms",
                "travel\nm",
                "velocity\nm/s",
                "breech\npressure\nMPa",
                "average\npressure\nMPa",
                "shot\npressure\nMPa",
                "volume\nburnup\nfractions",
            ),
        )

    def dt(self, state: State) -> Delta:
        P = state.average_pressure
        dZ = tuple(
            c.dZdt(P) if Z < c.Z_k else 0
            for Z, c in zip(state.burnup_fractions, self.charges)
        )
        return Delta(
            d_time=1,
            d_travel=state.velocity,
            d_velocity=self.S * P / (self.phi * self.shot_mass),
            d_burnup_fractions=dZ,
        )

    def dl(self, state: State) -> Delta:
        # d/dl = d/dt * dt/dl
        # dt / dl = 1/v
        v = state.velocity
        dt = self.dt(state)

        return dt / v

    def dv(self, state: State) -> Delta:
        # d / dv = d/dt * dt/dv
        dt = self.dt(state)
        return dt / dt.d_velocity

    def propagate_rk4(
        self, state: State, dt=..., dl=..., dv=..., marker: str = STEP
    ) -> State:
        s_i = state.increment

        if dt != ...:
            df, dx, d_arg = self.dt, dt, "dt"
        elif dl != ...:
            df, dx, d_arg = self.dl, dl, "dl"
        elif dv != ...:
            df, dx, d_arg = self.dv, dv, "dv"
        else:
            raise ValueError("at least one of `dv, dt, dl` must be specified.")

        def generate_dargs(value: float) -> Dict[str, float]:
            return {d_arg: value}

        k1 = df(state)
        k2 = df(s_i(d=0.5 * k1 * dx, **generate_dargs(0.5 * dx), marker=INTERMEDIATE))
        k3 = df(s_i(d=0.5 * k2 * dx, **generate_dargs(0.5 * dx), marker=INTERMEDIATE))
        k4 = df(s_i(d=k3 * dx, **generate_dargs(dx), marker=INTERMEDIATE))
        return s_i(
            d=(k1 + k2 * 2 + k3 * 2 + k4) * dx / 6, **generate_dargs(dx), marker=marker
        )
