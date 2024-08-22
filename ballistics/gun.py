from __future__ import annotations

from bisect import bisect, insort
from dataclasses import dataclass
from functools import cached_property, wraps
from math import ceil, inf, pi
from typing import Callable, Dict, Iterable, List, Tuple

from tabulate import tabulate

from . import (DEFAULT_GUN_IGNITION_PRESSURE, DEFAULT_GUN_START_PRESSURE,
               DFEAULT_GUN_LOSS_FRACTION, MAX_DT, Significance)
from .charge import Charge
from .num import Find, dekker, gss
from .state import Delta, State, StateList


@dataclass
class Gun:
    """
    Class that tracks physical properties of the bore (i.e. that are charge-invariant)
    and manages propellant charge.
    """

    caliber: float
    shot_mass: float
    chamber_volume: float
    loss_fraction: float = DFEAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE
    ignition_pressure: float = DEFAULT_GUN_IGNITION_PRESSURE

    def __post_init__(self):
        self._charges = {}

    @cached_property
    def S(self) -> float:
        return 0.25 * self.caliber**2 * pi

    @cached_property
    def l_0(self) -> float:
        return self.chamber_volume / self.S

    @property
    def charge_masses(self) -> Iterable[float]:
        return self._charges.values()

    @property
    def charges(self) -> Iterable[Charge]:
        return self._charges.keys()

    @property
    def total_charge_mass(self) -> float:
        return sum(self.charge_masses)

    @property
    def total_charge_volume(self) -> float:
        return sum(m / c.density for c, m in zip(self.charges, self.charge_masses))

    def get_bomb_state(self) -> State:
        """
        Generate a special state that corresponds to the case where the gun is operated
        as a ballistic bomb, and where all propellants has fully combusted. This
        `ballistic.state.State` is uniquely marked by a `ballistic.Significance.BOMB`
        marker. This state's pressure values represents the maximum possible that can
        be achieved under this loading condition regardless of powder combustion behavior.

        """
        return State(
            gun=self,
            time=0,
            travel=0,
            velocity=0,
            burnup_fractions=tuple(c.Z_k for c in self.charges),
            marker=Significance.BOMB,
        )

    @property
    def bomb_free_fraction(self) -> float:
        ff = 1.0
        for c, w in zip(self.charges, self.charge_masses):
            ff -= c.covolume * w / self.chamber_volume
        return ff

    def gas_energy(self, psi: Tuple[float, ...], v: float) -> float:
        # calculated the average adiabatic index for the gas mixture.
        molar_sum = sum(
            w / c.gas_molar_mass * psi_c
            for c, w, psi_c in zip(self.charges, self.charge_masses, psi)
        )

        if molar_sum == 0.0:
            return 0

        average_Cp, average_Cv = 0.0, 0.0
        for c, w, psi_c in zip(self.charges, self.charge_masses, psi):
            adiabatic_index = c.adiabatic_index
            molar_fraction = (w / c.gas_molar_mass * psi_c) / molar_sum
            average_Cp += molar_fraction * (adiabatic_index) / (adiabatic_index - 1)
            average_Cv += molar_fraction / (adiabatic_index - 1)

        theta = average_Cp / average_Cv - 1
        return sum(
            c.force * w * psi_c
            for c, w, psi_c in zip(self.charges, self.charge_masses, psi)
        ) - (0.5 * theta * self.phi * self.shot_mass * v**2)

    def incompressible_fraction(self, psi: Tuple[float, ...]) -> float:
        i_f = 0.0
        for c, w, psi_c in zip(self.charges, self.charge_masses, psi):
            delta_c = w / self.chamber_volume
            i_f += (1 - psi_c) * delta_c / c.density + c.covolume * psi_c * delta_c

        return i_f

    @property
    def phi(self) -> float:
        return 1 + self.loss_fraction + self.total_charge_mass / (3 * self.shot_mass)

    def dt(self, state: State) -> Delta:
        P = state.average_pressure
        dZ = tuple(c.dZdt(P) for Z, c in zip(state.burnup_fractions, self.charges))
        return Delta(
            d_time=1,
            d_travel=state.velocity if state.is_started else 0,
            d_velocity=(
                self.S * P / (self.phi * self.shot_mass) if state.is_started else 0
            ),
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
        self,
        state: State,
        dt=...,
        dl=...,
        dv=...,
        marker: Significance = Significance.STEP,
    ) -> State:
        s_i = state.increment

        if dt != ...:
            df, dx = self.dt, dt
        elif dl != ...:
            df, dx = self.dl, dl
        elif dv != ...:
            df, dx = self.dv, dv
        else:
            raise ValueError("at least one of `dv, dt, dl` must be specified.")

        def generate_dargs(value: float):
            return {
                "dt": value if dt != ... else ...,
                "dl": value if dl != ... else ...,
                "dv": value if dv != ... else ...,
            }

        intermediate: Dict[str, Significance] = {"marker": Significance.INTERMEDIATE}

        k1 = df(state)
        k2 = df(s_i(d=0.5 * k1 * dx, **{**generate_dargs(0.5 * dx), **intermediate}))
        k3 = df(s_i(d=0.5 * k2 * dx, **{**generate_dargs(0.5 * dx), **intermediate}))
        k4 = df(s_i(d=k3 * dx, **{**generate_dargs(dx), **intermediate}))
        return s_i(
            d=(k1 + k2 * 2 + k3 * 2 + k4) * dx / 6, **generate_dargs(dx), marker=marker
        )

    def set_charge(self, charge: Charge, mass: float):
        self._charges[charge] = mass

    def pop_charge(self, charge: Charge) -> float:
        """
        Remove a `ballistic.charge.Charge` from a gun's load, and return the corresponding
        mass of the charge.
        """
        return self._charges.pop(charge, 0.0)

    def set_ignition_charge(self, force: float, mass: float):
        """
        Calculate the pressure generated by the ignition charge, and set the
        `gun.ignition_pressure` parameter.

        Parameters
        ----------
        force: float
            the propellant force of the ignition charge.
        mass: float
            the charge mass of the ignition charge.
        """
        delta_ig = mass / (self.chamber_volume - self.total_charge_volume)
        self.ignition_pressure = force * delta_ig

    def to_start(self, n_intg: int, acc: float) -> StateList:
        # sanity check: maximum possible pressure developed is higher than start:
        if self.get_bomb_state().average_pressure < self.ignition_pressure:
            raise ValueError(
                "projectile cannot be started, the maximum pressure achievable is less\
 insufficient to overcome starting resistance."
            )

        delta_t, rough_ttb = MAX_DT, 0.0
        states = StateList()

        while len(states) < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg

            s_next = State(
                gun=self,
                time=0,
                travel=0,
                velocity=0,
                burnup_fractions=tuple(0 for _ in self.charges),
                marker=Significance.IGNITION,
                is_started=False,
            )

            states = StateList([s_next])
            while s_next.average_pressure < self.start_pressure:
                states.append(s_now := s_next)
                s_next = self.propagate_rk4(state=s_now, dt=delta_t)

            rough_ttb = s_next.time

        def state_at_time(
            time: float, marker: Significance = Significance.INTERMEDIATE
        ) -> State:
            return self.propagate_rk4(state=s_now, dt=time - s_now.time, marker=marker)

        start_time = dekker(
            f=lambda t: state_at_time(t).average_pressure - self.start_pressure,
            x_0=s_now.time,
            x_1=s_next.time,
            tol=rough_ttb * acc,
        )[0]

        s_start = state_at_time(time=start_time, marker=Significance.IGNITION)
        states.append(s_start)

        return states

    def to_burnout(
        self,
        n_intg: int,
        acc: float,
        abort_velocity: float = inf,
        abort_travel: float = inf,
    ) -> StateList:
        """
        Integrates projectile motion up to the propellant burnout point and returns
        a List of State.

        Parameters
        ----------
        n_intg: int
            minimum number of integration steps that is to be taken from shot start
            to charge burnout.
        acc: float
            relative accuracy characteristic points (burnout and peak) will be
            determined to in relation to the process's total time. Also controls
            the accuracy to which initial burnup is solved to.
        abort_travel, abort_velocity: float
            additional criterias to abort the calculation before burnout point is
            reached.

        Returns
        -------
        list of `ballistics.state.State`.

        Notes
        -----
        Implementation wise, the adaptive stepsize is first seeded with a
        value from module wide constant `ballistics.MAX_DT`, integrated until
        post burnout, or after the abort conditionals (travel or velocity) have been
        exceeded. The total time of which is used as a better approximate to
        time-to-burnout (or abort), divided by `n_intg` as the step size for the next run.
        This is repeated until at least `n_intg` steps were taken (including the
        initial step, and the post-burnout/abort step).

        In the burnout case, the last two steps brackets the actual burnout point,
        from which `ballistics.num.dekker` is called to numerically find the burnout
        point to an accuracy of `acc` times the approximate total time.

        In the abort case, the behavior is the same as the above, but the point
        of abort is found and marked with `ballistics.Significance.MUZZLE` instead.

        In either case, the result is passed through `Gun.mark_max_pressure` to mark
        the peak pressure point.
        """

        pre_start_states = self.to_start(n_intg=n_intg, acc=acc)
        Z_c0 = max(pre_start_states).burnup_fractions

        def burnout(state: State) -> int:
            return all(Z >= c.Z_k for Z, c in zip(state.burnup_fractions, self.charges))

        def abort(state: State) -> bool:
            return state.travel > abort_travel or state.velocity > abort_velocity

        states = StateList()
        delta_t = MAX_DT
        rough_ttb = 0.0
        while len(states) < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg
            states = StateList()
            s_next = State(
                gun=self,
                time=0.0,
                travel=0.0,
                velocity=0.0,
                burnup_fractions=Z_c0,
                marker=Significance.START,
            )

            while not (burnout(s_next) or abort(s_next)):
                states.append(s_now := s_next)
                s_next = self.propagate_rk4(state=s_now, dt=delta_t)

            rough_ttb = s_next.time

        def time_end(time: float) -> float:
            s = self.propagate_rk4(state=s_now, dt=time - s_now.time)
            return -1 if (burnout(s) or abort(s)) else 1

        end_time = max(
            dekker(f=time_end, x_0=s_now.time, x_1=s_next.time, tol=rough_ttb * acc)
        )

        s_end = self.propagate_rk4(state=s_now, dt=end_time - s_now.time)
        if burnout(s_end):
            s_burnout = State.remark(s_end, new_significance=Significance.BURNOUT)
            states.append(s_burnout)
        else:
            s_muzzle = State.remark(s_end, new_significance=Significance.MUZZLE)
            states.append(s_muzzle)

        return self.mark_max_pressure(states=states, acc=acc)

    def to_travel(self, travel: float, n_intg: int, acc: float) -> StateList:
        """
        Conducts integration up to the desired shot-travel using length-wise ODE, if
        the travel is greater than burnout point. Otherwise, length-wise ODE is used
        to single-step from the last point before the specified travel.

        Parameters
        ----------
        travel: float
            the projectile travel to which the integration is done to.
        n_intg, acc: int, float
            see documentation for `Gun.to_burnout`.

        Returns
        -------
        list of `ballistics.state.State`.

        """

        states = self.to_burnout(n_intg=n_intg, acc=acc, abort_travel=travel)

        if states.has_state_with_marker(Significance.BURNOUT):

            state = max(states)
            d_travel = (travel - state.travel) / n_intg
            for _ in range(n_intg - 1):
                states.append(state := self.propagate_rk4(state=state, dl=d_travel))

            states.append(
                self.propagate_rk4(state=state, dl=d_travel, marker=Significance.MUZZLE)
            )

        else:
            """
            the case where `to_burnout` has aborted less than a single step
            to the targeted projectile travel:
            """
            return states

        return self.mark_max_pressure(states=states, acc=acc)

    def to_velocity(self, velocity: float, n_intg: int, acc: float) -> StateList:
        """
        Conducts integration up to the desired velocity using velocity-wise ODE
        from burnout point to muzzle exit. Calls `.to_burnout` for integration up
        to the burnout point.
        Parameters
        ----------
        velocity: float
            the projectile velocity to which the integration is done to.
        n_intg, acc: int, float
            see documentation for `Gun.to_burnout`.

        Returns
        -------
        list of `ballistics.state.State`.

        """

        states = self.to_burnout(n_intg=n_intg, acc=acc, abort_velocity=velocity)

        if states.has_state_with_marker(Significance.BURNOUT):
            state = max(states)
            d_velocity = (velocity - state.velocity) / n_intg
            for _ in range(n_intg - 1):
                states.append(state := self.propagate_rk4(state=state, dv=d_velocity))

            states.append(
                self.propagate_rk4(
                    state=state, dv=d_velocity, marker=Significance.MUZZLE
                )
            )

        else:
            """
            the case where `to_burnout` has aborted less than a single step
            to the targeted projectile travel:
            """
            return states

        return self.mark_max_pressure(states=states, acc=acc)

    def mark_max_pressure(self, states: StateList, acc: float) -> StateList:
        """
        Finds the maximum pressure point and insert it into a list of
        `ballistics.state.State`, passed in as argument.

        Notes
        -----
        Implementation wise, conducts a gold-section search using `ballistics.num.gss`
        in the interval bracketed by the step before and after the step where maximum
        pressure is recorded. By intercepting the accuracy specification passed to the
        generating functions, the peak-pressure point is determined to (at worst) step size
        times `acc`.

        If a previous round of peak pressure finding is recognized (by the presence
        of the `ballistics.Significance.PEAK_PRPESSURE` marker).
        """
        if not any(s.marker == Significance.PEAK_PRESSURE for s in states):
            total_time = max(states).time - min(states).time
            pressures = [s.average_pressure for s in states]
            j = pressures.index(max(pressures))

            # find the bracketing points.
            i, k = max(j - 1, 0), min(j + 1, len(states) - 1)

            s_i, s_j, s_k = states[i], states[j], states[k]

            def time_pressure(time: float) -> float:
                return self.propagate_rk4(
                    state=s_j, dt=time - s_j.time
                ).average_pressure

            # conduct gss on (time_min, time_max)
            time_pmax = (
                sum(
                    gss(
                        f=time_pressure,
                        x_0=s_i.time,
                        x_1=s_k.time,
                        find=Find.MAX,
                        tol=acc * total_time,
                    )
                )
                * 0.5
            )
            s_pmax = self.propagate_rk4(
                state=s_j,
                dt=time_pmax - s_j.time,
                marker=Significance.PEAK_PRESSURE,
            )

            # if s_i.average_pressure > s_pmax.average_pressure:
            #     s_pmax = State.remark(s_i, Significance.PEAK_PRESSURE)
            # elif s_j.average_pressure > s_pmax.average_pressure:
            #     s_pmax = State.remark(s_j, Significance.PEAK_PRESSURE)

            insort(states, s_pmax)
        return states

    @staticmethod
    def tabulate(
        states: StateList,
        *args,
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
        **kwargs,
    ) -> str:
        """
        Generates a plain, tabulated view of data for a list of
        `ballistics.state.State` objects.

        Parameters
        ----------
        states: list of `ballistics.state.State`
            the list of `ballistics.state.State` to be pretty-printed.
        headers: tuple[str]
            argument passed to `tabulate.tabulate()` to generate a header for the
            table.
        *args, **kwargs:
            other positional and named arguments to be passed to `tabulate.tabulate()`,
            after the aforementioned once, respectively.

        Returns
        -------
        str
            generated using `tabulate.tabulate()`.

        Notes
        -----
        see documentation for [tabulate.tabulate](https://pypi.org/project/tabulate/)
        for information on additional arguments.
        """
        return tabulate(
            [
                (
                    state.marker.value,
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
            *args,
            **{**{"headers": headers}, **kwargs},  # feeds additional arguments
        )
