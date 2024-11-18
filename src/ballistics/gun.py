from __future__ import annotations

import json
import logging
from bisect import insort
from functools import cached_property
from math import inf
from typing import Dict, Iterable, List, Optional, Tuple

from attrs import define, field, frozen
from cattrs import Converter

from . import (DEFAULT_ACC, DEFAULT_GUN_LOSS_FRACTION,
               DEFAULT_GUN_START_PRESSURE, DEFAULT_STEPS, MAX_DT, Significance)
from .charge import Charge
from .num import dekker, gss_max
from .state import Delta, State, StateList

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class Gun:
    """
    Class that tracks physical properties of the bore (i.e. that are charge-invariant)
    and manages propellant charge.
    """

    name: str = field(default="")
    description: str = field(default="")
    family: str = field(default="")
    cross_section: float
    shot_mass: float
    charge_mass: float
    chamber_volume: float
    loss_fraction: float = DEFAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE
    travel: float

    charge: Charge

    def to_json(self):
        converter = Converter()
        return converter.unstructure(self)

    @staticmethod
    def from_json(json_dict: Dict) -> Gun:
        converter = Converter()
        return converter.structure(json_dict, Gun)

    @staticmethod
    def to_file(guns: Iterable[Gun], filename: str):
        with open(filename, mode="w", encoding="utf-8") as f:
            json.dump([gun.to_json() for gun in guns], f, ensure_ascii=False, indent="\t")

    @staticmethod
    def from_file(filename: str) -> Tuple[Gun, ...]:
        guns = []
        with open(filename, mode="r", encoding="utf-8") as f:
            for json_dict in json.load(f):
                guns.append(Gun.from_json(json_dict))

        return tuple(guns)

    @cached_property
    def l_0(self) -> float:
        return self.chamber_volume / self.S

    @cached_property
    def S(self) -> float:
        return self.cross_section

    @cached_property
    def delta(self) -> float:
        return self.charge_mass / self.chamber_volume

    @cached_property
    def charge_volume(self) -> float:
        return self.charge_mass / self.charge.density

    @cached_property
    def phi(self) -> float:
        return 1 + self.loss_fraction + self.charge_mass / (3 * self.shot_mass)

    @cached_property
    def bomb_free_fraction(self) -> float:
        return 1 - self.charge.covolume * self.charge_mass / self.chamber_volume

    @cached_property
    def velocity_limit(self) -> float:
        return (
            (2 * self.charge.force * self.charge_mass)
            / (self.charge.theta * self.phi * self.shot_mass)
        ) ** 0.5

    def get_thermal_efficiency(self, velocity: float) -> float:
        return (velocity / self.velocity_limit) ** 2

    def get_ballistic_efficiency(self, velocity: float) -> float:
        return self.get_thermal_efficiency(velocity) / self.phi

    def get_piezoelectric_efficiency(self, velocity: float, peak_average_pressure: float) -> float:
        return (0.5 * self.phi * self.shot_mass * velocity**2) / (
            self.cross_section * self.travel * peak_average_pressure
        )

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
            burnup_fraction=self.charge.Z_k,
            marker=Significance.BOMB,
        )

    def get_start_state(self, *, n_intg: int = DEFAULT_STEPS, acc: float = DEFAULT_ACC) -> State:
        return self.to_start(n_intg=n_intg, acc=acc).get_state_by_marker(
            significance=Significance.START
        )

    def gas_energy(self, *, psi: float, v: float) -> float:
        return (
            self.charge.force * self.charge_mass * psi
            - 0.5 * self.charge.theta * self.phi * self.shot_mass * v**2
        )

    def incompressible_fraction(self, psi: float) -> float:
        return (
            1 - psi
        ) * self.delta / self.charge.density + self.charge.covolume * psi * self.delta

    def dt(self, state: State) -> Delta:
        P = state.average_pressure
        dZ = self.charge.dZdt(P)
        return Delta(
            d_time=1,
            d_travel=state.velocity if state.is_started else 0,
            d_velocity=(self.S * P / (self.phi * self.shot_mass) if state.is_started else 0),
            d_burnup_fraction=dZ,
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
        *,
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
        return s_i(d=(k1 + k2 * 2 + k3 * 2 + k4) * dx / 6, **generate_dargs(dx), marker=marker)

    def to_start(self, *, n_intg: int = DEFAULT_STEPS, acc: float = DEFAULT_ACC) -> StateList:
        # sanity check: maximum possible pressure developed is higher than start:
        if self.get_bomb_state().average_pressure < self.start_pressure:
            raise ValueError(
                "projectile cannot be started, the maximum pressure achievable is less\
 insufficient to overcome starting resistance."
            )

        initial_state = State(
            gun=self,
            time=0,
            travel=0,
            velocity=0,
            burnup_fraction=0,
            marker=Significance.IGNITION,
            is_started=False,
        )

        delta_t, rough_ttb = MAX_DT, 0.0
        states = StateList()

        while len(states) < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg

            s_next = initial_state
            states = StateList([s_next])
            while s_next.average_pressure < self.start_pressure:
                states.append(s_now := s_next)
                s_next = self.propagate_rk4(s_now, dt=delta_t)

            rough_ttb = s_next.time

        def state_at_time(time: float, marker: Significance = Significance.INTERMEDIATE) -> State:
            return self.propagate_rk4(s_now, dt=time - s_now.time, marker=marker)

        start_time = dekker(
            f=lambda t: state_at_time(t).average_pressure - self.start_pressure,
            x_0=s_now.time,
            x_1=s_next.time,
            tol=rough_ttb * acc,
        )[0]

        s_start = state_at_time(time=start_time, marker=Significance.START)
        states.append(s_start)

        return states

    def get_velocity_post_burnout(self, *, burnout_state: State, travel: float) -> float:
        l_k, v_k = burnout_state.travel, burnout_state.velocity
        l_1 = self.l_0 * (1 - self.incompressible_fraction(1))
        v_j = self.velocity_limit
        theta = self.charge.theta
        return (1 - (1 - (v_k / v_j) ** 2) / ((l_1 + travel) / (l_1 + l_k)) ** theta) ** 0.5 * v_j

    def get_travel_post_burnout(self, *, burnout_state: State, velocity: float) -> float:
        l_k, v_k = burnout_state.travel, burnout_state.velocity
        l_1 = self.l_0 * (1 - self.incompressible_fraction(1))
        v_j = self.velocity_limit
        theta = self.charge.theta

        return (l_1 + l_k) * ((1 - (velocity / v_j) ** 2) / (1 - (v_k / v_j) ** 2)) ** (
            -1 / theta
        ) - l_1

    def to_burnout(
        self,
        *,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        abort_velocity: float = inf,
        abort_travel: float = inf,
        logging_preamble: str = "",
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

        In the abort case, the last step is dropped such that the returned
        `ballistics.state.StateList` does not contain any point that exceeds the abort
        criteria, whether travel or velocity.

        In either case, the result is passed through `Gun.mark_max_pressure` to mark
        the peak pressure point.
        """
        start_state = self.get_start_state(n_intg=n_intg, acc=acc)
        Z_c0 = start_state.burnup_fraction

        def burnout(state: State) -> int:
            return state.burnup_fraction > self.charge.Z_k

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
                burnup_fraction=Z_c0,
                marker=Significance.START,
            )

            while not (burnout(s_next) or abort(s_next)):
                states.append(s_now := s_next)
                s_next = self.propagate_rk4(s_now, dt=delta_t)

            rough_ttb = s_next.time

        def time_end(time: float) -> float:
            s = self.propagate_rk4(s_now, dt=time - s_now.time)
            return -1 if (burnout(s) or abort(s)) else 1

        end_time = max(dekker(f=time_end, x_0=s_now.time, x_1=s_next.time, tol=rough_ttb * acc))

        s_end = self.propagate_rk4(s_now, dt=end_time - s_now.time)

        if abort(s_end):
            # abort prioritized in case of both abort and burnout.
            pass
        elif burnout(s_end):
            s_burnout = State.remark(s_end, new_significance=Significance.BURNOUT)
            states.append(s_burnout)

        return self.mark_max_pressure(states, acc=acc, logging_preamble=logging_preamble)

    def to_travel(
        self,
        travel: Optional[float] = None,
        *,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        logging_preamble: str = "",
    ) -> StateList:
        """
        Conducts integration up to the desired shot-travel using time-wise ODE, if
        the travel is greater than burnout point. Then, length-wise ODE is used
        to single-step to the specified travel.

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

        if not travel:
            travel = self.travel

        states = self.to_burnout(n_intg=n_intg, acc=acc, abort_travel=travel)
        state = max(states)

        if states.has_state_with_marker(Significance.BURNOUT):
            burnout_state = states.get_state_by_marker(Significance.BURNOUT)

            # use the analytical function to estimate mv.
            v_muzzle = self.get_velocity_post_burnout(burnout_state=burnout_state, travel=travel)
            v_burnout = burnout_state.velocity

            # estimate the number of steps needed to be taken
            v_average = (v_muzzle + v_burnout) * 0.5
            ttm_est = (travel - burnout_state.travel) / v_average

            """
            use a step size that is the greater of
            > previous step size in `to_burnout`
            > a conservative estimate of the time to muzzle `ttm_est`, divided by `n_intg`.
            """
            dt = max((max(states).time - min(states).time) / len(states), ttm_est / n_intg)

            next_state = self.propagate_rk4(state, dt=dt)

            while next_state.travel < travel:
                states.append(state := next_state)
                next_state = self.propagate_rk4(state, dt=dt)

        states.append(
            self.propagate_rk4(state, dl=travel - state.travel, marker=Significance.MUZZLE)
        )

        return self.mark_max_pressure(states, acc=acc, logging_preamble=logging_preamble)

    def mark_max_pressure(
        self, states: StateList, *, acc: float = DEFAULT_ACC, logging_preamble: str = ""
    ) -> StateList:
        """
        Finds the maximum pressure point and insert it into a list of
        `ballistics.state.State`, passed in as argument.

        Notes
        -----
        Implementation wise, conducts a gold-section search using `ballistics.num.gss_max`
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
                if s_i.time <= time < s_j.time:
                    p_t = self.propagate_rk4(s_i, dt=time - s_i.time).average_pressure
                elif s_j.time <= time < s_k.time:
                    p_t = self.propagate_rk4(s_j, dt=time - s_j.time).average_pressure
                return p_t

            time_pmax = (
                sum(
                    gss_max(
                        f=time_pressure,
                        x_0=s_i.time,
                        x_1=s_k.time,
                        tol=acc * total_time,
                    )
                )
                * 0.5
            )
            s_pmax = self.propagate_rk4(
                s_j, dt=time_pmax - s_j.time, marker=Significance.PEAK_PRESSURE
            )

            insort(states, s_pmax)

            logger.debug(
                logging_preamble
                + f"GUN -> PMAX {s_pmax.average_pressure * 1e-6:.3f} MPa"
                + f" AT {s_pmax.time * 1e3:.3f} ms "
            )

        return states
